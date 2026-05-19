"""
rag/pipeline.py — Pipeline RAG unificado SISTAC (C1 / C2 / C3)

Refactoriza la lógica del piloto de David (index_pilot_corpus.py +
evaluate_pilot_c2.py) en una clase reutilizable que soporta las tres
configuraciones experimentales del diseño factorial:

  C1 — LLM puro: CV texto → scorer → decision
  C2 — LLM + RAG: CV → Azure Search → scorer con contexto → decision
  C3 — LLM + RAG + PII: CV → anonimizador → Azure Search → scorer → decision

Stack:
  - Vector store:  Azure AI Search (créditos estudiante UNIR)
  - Embeddings:    text-embedding-3-small (OpenAI) | paraphrase-multilingual-mpnet (local)
  - Chunking:      RecursiveCharacterTextSplitter (LangChain, 512 tokens)
  - Reranking:     Azure Semantic Ranker (nativo, reemplaza cross-encoder)
  - LLM:           llm/provider.py (Anthropic o OpenAI según .env)
  - PII (C3):      pii/anonymizer.py (SistacAnonymizer)

Hipótesis:
  H1 — eficiencia: mide T_cand via get_processing_time()
  H2 — eficacia:   score F1/AUC-ROC via evaluate()
  H3 — equidad:    DIR/SPD comparando C2 vs C3

Invariantes:
  INV-14: random.seed(42) al inicio
  INV-15: todos los imports al comienzo
  INV-16: rutas via config.PROJECT_ROOT
  INV-19: sin sys.path.insert() ni sys.path.append()
"""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path
from typing import Optional

import numpy as np
import requests

# INV-14: semilla global
random.seed(42)
np.random.seed(42)

# INV-16: PYTHONPATH via PROJECT_ROOT
_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from config import (
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_KEY,
    AZURE_SEARCH_INDEX,
    CHUNK_SIZE,
    CHUNK_OVERLAP,
    RETRIEVAL_TOP_K,
    SCORE_THRESHOLD,
)
from llm.provider import get_embedding
from rag.chunking import chunk_text_tokens
from scoring.scorer import score_candidate


# ── Clase principal ───────────────────────────────────────────────────────────

