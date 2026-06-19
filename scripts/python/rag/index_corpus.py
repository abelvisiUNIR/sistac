"""
rag/index_corpus.py — Indexar el corpus sintético en Azure AI Search

Lee los 300 CVs y 5 JDs de data/raw/, genera embeddings y los sube
al índice 'sistac-cvs' en Azure AI Search.

El script es idempotente: vuelve a subir (upsert) si el chunk ya existe.

Tiempo estimado: ~15-20 min para 300 CVs × 5 JDs con embeddings locales.
Con embeddings OpenAI: ~5 min (sujeto a rate limits).

Uso:
    py -3 scripts/python/rag/index_corpus.py
    py -3 scripts/python/rag/index_corpus.py --dry-run   # ver stats sin subir
    py -3 scripts/python/rag/index_corpus.py --config c3  # indexa con PII anonimizada

Requiere:
    - data/raw/cvs/CV_001.txt ... CV_300.txt  (generado por synthetic_corpus_generator.py)
    - data/raw/job_descriptions/JD_001.txt ... JD_005.txt
    - .env con AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, AZURE_SEARCH_INDEX
"""

from __future__ import annotations

import argparse
import json
import random
import sys
import time
from pathlib import Path

import numpy as np

# INV-14: semilla global
random.seed(42)
np.random.seed(42)

# INV-16: rutas via PROJECT_ROOT
_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from config import (
    CVS_RAW,
    JOB_DESCRIPTIONS,
    AZURE_SEARCH_INDEX,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    GOLD_STANDARD_DIR,
    check_azure_config,
    VECTORSTORE_PROVIDER,
    check_vectorstore_config,
)
from llm.provider import get_embedding
from rag.chunking import chunk_text_tokens
from rag.pipeline import _upload_to_azure, _azure_headers, _upload_to_gcp
import requests


# ── Helpers ───────────────────────────────────────────────────────────────────

def load_corpus() -> tuple[dict[str, str], dict[str, str]]:
    """
    Carga todos los CVs y JDs desde data/raw/.

    Returns:
        cv_texts:  {cv_id: texto} — ej. {"CV_001": "Florencia Rodríguez..."}
        jd_texts:  {jd_id: texto} — ej. {"JD_001": "CARGO: Analista de Datos..."}

    Raises:
        FileNotFoundError: si data/raw/cvs/ o data/raw/job_descriptions/ no existen.
    """
    if not CVS_RAW.exists():
        raise FileNotFoundError(
            f"No se encontró: {CVS_RAW}\n"
            "Primero generá el corpus con:\n"
            "  py -3 scripts/python/data/synthetic_corpus_generator.py"
        )

    cv_texts = {}
    for cv_file in sorted(CVS_RAW.glob("CV_*.txt")):
        cv_id = cv_file.stem  # "CV_001"
        cv_texts[cv_id] = cv_file.read_text(encoding="utf-8")

    jd_texts = {}
    for jd_file in sorted(JOB_DESCRIPTIONS.glob("JD_*.txt")):
        jd_id = jd_file.stem  # "JD_001"
        jd_texts[jd_id] = jd_file.read_text(encoding="utf-8")

    return cv_texts, jd_texts


