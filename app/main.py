"""
app/main.py — SISTAC Web Application (FastAPI)

API REST + frontend HTML para la aplicación de screening de CVs.

Endpoints:
  GET  /                  → UI principal (HTML)
  POST /api/cargo         → Crear/indexar un cargo (JD)
  GET  /api/cargos        → Listar cargos disponibles
  POST /api/evaluar       → Evaluar un CV contra un cargo
  GET  /api/resultados    → Últimos resultados de evaluación
  GET  /health            → Health check (para Azure DevOps)

Uso local:
  pip install fastapi uvicorn python-multipart
  uvicorn app.main:app --reload --port 8000

Uso con Docker:
  docker build -t sistac-app .
  docker run -p 8000:8000 --env-file .env sistac-app
"""

from __future__ import annotations

import json
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

from config import ensure_dirs, SCORE_THRESHOLD

# ── App ───────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="SISTAC — Sistema Inteligente de Selección de Talento",
    description="Pre-screening de CVs con LLM + RAG. TFE UNIR 2026.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage en memoria (en producción: base de datos)
_cargos: dict[str, dict] = {}       # {cargo_id: {id, nombre, descripcion, fecha}}
_resultados: list[dict] = []        # historial de evaluaciones

# ── Health ────────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "version": "1.0.0", "cargos": len(_cargos)}


# ── API: Cargos (Job Descriptions) ───────────────────────────────────────────

@app.post("/api/cargo")
async def crear_cargo(
    nombre: str = Form(..., description="Nombre del cargo, ej: Analista de Datos"),
    descripcion: str = Form(..., description="Descripción completa del cargo (JD)"),
    config: str = Form("c2", description="Configuración RAG: c1, c2 o c3"),
):
    """
    Crea un nuevo cargo y lo indexa en Azure AI Search.
    El cargo queda disponible para evaluar candidatos.
    """
    cargo_id = f"JD_{str(uuid.uuid4())[:8].upper()}"

    _cargos[cargo_id] = {
        "id":          cargo_id,
        "nombre":      nombre,
        "descripcion": descripcion,
        "config":      config,
        "fecha":       datetime.now().isoformat(),
        "candidatos":  0,
    }

    # Indexar en Azure Search (async, no bloqueante para el usuario)
    try:
        from rag.pipeline import SistacRAGPipeline
        pipeline = SistacRAGPipeline(config=config)
        if config in {"c2", "c3"}:
            pipeline.index(
                cv_texts={},                          # sin CVs nuevos aún
                jd_texts={cargo_id: descripcion},     # indexar solo la JD
            )
        indexado = True
    except Exception as exc:
        # Continuar sin Azure Search — C1 (LLM puro) funciona igual
        indexado = False
        print(f"[WARN] No se pudo indexar en Azure Search: {exc}")

    return {
        "cargo_id": cargo_id,
        "nombre":   nombre,
        "indexado": indexado,
        "mensaje":  f"Cargo '{nombre}' creado. ID: {cargo_id}",
    }


@app.get("/api/cargos")
def listar_cargos():
    """Lista todos los cargos disponibles."""
    return {"cargos": list(_cargos.values())}


@app.delete("/api/cargo/{cargo_id}")
def eliminar_cargo(cargo_id: str):
    """Elimina un cargo del sistema."""
    if cargo_id not in _cargos:
        raise HTTPException(status_code=404, detail=f"Cargo '{cargo_id}' no encontrado.")
    del _cargos[cargo_id]
    return {"mensaje": f"Cargo '{cargo_id}' eliminado."}


# ── API: Evaluación de CVs ────────────────────────────────────────────────────

@app.post("/api/evaluar")
async def evaluar_cv(
    cargo_id: str = Form(..., description="ID del cargo a evaluar"),
    cv_texto: Optional[str] = Form(None, description="Texto del CV (pegar directamente)"),
    cv_archivo: Optional[UploadFile] = File(None, description="Archivo .txt con el CV"),
    config: str = Form("c2", description="Configuración: c1 (LLM puro), c2 (RAG), c3 (RAG+PII)"),
    candidato_nombre: str = Form("Candidato", description="Nombre del candidato (opcional)"),
):
    """
    Evalúa un CV contra un cargo usando el pipeline SISTAC.

    Acepta el CV como texto pegado directamente o como archivo .txt.
    Retorna score (0-100), decisión APTO/NO_APTO y justificación del LLM.
    """
    # Validar cargo
    if cargo_id not in _cargos:
        raise HTTPException(status_code=404, detail=f"Cargo '{cargo_id}' no encontrado.")

    # Obtener texto del CV
    if cv_archivo:
        content = await cv_archivo.read()
        try:
            cv_text = content.decode("utf-8")
        except UnicodeDecodeError:
            cv_text = content.decode("latin-1")
    elif cv_texto:
        cv_text = cv_texto
    else:
        raise HTTPException(
            status_code=400,
            detail="Debe proveer el CV como texto o como archivo .txt.",
        )

    if len(cv_text.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="El CV parece muy corto (< 50 caracteres). Verificá el contenido.",
        )

    cargo = _cargos[cargo_id]
    cv_id = f"CV_{str(uuid.uuid4())[:8].upper()}"

    # Evaluar con el pipeline
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
        raise HTTPException(
            status_code=500,
            detail=f"Error al evaluar el CV: {str(exc)}",
        )

    # Guardar en historial
    entrada = {
        "id":                str(uuid.uuid4())[:8],
        "cv_id":             cv_id,
        "candidato_nombre":  candidato_nombre,
        "cargo_id":          cargo_id,
        "cargo_nombre":      cargo["nombre"],
        "score":             resultado["score"],
        "decision":          resultado["decision"],
        "justificacion":     resultado["justification"],
        "dimensiones":       resultado.get("dimensions", {}),
        "chunks_usados":     resultado.get("chunks_used", 0),
        "anonimizado":       resultado.get("anonymized", False),
        "tiempo_segundos":   resultado.get("time_seconds", 0),
        "config":            config,
        "fecha":             datetime.now().isoformat(),
    }
    _resultados.insert(0, entrada)   # más reciente primero
    _cargos[cargo_id]["candidatos"] += 1

    return entrada


@app.get("/api/resultados")
def listar_resultados(
    cargo_id: Optional[str] = None,
    limite: int = 50,
):
    """
    Retorna el historial de evaluaciones.
    Filtrar por cargo_id para ver solo candidatos de un cargo específico.
    """
    resultados = _resultados
    if cargo_id:
        resultados = [r for r in resultados if r["cargo_id"] == cargo_id]
    return {"resultados": resultados[:limite], "total": len(resultados)}


# ── Frontend HTML ─────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def frontend():
    """Sirve el frontend HTML de la aplicación."""
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return HTMLResponse("<h1>SISTAC — Frontend no encontrado</h1><p>Verificar app/static/index.html</p>")