class SistacRAGPipeline:
    """
    Pipeline RAG configurable para las condiciones experimentales C1, C2 y C3.

    Attributes:
        config (str): Configuración experimental — "c1", "c2" o "c3".

    Example:
        pipeline = SistacRAGPipeline(config="c3")
        pipeline.index(cv_texts=["CV de María..."], jd_texts=["Cargo de analista..."])
        result = pipeline.evaluate(cv_id="CV_001", cv_text="...", jd_text="...")
    """

    def __init__(self, config: str = "c2") -> None:
        """
        Inicializa el pipeline con la configuración experimental especificada.

        Args:
            config: "c1" (LLM puro), "c2" (LLM + RAG), "c3" (PII + LLM + RAG).

        Raises:
            ValueError: si config no es "c1", "c2" o "c3".
        """
        valid_configs = {"c1", "c2", "c3"}
        if config not in valid_configs:
            raise ValueError(
                f"Config inválida: '{config}'. Usar: {valid_configs}"
            )

        self.config = config
        self._anonymizer = None  # lazy load — solo para C3

        # Verificar credenciales Azure si el modo las requiere
        if config in {"c2", "c3"}:
            _check_azure_credentials()

    # ── Indexación ────────────────────────────────────────────────────────────

    def index(
        self,
        cv_texts: dict[str, str],
        jd_texts: dict[str, str],
    ) -> None:
        """
        Indexa CVs y JDs en Azure AI Search.

        Para C3, los CVs se anonimizan antes de indexar (el índice no contiene PII).

        Args:
            cv_texts: Diccionario {cv_id: texto_cv}.
            jd_texts: Diccionario {jd_id: texto_jd}.
        """
        if self.config == "c1":
            print("[pipeline] C1 no usa vector store — indexación omitida.")
            return

        documents = []

        for cv_id, cv_text in cv_texts.items():
            # C3: anonimizar antes de indexar
            text_to_index = (
                self._get_anonymizer().anonymize(cv_text)
                if self.config == "c3"
                else cv_text
            )

            for jd_id, jd_text in jd_texts.items():
                combined = f"CV:\n{text_to_index}\n\nDESCRIPCIÓN DEL CARGO:\n{jd_text}"
                chunks = chunk_text_tokens(
                    combined,
                    chunk_size=CHUNK_SIZE,
                    chunk_overlap=CHUNK_OVERLAP,
                )

                for idx, chunk in enumerate(chunks, start=1):
                    chunk_id = f"{cv_id}_{jd_id}_chunk_{idx:03d}"
                    print(f"  [index] Generando embedding: {chunk_id}")
                    embedding = get_embedding(chunk)

                    documents.append({
                        "id":         chunk_id,
                        "cv_id":      cv_id,
                        "jd_id":      jd_id,
                        "cv_text":    cv_text,    # texto original (para referencia)
                        "jd_text":    jd_text,
                        "chunk_text": chunk,
                        "embedding":  embedding,
                        "anonymized": self.config == "c3",
                    })

        if documents:
            _upload_to_azure(documents)
            print(f"[pipeline] Indexados {len(documents)} chunks en Azure Search.")

    # ── Evaluación ────────────────────────────────────────────────────────────

    def evaluate(
        self,
        cv_id: str,
        cv_text: str,
        jd_id: str,
        jd_text: str,
    ) -> dict:
        """
        Evalúa un par (CV, JD) según la configuración experimental.

        Args:
            cv_id:   Identificador del CV.
            cv_text: Texto completo del CV.
            jd_id:   Identificador de la JD.
            jd_text: Texto de la descripción del cargo.

        Returns:
            Diccionario con:
                cv_id, jd_id, config, score, decision, justification,
                chunks_used, anonymized, time_seconds
        """
        t_start = time.perf_counter()

        # C3: anonimizar antes de retrieval y scoring
        text_for_pipeline = (
            self._get_anonymizer().anonymize(cv_text)
            if self.config == "c3"
            else cv_text
        )

        # Retrieval (C2 y C3)
        chunks: list[str] = []
        if self.config in {"c2", "c3"}:
            chunks = _search_chunks(
                cv_id=cv_id,
                jd_id=jd_id,
                query_text=jd_text,
                top_k=RETRIEVAL_TOP_K,
            )

        # Scoring
        result = score_candidate(
            cv_text=text_for_pipeline,
            jd_text=jd_text,
            context_chunks=chunks if chunks else None,
        )

        t_end = time.perf_counter()

        return {
            "cv_id":        cv_id,
            "jd_id":        jd_id,
            "config":       self.config,
            "score":        result["score"],
            "decision":     result["decision"],
            "justification": result["justification"],
            "dimensions":   result["dimensions"],
            "chunks_used":  len(chunks),
            "anonymized":   self.config == "c3",
            "time_seconds": round(t_end - t_start, 3),
        }

    def get_processing_time(
        self,
        cv_id: str,
        cv_text: str,
        jd_id: str,
        jd_text: str,
    ) -> float:
        """
        Mide el tiempo de procesamiento T_cand para un par (CV, JD).

        Wrapper de evaluate() que retorna solo el tiempo. Usado por
        efficiency_metrics.py para el cálculo de H1.

        Returns:
            Tiempo en segundos (float).
        """
        result = self.evaluate(cv_id, cv_text, jd_id, jd_text)
        return result["time_seconds"]

    # ── Helpers privados ──────────────────────────────────────────────────────

    def _get_anonymizer(self):
        """Carga SistacAnonymizer de forma lazy (solo cuando se necesita en C3)."""
        if self._anonymizer is None:
            from pii.anonymizer import SistacAnonymizer
            self._anonymizer = SistacAnonymizer()
        return self._anonymizer


# ── Azure AI Search helpers ───────────────────────────────────────────────────

def _check_azure_credentials() -> None:
    """Verifica que las credenciales de Azure estén configuradas."""
    if not AZURE_SEARCH_ENDPOINT or not AZURE_SEARCH_KEY:
        raise EnvironmentError(
            "Azure AI Search no configurado.\n"
            "Agregá al archivo .env:\n"
            "  AZURE_SEARCH_ENDPOINT=https://tu-servicio.search.windows.net\n"
            "  AZURE_SEARCH_KEY=tu-api-key\n"
            "  AZURE_SEARCH_INDEX=sistac-cvs"
        )


