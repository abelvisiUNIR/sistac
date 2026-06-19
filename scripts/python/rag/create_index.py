"""
rag/create_index.py — Crear el índice de Azure AI Search para SISTAC

Crea el índice vectorial `sistac-cvs` con el esquema correcto para:
  - Búsqueda vectorial (embeddings 768 dimensiones — multilingual-mpnet)
  - Búsqueda híbrida (keyword + vector)
  - Azure Semantic Ranker (configuración semántica)
  - Filtrado por cv_id y jd_id (evitar contaminación cruzada entre pares)

Uso:
    py -3 scripts/python/rag/create_index.py
    py -3 scripts/python/rag/create_index.py --delete  # eliminar y recrear

Requiere en .env:
    AZURE_SEARCH_ENDPOINT=https://tu-servicio.search.windows.net
    AZURE_SEARCH_KEY=tu-api-key
    AZURE_SEARCH_INDEX=sistac-cvs   (opcional, default: sistac-cvs)
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import requests

# INV-16: rutas via PROJECT_ROOT
_SCRIPTS_DIR = Path(__file__).parent.parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))



from config import (
    AZURE_SEARCH_ENDPOINT,
    AZURE_SEARCH_KEY,
    AZURE_SEARCH_INDEX,
    check_azure_config,
    VECTORSTORE_PROVIDER,
    check_vectorstore_config,
)
# Dimensiones del modelo de embeddings
# paraphrase-multilingual-mpnet-base-v2 → 768
# text-embedding-3-small (OpenAI) → 1536
EMBEDDING_DIMENSIONS = 768


def _headers() -> dict:
    return {
        "Content-Type": "application/json",
        "api-key": AZURE_SEARCH_KEY,
    }


def index_exists() -> bool:
    """Verifica si el índice ya existe en Azure AI Search."""
    url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX}?api-version=2024-07-01"
    response = requests.get(url, headers=_headers())
    return response.status_code == 200


def delete_index() -> None:
    """Elimina el índice si existe (para recrearlo limpio)."""
    url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX}?api-version=2024-07-01"
    response = requests.delete(url, headers=_headers())
    if response.status_code == 204:
        print(f"  Índice '{AZURE_SEARCH_INDEX}' eliminado.")
    elif response.status_code == 404:
        print(f"  Índice '{AZURE_SEARCH_INDEX}' no existía — nada que eliminar.")
    else:
        response.raise_for_status()


def create_index() -> None:
    """
    Crea el índice sistac-cvs con:
      - Campos de texto filtrable (cv_id, jd_id, chunk_text, etc.)
      - Campo vectorial 'embedding' (768 dims, cosine similarity)
      - Semantic configuration 'default' para Azure Semantic Ranker
    """
    url = f"{AZURE_SEARCH_ENDPOINT}/indexes?api-version=2024-07-01"

    schema = {
        "name": AZURE_SEARCH_INDEX,
        "fields": [
            # ── Identificadores ──────────────────────────────────────────────
            {
                "name": "id",
                "type": "Edm.String",
                "key": True,
                "searchable": False,
                "filterable": True,
                "retrievable": True,
            },
            {
                "name": "cv_id",
                "type": "Edm.String",
                "searchable": False,
                "filterable": True,
                "retrievable": True,
            },
            {
                "name": "jd_id",
                "type": "Edm.String",
                "searchable": False,
                "filterable": True,
                "retrievable": True,
            },
            # ── Contenido ────────────────────────────────────────────────────
            {
                "name": "chunk_text",
                "type": "Edm.String",
                "searchable": True,    # keyword search
                "filterable": False,
                "retrievable": True,
                "analyzer": "es.lucene",  # analizador en español
            },
            {
                "name": "cv_text",
                "type": "Edm.String",
                "searchable": False,
                "filterable": False,
                "retrievable": True,
            },
            {
                "name": "jd_text",
                "type": "Edm.String",
                "searchable": False,
                "filterable": False,
                "retrievable": True,
            },
            # ── Metadata ─────────────────────────────────────────────────────
            {
                "name": "anonymized",
                "type": "Edm.Boolean",
                "searchable": False,
                "filterable": True,
                "retrievable": True,
            },
            {
                "name": "chunk_index",
                "type": "Edm.Int32",
                "searchable": False,
                "filterable": False,
                "retrievable": True,
            },
            # ── Vector field ──────────────────────────────────────────────────
            {
                "name": "embedding",
                "type": "Collection(Edm.Single)",
                "searchable": True,
                "retrievable": False,   # no retornar el vector crudo (ahorra bandwidth)
                "dimensions": EMBEDDING_DIMENSIONS,
                "vectorSearchProfile": "sistac-vector-profile",
            },
        ],
        # ── Configuración de búsqueda vectorial ───────────────────────────────
        "vectorSearch": {
            "algorithms": [
                {
                    "name": "sistac-hnsw",
                    "kind": "hnsw",
                    "hnswParameters": {
                        "m": 4,
                        "efConstruction": 400,
                        "efSearch": 500,
                        "metric": "cosine",
                    },
                }
            ],
            "profiles": [
                {
                    "name": "sistac-vector-profile",
                    "algorithm": "sistac-hnsw",
                }
            ],
        },
        # ── Semantic Ranker ───────────────────────────────────────────────────
        # Nombres correctos para api-version 2024-07-01:
        #   prioritizedContentFields (no contentFields)
        #   prioritizedKeywordsFields (no keywordsFields)
        # Nota: Semantic Ranker requiere tier Basic+.
        # En tier Free esta configuración se acepta pero el ranker no se activa.
        "semantic": {
            "defaultConfiguration": "default",
            "configurations": [
                {
                    "name": "default",
                    "prioritizedFields": {
                        "prioritizedContentFields": [
                            {"fieldName": "chunk_text"}
                        ],
                        "prioritizedKeywordsFields": [
                            {"fieldName": "cv_id"},
                            {"fieldName": "jd_id"},
                        ],
                    },
                }
            ],
        },
    }

    response = requests.post(url, headers=_headers(), json=schema)
    if response.status_code == 201:
        print(f"  Índice '{AZURE_SEARCH_INDEX}' creado correctamente.")
        print(f"  Campos: {len(schema['fields'])} | Dimensiones: {EMBEDDING_DIMENSIONS}")
        print(f"  Algoritmo: HNSW (cosine similarity)")
    else:
        print(f"  ERROR {response.status_code}: {response.text}")
        response.raise_for_status()


def verify_index() -> None:
    """Verifica el índice creado y muestra su configuración."""
    url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX}?api-version=2024-07-01"
    response = requests.get(url, headers=_headers())
    response.raise_for_status()

    data = response.json()
    print(f"\n  Índice verificado: {data['name']}")
    print(f"  Campos: {[f['name'] for f in data['fields']]}")

    # Contar documentos indexados
    count_url = (
        f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX}"
        f"/docs/$count?api-version=2024-07-01"
    )
    count_response = requests.get(count_url, headers=_headers())
    if count_response.status_code == 200:
        print(f"  Documentos indexados: {count_response.text}")


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Crear índice Azure AI Search para SISTAC"
    )
    parser.add_argument(
        "--delete",
        action="store_true",
        help="Eliminar el índice existente antes de crear (útil para reset)",
    )
    parser.add_argument(
        "--verify-only",
        action="store_true",
        help="Solo verificar el índice existente sin crear",
    )
    args = parser.parse_args()

    if VECTORSTORE_PROVIDER == "google":
        print("=== SISTAC — Google Vertex AI Search: Configuración del índice ===\n")
        from config import check_gcp_config, GCP_PROJECT_ID, GCP_SEARCH_APP_ID, GCP_DATA_STORE_ID, GCP_LOCATION
        try:
            check_gcp_config()
            print(f"  GCP Project ID  : {GCP_PROJECT_ID}")
            print(f"  Search App ID   : {GCP_SEARCH_APP_ID}")
            print(f"  Data Store ID   : {GCP_DATA_STORE_ID}")
            print("\n[INFO] En Google Cloud Vertex AI Search, el índice y esquema se crean")
            print("y configuran a través de la consola de GCP (Vertex AI Agent Builder).")
            print("Asegurate de haber creado el Data Store de tipo 'Unstructured Documents' y")
            print("conectarlo al bucket de Cloud Storage correspondiente.")
            print("\nVerificando conexión con el SDK de Google...")
            try:
                from google.cloud import discoveryengine_v1beta as discoveryengine
                client = discoveryengine.DocumentServiceClient()
                parent = client.branch_path(
                    project=GCP_PROJECT_ID,
                    location=GCP_LOCATION,
                    data_store=GCP_DATA_STORE_ID,
                    branch="default_branch",
                )
                # Intento simple de listar documentos para validar credenciales
                list(client.list_documents(parent=parent, page_size=1))
                print("  [SUCCESS] Conexión establecida con éxito y credenciales validadas.")
            except Exception as conn_err:
                print(f"  [WARN] No se pudo conectar o el Data Store está vacío: {conn_err}")
                print("  Esto es normal si el Data Store es nuevo y aún no tiene documentos.")
            sys.exit(0)
        except EnvironmentError as e:
            print(f"\n[ERROR] {e}")
            sys.exit(1)

    print("=== SISTAC — Azure AI Search: Configuración del índice ===\n")

    # Verificar credenciales Azure
    try:
        check_azure_config()
        print(f"  Endpoint : {AZURE_SEARCH_ENDPOINT}")
        print(f"  Índice   : {AZURE_SEARCH_INDEX}")
        print(f"  API Key  : {'*' * 8}{AZURE_SEARCH_KEY[-4:] if AZURE_SEARCH_KEY else 'FALTA'}")
    except EnvironmentError as e:
        print(f"\n[ERROR] {e}")
        print("\nSolución:")
        print("  1. Ir a portal.azure.com → Azure AI Search → tu servicio")
        print("  2. Keys → Primary admin key")
        print("  3. Overview → URL")
        print("  4. Pegar en .env:\n")
        print("     AZURE_SEARCH_ENDPOINT=https://tu-servicio.search.windows.net")
        print("     AZURE_SEARCH_KEY=tu-api-key")
        print("     AZURE_SEARCH_INDEX=sistac-cvs")
        sys.exit(1)

    if args.verify_only:
        verify_index()
        sys.exit(0)

    # Flujo normal
    if args.delete:
        print("\nEliminando índice existente...")
        delete_index()
    elif index_exists():
        print(f"\n  El índice '{AZURE_SEARCH_INDEX}' ya existe.")
        print("  Usar --delete para eliminarlo y recrearlo desde cero.")
        verify_index()
        sys.exit(0)

    print("\nCreando índice...")
    create_index()

    print("\nVerificando...")
    verify_index()

    print("\n=== Listo ===")
    print("Próximo paso: indexar el corpus con:")
    print("  py -3 scripts/python/rag/index_corpus.py")
