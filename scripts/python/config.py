"""
config.py — Configuración de rutas y modelos del proyecto SISTAC

Todas las rutas son relativas al directorio raíz del proyecto.
No usar rutas absolutas en ningún script (INV-16).

Variables de entorno requeridas (archivo .env en la raíz del proyecto):
    ANTHROPIC_API_KEY=sk-ant-...        # LLM Mario (Claude)
    OPENAI_API_KEY=sk-...               # LLM David (GPT-4o) + embeddings
    AZURE_SEARCH_ENDPOINT=https://...   # Vector store
    AZURE_SEARCH_KEY=...                # API key Azure AI Search
    AZURE_SEARCH_INDEX=sistac-cvs       # Nombre del índice
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde .env (si existe)
load_dotenv(Path(__file__).parent.parent.parent / ".env")

# ── Raíz del proyecto ────────────────────────────────────────────────────────
# Este archivo está en scripts/python/config.py → tres niveles arriba = raíz
PROJECT_ROOT = Path(__file__).parent.parent.parent

# ── Datos ────────────────────────────────────────────────────────────────────
DATA_RAW   = PROJECT_ROOT / "data" / "raw"
DATA_CLEAN = PROJECT_ROOT / "data" / "cleaned"

CVS_RAW          = DATA_RAW / "cvs"
JOB_DESCRIPTIONS = DATA_RAW / "job_descriptions"
GOLD_STANDARD_DIR = DATA_RAW / "gold_standard"
VECTORSTORE_DIR  = DATA_RAW / "vectorstore"

CVS_PROCESSED = DATA_CLEAN / "cvs_processed"
EMBEDDINGS_DIR = DATA_CLEAN / "embeddings"
EVAL_SETS     = DATA_CLEAN / "evaluation_sets"

# ── Outputs del paper ────────────────────────────────────────────────────────
FIGURES_DIR = PROJECT_ROOT / "paper" / "figures"
TABLES_DIR  = PROJECT_ROOT / "paper" / "tables"

# ── Documentos fuente ────────────────────────────────────────────────────────
SUPPORTING_DOCS = PROJECT_ROOT / "master_supporting_docs"
EXPLORATIONS    = PROJECT_ROOT / "explorations"
BIB_FILE        = PROJECT_ROOT / "Bibliography_base.bib"
SCRIPTS_DIR     = PROJECT_ROOT / "scripts" / "python"

# ── Azure AI Search (vector store oficial del experimento) ───────────────────
AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT", "")
AZURE_SEARCH_KEY      = os.getenv("AZURE_SEARCH_KEY", "")
AZURE_SEARCH_INDEX    = os.getenv("AZURE_SEARCH_INDEX", "sistac-cvs")

# ── Configuración LLM ─────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY    = os.getenv("OPENAI_API_KEY", "")

# Modelos disponibles (seleccionar según fase):
#   Desarrollo / iteración rápida  → claude-haiku-3-5
#   Redacción y análisis           → claude-sonnet-4-5 (recomendado)
#   Experimento final (máx calidad) → claude-opus-4-5
LLM_MODEL_DEV   = "claude-haiku-3-5-20241022"     # dev: rápido y barato
LLM_MODEL_PROD  = "claude-sonnet-4-5-20241022"    # producción: equilibrado
LLM_MODEL_FINAL = "claude-opus-4-5-20240229"      # experimento final: máxima calidad

# Modelo activo (cambiar según la fase del proyecto)
LLM_MODEL = LLM_MODEL_PROD

# Parámetros del LLM
LLM_TEMPERATURE   = 0.0    # Determinista para scoring reproducible
LLM_MAX_TOKENS    = 1024   # Por respuesta (score + justificación)

# ── Configuración RAG ─────────────────────────────────────────────────────────
# Modelo de embeddings (local, sin API externa)
EMBEDDING_MODEL = "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"

# Chunking
CHUNK_SIZE    = 512    # tokens por chunk
CHUNK_OVERLAP = 64     # overlap entre chunks

# Retrieval
RETRIEVAL_TOP_K = 5    # número de chunks recuperados

# ── Configuración del experimento ─────────────────────────────────────────────
RANDOM_SEED    = 42
N_BOOTSTRAP    = 1000   # iteraciones para IC95% AUC-ROC
ALPHA          = 0.05   # nivel de significancia

# Umbrales de hipótesis
H1_REDUCTION_THRESHOLD = 0.50   # reducción >50% en T_cand (H1)
H2_F1_THRESHOLD        = 0.85   # F1 ≥ 0.85 vs Gold Standard (H2)
H2_AUC_THRESHOLD       = 0.90   # AUC-ROC ≥ 0.90 (H2)
H3_DIR_THRESHOLD       = 0.80   # DIR ≥ 0.80 (regla EEOC 4/5) (H3)
GOLD_STANDARD_KAPPA    = 0.70   # κ ≥ 0.70 inter-evaluador (Gold Standard válido)

# Score de corte para decisión apto/no apto
# Calibrado con el piloto C2 (5 CVs vs Gold Standard): score ≥ 70 → APTO
# Todos los experimentos C1/C2/C3 usan este umbral para comparabilidad.
SCORE_THRESHOLD = 70   # candidatos con score ≥ 70 → "apto"

# ── Helpers ───────────────────────────────────────────────────────────────────
def ensure_dirs() -> None:
    """Crear todos los directorios necesarios si no existen."""
    dirs = [
        DATA_RAW, DATA_CLEAN,
        CVS_RAW, JOB_DESCRIPTIONS, GOLD_STANDARD_DIR, VECTORSTORE_DIR,
        CVS_PROCESSED, EMBEDDINGS_DIR, EVAL_SETS,
        FIGURES_DIR, TABLES_DIR,
        EXPLORATIONS / "raw",
    ]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)


def check_api_key() -> bool:
    """Verificar que la API key de Anthropic esté configurada."""
    if not ANTHROPIC_API_KEY:
        raise EnvironmentError(
            "ANTHROPIC_API_KEY no está configurada.\n"
            "Agregá al archivo .env en la raíz del proyecto:\n"
            "  ANTHROPIC_API_KEY=sk-ant-..."
        )
    return True


def check_azure_config() -> bool:
    """Verificar que Azure AI Search esté configurado."""
    missing = []
    if not AZURE_SEARCH_ENDPOINT:
        missing.append("AZURE_SEARCH_ENDPOINT")
    if not AZURE_SEARCH_KEY:
        missing.append("AZURE_SEARCH_KEY")
    if missing:
        raise EnvironmentError(
            f"Variables de Azure no configuradas: {', '.join(missing)}\n"
            "Agregá al archivo .env:\n"
            "  AZURE_SEARCH_ENDPOINT=https://tu-servicio.search.windows.net\n"
            "  AZURE_SEARCH_KEY=tu-api-key\n"
            "  AZURE_SEARCH_INDEX=sistac-cvs"
        )
    return True


if __name__ == "__main__":
    ensure_dirs()
    print("Configuracion SISTAC:")
    print(f"  PROJECT_ROOT    : {PROJECT_ROOT}")
    print(f"  LLM_MODEL       : {LLM_MODEL}")
    print(f"  EMBEDDING       : {EMBEDDING_MODEL}")
    print(f"  ANTHROPIC_KEY   : {'OK' if ANTHROPIC_API_KEY else 'FALTA (.env)'}")
    print(f"  OPENAI_KEY      : {'OK' if OPENAI_API_KEY else 'FALTA (.env)'}")
    print(f"  AZURE_ENDPOINT  : {'OK' if AZURE_SEARCH_ENDPOINT else 'FALTA (.env)'}")
    print(f"  SCORE_THRESHOLD : {SCORE_THRESHOLD}")
    print(f"  RANDOM_SEED     : {RANDOM_SEED}")