def _azure_headers() -> dict:
    return {
        "Content-Type": "application/json",
        "api-key": AZURE_SEARCH_KEY,
    }


def _upload_to_azure(documents: list[dict]) -> None:
    """Sube documentos al índice de Azure AI Search."""
    url = (
        f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX}"
        f"/docs/index?api-version=2024-07-01"
    )
    payload = {
        "value": [{"@search.action": "upload", **doc} for doc in documents]
    }
    response = requests.post(url, headers=_azure_headers(), json=payload)
    response.raise_for_status()


def _search_chunks(
    cv_id: str,
    jd_id: str,
    query_text: str,
    top_k: int = RETRIEVAL_TOP_K,
) -> list[str]:
    """
    Recupera los top-k chunks más relevantes de Azure AI Search.

    Usa búsqueda vectorial con Semantic Ranker de Azure (reranking nativo).
    Filtra chunks al par (cv_id, jd_id) para evitar contaminación cruzada.

    Args:
        cv_id:       ID del candidato.
        jd_id:       ID de la JD.
        query_text:  Texto de la consulta (JD usada como query).
        top_k:       Número de chunks a recuperar.

    Returns:
        Lista de strings con el contenido de los chunks recuperados.
    """
    embedding = get_embedding(query_text)

    url = (
        f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX}"
        f"/docs/search?api-version=2024-07-01"
    )

    payload = {
        "count": True,
        "select": "id,chunk_text",
        "vectorQueries": [
            {
                "kind":   "vector",
                "vector": embedding,
                "fields": "embedding",
                "k":      top_k * 4,  # over-fetch antes del filtro por par CV-JD
            }
        ],
        # Semantic Ranker de Azure (reemplaza cross-encoder manual)
        "queryType": "semantic",
        "semanticConfiguration": "default",
        "captions": "none",
    }

    response = requests.post(url, headers=_azure_headers(), json=payload)
    response.raise_for_status()

    results = response.json().get("value", [])

    # Filtrar solo chunks del par (cv_id, jd_id)
    pair_prefix = f"{cv_id}_{jd_id}_"
    filtered = [
        doc["chunk_text"]
        for doc in results
        if doc.get("id", "").startswith(pair_prefix)
    ]

    return filtered[:top_k]


# ── Demo / smoke test ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="SISTAC RAG Pipeline — demo")
    parser.add_argument(
        "--config",
        choices=["c1", "c2", "c3"],
        default="c1",
        help="Configuración experimental (default: c1)",
    )
    parser.add_argument(
        "--demo",
        action="store_true",
        help="Ejecutar con datos de ejemplo embebidos",
    )
    args = parser.parse_args()

    cv_demo = """
    Ana Pérez — Desarrolladora de Software
    Licenciatura en Informática, Universidad ORT Uruguay (2019).
    4 años de experiencia en desarrollo backend con Python, Django y FastAPI.
    Habilidades: Python avanzado, REST APIs, PostgreSQL, Docker, Git.
    Capacidad de trabajo en equipo y comunicación efectiva.
    """

    jd_demo = """
    Desarrolladora/Desarrollador Backend Python
    Requisitos: Python 3+ (avanzado), experiencia con frameworks web (Django/FastAPI),
    3+ años de experiencia, conocimiento de bases de datos relacionales.
    Valoramos: Docker, CI/CD, metodologías ágiles.
    """

    print(f"\n=== SISTAC RAG Pipeline — config: {args.config.upper()} ===\n")

    try:
        pipeline = SistacRAGPipeline(config=args.config)
        result = pipeline.evaluate(
            cv_id="CV_DEMO",
            cv_text=cv_demo,
            jd_id="JD_DEMO",
            jd_text=jd_demo,
        )
        print(f"Score:       {result['score']}/100")
        print(f"Decisión:    {result['decision']}")
        print(f"Chunks RAG:  {result['chunks_used']}")
        print(f"Anonimizado: {result['anonymized']}")
        print(f"T_cand:      {result['time_seconds']}s")
        print(f"\nJustificación:\n{result['justification']}")

    except EnvironmentError as e:
        print(f"\n[WARN] {e}")
        print("Para el demo sin Azure, usar --config c1 (LLM puro, sin vector store).")
