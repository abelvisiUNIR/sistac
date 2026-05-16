"""
app/main.py — SISTAC Web Application (FastAPI)

Flujo:
  EMPRESA  → sube DOCX/PDF del cargo → POST /api/cargo → indexado en Azure Search
  CANDIDATO → sube CV (PDF/DOCX/imagen) → POST /api/evaluar → score + justificación

Uso local:
  py -3 -m uvicorn app.main:app --reload --port 8000
"""

from __future__ import annotations

import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# INV-16: rutas via PROJECT_ROOT
_PROJECT_ROOT = Path(__file__).parent.parent
_SCRIPTS_DIR  = _PROJECT_ROOT / "scripts" / "python"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from config import SCORE_THRESHOLD
from utils.doc_extractor import extract_text, SUPPORTED_EXTENSIONS

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="SISTAC",
    description="Sistema Inteligente de Selección de Talento y Análisis Curricular",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage en memoria (sesión)
_cargos: dict[str, dict] = {}
_resultados: list[dict] = []


# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "cargos": len(_cargos),
        "evaluaciones": len(_resultados),
        "formatos_soportados": sorted(SUPPORTED_EXTENSIONS),
    }


# ── API: Cargos ───────────────────────────────────────────────────────────────

@app.post("/api/cargo")
async def crear_cargo(
    nombre: str = Form(...),
    archivo: UploadFile = File(..., description="PDF o DOCX con la descripción del cargo"),
    config: str = Form("c2"),
):
    """
    Crea un cargo a partir de un archivo PDF o DOCX.
    Extrae el texto automáticamente y lo indexa en Azure AI Search.
    """
    ext = Path(archivo.filename).suffix.lower()
    if ext not in {".pdf", ".docx", ".txt"}:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{ext}' no soportado para cargos. Usá PDF, DOCX o TXT.",
        )

    # Extraer texto del documento
    data = await archivo.read()
    try:
        descripcion = extract_text(data, archivo.filename)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"No se pudo extraer texto: {exc}")

    if len(descripcion.strip()) < 30:
        raise HTTPException(
            status_code=422,
            detail="El documento parece vacío o no contiene texto legible.",
        )

    cargo_id = f"JD_{str(uuid.uuid4())[:8].upper()}"
    _cargos[cargo_id] = {
        "id":          cargo_id,
        "nombre":      nombre,
        "descripcion": descripcion,
        "archivo":     archivo.filename,
        "config":      config,
        "fecha":       datetime.now().isoformat(),
        "candidatos":  0,
    }

    # Indexar en Azure Search (C2/C3)
    indexado = False
    try:
        from rag.pipeline import SistacRAGPipeline
        pipeline = SistacRAGPipeline(config=config)
        if config in {"c2", "c3"}:
            pipeline.index(cv_texts={}, jd_texts={cargo_id: descripcion})
            indexado = True
    except Exception as exc:
        print(f"[WARN] Azure Search no disponible: {exc}")

    return {
        "cargo_id":  cargo_id,
        "nombre":    nombre,
        "archivo":   archivo.filename,
        "chars":     len(descripcion),
        "indexado":  indexado,
        "preview":   descripcion[:300] + "..." if len(descripcion) > 300 else descripcion,
    }


@app.get("/api/cargos")
def listar_cargos():
    return {"cargos": list(_cargos.values())}


@app.delete("/api/cargo/{cargo_id}")
def eliminar_cargo(cargo_id: str):
    if cargo_id not in _cargos:
        raise HTTPException(status_code=404, detail="Cargo no encontrado.")
    del _cargos[cargo_id]
    return {"ok": True}


# ── API: Evaluación ───────────────────────────────────────────────────────────

@app.post("/api/evaluar")
async def evaluar_cv(
    cargo_id: str = Form(...),
    archivo_cv: UploadFile = File(..., description="CV en PDF, DOCX o imagen (JPG/PNG)"),
    candidato_nombre: str = Form("Candidato"),
    config: str = Form("c2"),
):
    """
    Evalúa un CV subido como archivo (PDF, DOCX, JPG, PNG) contra un cargo.
    Extrae el texto automáticamente (usa Claude Vision para imágenes).
    """
    if cargo_id not in _cargos:
        raise HTTPException(status_code=404, detail="Cargo no encontrado.")

    ext = Path(archivo_cv.filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Formato '{ext}' no soportado. Usá: {', '.join(sorted(SUPPORTED_EXTENSIONS))}",
        )

    # Extraer texto del CV
    data = await archivo_cv.read()
    try:
        cv_text = extract_text(data, archivo_cv.filename)
    except Exception as exc:
        raise HTTPException(status_code=422, detail=f"No se pudo leer el CV: {exc}")

    if len(cv_text.strip()) < 50:
        raise HTTPException(
            status_code=422,
            detail="El CV parece vacío o ilegible. Probá con otro formato.",
        )

    cargo = _cargos[cargo_id]
    cv_id = f"CV_{str(uuid.uuid4())[:8].upper()}"

    # Evaluar con pipeline SISTAC
    try:
        from rag.pipeline import SistacRAGPipeline
        pipeline = SistacRAGPipeline(config=config)
        resultado = pipeline.evaluate(
            cv_id=cv_id,
            cv_text=cv_text,
            jd_id=cargo_id,
            jd_text=cargo["descripcion"],
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error en pipeline: {exc}")

    entrada = {
        "id":               str(uuid.uuid4())[:8],
        "cv_id":            cv_id,
        "candidato_nombre": candidato_nombre,
        "archivo_cv":       archivo_cv.filename,
        "cargo_id":         cargo_id,
        "cargo_nombre":     cargo["nombre"],
        "score":            resultado["score"],
        "decision":         resultado["decision"],
        "justificacion":    resultado["justification"],
        "dimensiones":      resultado.get("dimensions", {}),
        "chunks_usados":    resultado.get("chunks_used", 0),
        "anonimizado":      resultado.get("anonymized", False),
        "tiempo_segundos":  resultado.get("time_seconds", 0),
        "config":           config,
        "fecha":            datetime.now().isoformat(),
    }
    _resultados.insert(0, entrada)
    _cargos[cargo_id]["candidatos"] += 1

    return entrada


@app.get("/api/resultados")
def listar_resultados(cargo_id: Optional[str] = None, limite: int = 100):
    resultados = _resultados
    if cargo_id:
        resultados = [r for r in resultados if r["cargo_id"] == cargo_id]
    return {"resultados": resultados[:limite], "total": len(resultados)}


# ── Frontend ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def frontend():
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return HTMLResponse("<h1>SISTAC</h1><p>Frontend no encontrado en app/static/index.html</p>")