def index_corpus(
    cv_texts: dict[str, str],
    jd_texts: dict[str, str],
    config: str = "c2",
    dry_run: bool = False,
    batch_size: int = 50,
) -> None:
    """
    Indexa los CVs y JDs en Azure AI Search con soporte para continuar (resumen).

    Args:
        cv_texts:   {cv_id: texto_cv}
        jd_texts:   {jd_id: texto_jd}
        config:     "c2" (texto original) | "c3" (PII anonimizada)
        dry_run:    Si True, calcula stats sin subir nada
        batch_size: Chunks por batch de upload (Azure acepta hasta 1000 docs/batch)
    """
    # C3: cargar anonimizador
    anonymizer = None
    if config == "c3":
        from pii.anonymizer import SistacAnonymizer
        anonymizer = SistacAnonymizer()
        print("  Modo C3: PII será anonimizada antes de indexar")

    total_chunks = 0
    batch_docs = []
    cv_count = 0

    n_cvs = len(cv_texts)
    n_jds = len(jd_texts)
    print(f"  {n_cvs} CVs × {n_jds} JDs = {n_cvs * n_jds} pares a indexar")
    print(f"  Chunk size: {CHUNK_SIZE} tokens | Overlap: {CHUNK_OVERLAP}")
    print()

    # Cargar progreso para permitir continuar si se corta la ejecución
    progress_file = GOLD_STANDARD_DIR / "indexed_cvs_progress.json"
    progress = {"c2": [], "c3": []}
    if progress_file.exists():
        try:
            with open(progress_file, "r", encoding="utf-8") as f:
                progress = json.load(f)
                if "c2" not in progress: progress["c2"] = []
                if "c3" not in progress: progress["c3"] = []
        except Exception as e:
            print(f"  [WARN] Error cargando progreso de indexación: {e}")

    # Cargar parejas de ground truth (si existen) para indexar únicamente las necesarias
    valid_pairs = set()
    gt_path = GOLD_STANDARD_DIR / "ground_truth.csv"
    if gt_path.exists():
        try:
            import csv
            with open(gt_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cid = row.get("cv_id")
                    jid = row.get("jd_id")
                    if cid and jid:
                        valid_pairs.add((cid, jid))
            print(f"  [INFO] Se encontraron {len(valid_pairs)} parejas en ground_truth.csv. Solo se indexarán estas parejas para el experimento.")
        except Exception as e:
            print(f"  [WARN] Error al cargar ground_truth.csv para filtrar: {e}")

    indexed_cvs = set(progress.get(config, []))

    for cv_id, cv_text in cv_texts.items():
        cv_count += 1
        progress_status = f"{cv_count}/{n_cvs}"

        if cv_id in indexed_cvs and not dry_run:
            print(f"  [{progress_status}] {cv_id} ya indexado en {config.upper()} previamente — omitiendo.")
            continue

        # C3: anonimizar
        text_to_index = (
            anonymizer.anonymize(cv_text) if anonymizer else cv_text
        )

        for jd_id, jd_text in jd_texts.items():
            if valid_pairs and (cv_id, jd_id) not in valid_pairs:
                continue
            combined = f"CV:\n{text_to_index}\n\nDESCRIPCIÓN DEL CARGO:\n{jd_text}"
            chunks = chunk_text_tokens(
                combined,
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
            )

            for idx, chunk in enumerate(chunks, start=1):
                chunk_id = f"{cv_id}_{jd_id}_chunk_{idx:03d}"

                if not dry_run:
                    try:
                        embedding = get_embedding(chunk)
                    except Exception as err:
                        print(f"  [WARN] Falló la generación del embedding para {chunk_id}: {err}. Omitiendo este chunk.")
                        continue
                else:
                    embedding = [0.0] * 768  # placeholder en dry-run

                batch_docs.append({
                    "id":          chunk_id,
                    "cv_id":       cv_id,
                    "jd_id":       jd_id,
                    "cv_text":     cv_text[:500],  # truncar para metadata (no es el chunk)
                    "jd_text":     jd_text[:500],
                    "chunk_text":  chunk,
                    "embedding":   embedding,
                    "anonymized":  config == "c3",
                    "chunk_index": idx,
                })
                total_chunks += 1

                # Subir en batches para no saturar la API
                if len(batch_docs) >= batch_size and not dry_run:
                    try:
                        if VECTORSTORE_PROVIDER == "google":
                            _upload_to_gcp(batch_docs)
                        else:
                            _upload_to_azure(batch_docs)
                        print(f"    Subidos {total_chunks} chunks... ({cv_id} procesado)")
                    except Exception as err:
                        print(f"  [ERROR BATCH] Error crítico al subir batch: {err}. Continuando con los demás...")
                    batch_docs = []
                    time.sleep(1.5)  # rate limit suave

        # Subir los chunks restantes del CV actual para asegurar atomicidad
        if batch_docs and not dry_run:
            try:
                if VECTORSTORE_PROVIDER == "google":
                    _upload_to_gcp(batch_docs)
                else:
                    _upload_to_azure(batch_docs)
            except Exception as err:
                print(f"  [ERROR BATCH] Error al subir el batch final para {cv_id}: {err}")
                raise err
            batch_docs = []

        if not dry_run:
            progress[config].append(cv_id)
            try:
                with open(progress_file, "w", encoding="utf-8") as f:
                    json.dump(progress, f, ensure_ascii=False, indent=2)
            except Exception as e:
                print(f"  [WARN] No se pudo guardar el archivo de progreso: {e}")

        print(f"  [{progress_status}] {cv_id} completado para {config.upper()} y guardado en progreso.")

    print(f"\n  Total chunks procesados: {total_chunks}")
    if dry_run:
        print("  [DRY RUN] No se subió nada — usar sin --dry-run para indexar")


def verify_index_count() -> None:
    """Verifica cuántos documentos hay en el índice."""
    if VECTORSTORE_PROVIDER == "google":
        try:
            from google.cloud import discoveryengine_v1beta as discoveryengine
            client = discoveryengine.DocumentServiceClient()
            parent = client.branch_path(
                project=GCP_PROJECT_ID,
                location=GCP_LOCATION,
                data_store=GCP_DATA_STORE_ID,
                branch="default_branch",
            )
            docs = list(client.list_documents(parent=parent))
            print(f"\n  Documentos en el índice Google: {len(docs)}")
        except Exception as e:
            print(f"\n  No se pudo verificar el índice Google: {e}")
    else:
        from config import AZURE_SEARCH_ENDPOINT
        url = (
            f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX}"
            f"/docs/$count?api-version=2024-07-01"
        )
        try:
            response = requests.get(url, headers=_azure_headers())
            if response.status_code == 200:
                print(f"\n  Documentos en el índice Azure: {response.text}")
            else:
                print(f"\n  No se pudo verificar el índice Azure: {response.status_code}")
        except Exception as e:
            print(f"\n  Error al verificar el índice Azure: {e}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Indexar corpus SISTAC en Azure AI Search"
    )
    parser.add_argument(
        "--config",
        choices=["c2", "c3"],
        default="c2",
        help="c2: texto original | c3: PII anonimizada (default: c2)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Calcular stats sin subir documentos",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=50,
        help="Chunks por batch de upload (default: 50)",
    )
    args = parser.parse_args()

    print(f"=== SISTAC — Indexación del corpus (config={args.config.upper()}) ===\n")

    # Verificar credenciales del Vector Store
    if not args.dry_run:
        try:
            check_vectorstore_config()
        except EnvironmentError as e:
            print(f"[ERROR] {e}")
            sys.exit(1)

    # Cargar corpus
    print("Cargando corpus...")
    try:
        cv_texts, jd_texts = load_corpus()
        print(f"  CVs cargados: {len(cv_texts)}")
        print(f"  JDs cargadas: {len(jd_texts)}")
    except FileNotFoundError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    # Indexar
    print(f"\nIndexando {'(DRY RUN) ' if args.dry_run else ''}...")
    t_start = time.perf_counter()
    index_corpus(
        cv_texts=cv_texts,
        jd_texts=jd_texts,
        config=args.config,
        dry_run=args.dry_run,
        batch_size=args.batch_size,
    )
    t_total = time.perf_counter() - t_start

    print(f"\n  Tiempo total: {t_total:.1f}s ({t_total/60:.1f} min)")

    # Verificar
    if not args.dry_run:
        verify_index_count()
        print("\nListo. El índice está disponible para el pipeline RAG.")
        print("Próximo paso:")
        print("  py -3 scripts/python/experiments/orquestador_c0_c3.py")
