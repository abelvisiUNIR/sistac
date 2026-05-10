"""
config.py — Configuración de rutas del proyecto SISTAC

Todas las rutas son relativas al directorio raíz del proyecto (clo-author/).
No usar rutas absolutas en ningún script (INV-16).
"""

from pathlib import Path

# Raíz del proyecto (tres niveles arriba de scripts/python/)
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Datos
DATA_RAW = PROJECT_ROOT / "data" / "raw"
DATA_CLEAN = PROJECT_ROOT / "data" / "cleaned"

# Subdirectorios de datos crudos
CVS_RAW = DATA_RAW / "cvs"
JOB_DESCRIPTIONS = DATA_RAW / "job_descriptions"
GOLD_STANDARD_DIR = DATA_RAW / "gold_standard"

# Subdirectorios de datos procesados
CVS_PROCESSED = DATA_CLEAN / "cvs_processed"
EMBEDDINGS_DIR = DATA_CLEAN / "embeddings"
EVAL_SETS = DATA_CLEAN / "evaluation_sets"

# Outputs del paper
FIGURES_DIR = PROJECT_ROOT / "paper" / "figures"
TABLES_DIR = PROJECT_ROOT / "paper" / "tables"

# Documentos fuente (para migración de .docx)
SUPPORTING_DOCS = PROJECT_ROOT / "master_supporting_docs"
EXPLORATIONS = PROJECT_ROOT / "explorations"

# Bibliografía
BIB_FILE = PROJECT_ROOT / "Bibliography_base.bib"

# Scripts
SCRIPTS_DIR = PROJECT_ROOT / "scripts" / "python"


def ensure_dirs():
    """Crear todos los directorios necesarios si no existen."""
    for d in [
        DATA_RAW, DATA_CLEAN,
        CVS_RAW, JOB_DESCRIPTIONS, GOLD_STANDARD_DIR,
        CVS_PROCESSED, EMBEDDINGS_DIR, EVAL_SETS,
        FIGURES_DIR, TABLES_DIR,
        EXPLORATIONS / "raw",
    ]:
        d.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    ensure_dirs()
    print("Directorios del proyecto verificados:")
    for name, path in [
        ("PROJECT_ROOT", PROJECT_ROOT),
        ("DATA_RAW", DATA_RAW),
        ("DATA_CLEAN", DATA_CLEAN),
        ("FIGURES_DIR", FIGURES_DIR),
        ("TABLES_DIR", TABLES_DIR),
    ]:
        status = "OK" if path.exists() else "CREADO"
        print(f"  {name}: {path} [{status}]")
