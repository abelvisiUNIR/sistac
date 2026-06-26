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
import random
import csv
from datetime import datetime
from pathlib import Path
from typing import Optional
from pydantic import BaseModel
from bson import ObjectId

from fastapi import FastAPI, File, Form, HTTPException, UploadFile, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

# INV-16: rutas via PROJECT_ROOT
_PROJECT_ROOT = Path(__file__).parent.parent
_SCRIPTS_DIR  = _PROJECT_ROOT / "scripts" / "python"
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from config import SCORE_THRESHOLD, CVS_RAW, GOLD_STANDARD_DIR, USE_EXTERNAL_DATA
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

# ====== MongoDB Client ======
import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI")
db_client = None
db = None
resultados_col = None
cargos_col = None

if MONGO_URI:
    try:
        db_client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=2000)
        # Validar conexión
        db_client.server_info()
        db = db_client["sistac_tfe"]
        resultados_col = db["resultados"]
        cargos_col = db["cargos"]
        print("[INFO] Conectado exitosamente a MongoDB")
    except Exception as e:
        print(f"[WARN] No se pudo conectar a MongoDB: {e}. Usando almacenamiento en memoria.")

@app.on_event("startup")
async def startup_event():
    if cargos_col is not None:
        try:
            from data.seed_mongodb import seed_database
            await run_in_threadpool(seed_database)
            
            db_cargos = list(cargos_col.find({}, {"_id": 0}))
            for c in db_cargos:
                _cargos[c["id"]] = c
            print(f"[INFO] Cargados {len(db_cargos)} cargos desde MongoDB.")
        except Exception as e:
            print(f"[WARN] No se pudieron cargar o sembrar datos en MongoDB: {e}")



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
    cargo_data = {
        "id":          cargo_id,
        "nombre":      nombre,
        "descripcion": descripcion,
        "archivo":     archivo.filename,
        "config":      config,
        "fecha":       datetime.now().isoformat(),
        "candidatos":  0,
    }
    _cargos[cargo_id] = cargo_data
    if cargos_col is not None:
        try:
            cargos_col.update_one({"id": cargo_id}, {"$set": cargo_data}, upsert=True)
        except Exception as e:
            print(f"[WARN] Error guardando cargo en MongoDB: {e}")

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
    if cargos_col is not None:
        try:
            db_cargos = list(cargos_col.find({}, {"_id": 0}))
            for c in db_cargos:
                _cargos[c["id"]] = c
        except Exception as e:
            print(f"[WARN] Error leyendo cargos de MongoDB: {e}")
            
    filtered_cargos = []
    for c in _cargos.values():
        cid = c.get("id", "")
        is_standard = cid in {"JD_001", "JD_002", "JD_003", "JD_004", "JD_005"}
        if USE_EXTERNAL_DATA:
            if not is_standard:
                filtered_cargos.append(c)
        else:
            if is_standard or not cid.startswith("JD_EXT_"):
                filtered_cargos.append(c)
                
    return {"cargos": filtered_cargos}


@app.delete("/api/cargo/{cargo_id}")
def eliminar_cargo(cargo_id: str):
    if cargo_id not in _cargos:
        raise HTTPException(status_code=404, detail="Cargo no encontrado.")
    del _cargos[cargo_id]
    if cargos_col is not None:
        try:
            cargos_col.delete_one({"id": cargo_id})
        except Exception as e:
            print(f"[WARN] Error eliminando cargo de MongoDB: {e}")
    return {"ok": True}


# ── API: Evaluación ───────────────────────────────────────────────────────────

@app.post("/api/evaluar/batch")
async def evaluar_batch(
    cargo_id: str = Form(...),
    archivos_cv: list[UploadFile] = File(..., description="Múltiples CVs — PDF, DOCX, JPG, PNG"),
    config: str = Form("c2"),
):
    """
    Evalúa varios CVs a la vez contra un cargo.
    Retorna lista ordenada por score descendente.
    """
    print(f"[API] Invocando evaluar_batch: cargo_id={cargo_id}, config={config}, num_cvs={len(archivos_cv)}")

    if cargo_id not in _cargos:
        print(f"[API ERROR] Cargo {cargo_id} no encontrado.")
        raise HTTPException(status_code=404, detail="Cargo no encontrado.")

    if len(archivos_cv) > 50:
        print(f"[API ERROR] Exceso de CVs: {len(archivos_cv)}")
        raise HTTPException(status_code=400, detail="Máximo 50 CVs por lote.")

    cargo = _cargos[cargo_id]
    resultados_batch = []

    # Instanciar pipeline UNA SOLA VEZ para todo el batch, en thread pool para
    # no bloquear el event loop de FastAPI durante la carga del modelo de embeddings
    from rag.pipeline import SistacRAGPipeline
    print(f"[API] Instanciando SistacRAGPipeline con config={config}...")
    pipeline = await run_in_threadpool(SistacRAGPipeline, config=config)

    # Extraer texto de todos los archivos válidos
    valid_cvs = {}  # {cv_id: (cv_text, filename)}
    for archivo_cv in archivos_cv:
        print(f"[API] Procesando archivo de CV: {archivo_cv.filename}")
        ext = Path(archivo_cv.filename).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            print(f"[API WARN] Formato no soportado para CV: {archivo_cv.filename} ({ext})")
            resultados_batch.append({
                "archivo_cv": archivo_cv.filename,
                "error": f"Formato '{ext}' no soportado.",
                "score": None,
                "decision": "ERROR",
            })
            continue

        data = await archivo_cv.read()
        try:
            cv_text = extract_text(data, archivo_cv.filename)
            print(f"[API] Texto extraído exitosamente de {archivo_cv.filename} ({len(cv_text)} caracteres)")
        except Exception as exc:
            print(f"[API ERROR] Fallo al extraer texto de {archivo_cv.filename}: {exc}")
            resultados_batch.append({
                "archivo_cv": archivo_cv.filename,
                "error": f"No se pudo leer el archivo: {exc}",
                "score": None,
                "decision": "ERROR",
            })
            continue

        if len(cv_text.strip()) < 50:
            print(f"[API WARN] CV {archivo_cv.filename} parece vacío o muy corto.")
            resultados_batch.append({
                "archivo_cv": archivo_cv.filename,
                "error": "Documento vacío o ilegible.",
                "score": None,
                "decision": "ERROR",
            })
            continue

        cv_id = f"CV_{str(uuid.uuid4())[:8].upper()}"
        valid_cvs[cv_id] = (cv_text, archivo_cv.filename)

    # Indexar todos los CVs válidos juntos en Azure AI Search (si C2/C3)
    if config in {"c2", "c3"} and valid_cvs:
        try:
            print(f"[API] Iniciando indexación de {len(valid_cvs)} CVs para cargo {cargo_id}...")
            cv_texts_to_index = {cid: val[0] for cid, val in valid_cvs.items()}
            await run_in_threadpool(
                pipeline.index,
                cv_texts=cv_texts_to_index,
                jd_texts={cargo_id: cargo["descripcion"]}
            )
            print(f"[API] Indexación completada exitosamente.")
        except Exception as exc:
            print(f"[API ERROR] Falló la indexación en el Vector Store: {exc}")
            for cid, (cv_text, filename) in valid_cvs.items():
                resultados_batch.append({
                    "archivo_cv": filename,
                    "error": f"Fallo al indexar en Vector Store: {exc}",
                    "score": None,
                    "decision": "ERROR",
                })
            valid_cvs = {}  # Limpiar para no evaluar sin índice

    # Evaluar los CVs válidos
    for cv_id, (cv_text, filename) in valid_cvs.items():
        try:
            print(f"[API] Evaluando candidato: {filename} (ID: {cv_id}) contra JD {cargo_id}...")
            resultado = await run_in_threadpool(
                pipeline.evaluate,
                cv_id=cv_id,
                cv_text=cv_text,
                jd_id=cargo_id,
                jd_text=cargo["descripcion"],
            )
            print(f"[API] Candidato {filename} evaluado. Score: {resultado.get('score')}, Decisión: {resultado.get('decision')}")

            entrada = {
                "id":              str(uuid.uuid4())[:8],
                "cv_id":           cv_id,
                "candidato_nombre": Path(filename).stem,
                "archivo_cv":      filename,
                "cargo_id":        cargo_id,
                "cargo_nombre":    cargo["nombre"],
                "score":           resultado["score"],
                "decision":        resultado["decision"],
                "justificacion":   resultado["justification"],
                "dimensiones":     resultado.get("dimensions", {}),
                "chunks_usados":   resultado.get("chunks_used", 0),
                "chunks":          resultado.get("chunks", []),
                "anonimizado":     resultado.get("anonymized", False),
                "tiempo_segundos": resultado.get("time_seconds", 0),
                "config":          config,
                "fecha":           datetime.now().isoformat(),
                "error":           None,
            }
            _resultados.insert(0, entrada)
            _cargos[cargo_id]["candidatos"] += 1
            if resultados_col is not None:
                try:
                    resultados_col.insert_one(dict(entrada))
                except Exception as e:
                    print(f"[WARN] Error guardando resultado en MongoDB: {e}")
            if cargos_col is not None:
                try:
                    cargos_col.update_one({"id": cargo_id}, {"$inc": {"candidatos": 1}})
                except Exception as e:
                    print(f"[WARN] Error incrementando candidatos en MongoDB: {e}")
            resultados_batch.append(entrada)
        except Exception as exc:
            resultados_batch.append({
                "archivo_cv": filename,
                "error": f"Error en pipeline: {exc}",
                "score": None,
                "decision": "ERROR",
            })

    # Ordenar: APTOs primero, luego por score descendente, errores al final
    resultados_batch.sort(key=lambda r: (
        0 if r.get("decision") == "ERROR" else 1,
        -(r.get("score") or 0),
    ), reverse=False)
    resultados_batch.sort(key=lambda r: (r.get("decision") == "ERROR", -(r.get("score") or 0)))

    return {
        "cargo_nombre": cargo["nombre"],
        "total":        len(resultados_batch),
        "aptos":        sum(1 for r in resultados_batch if r.get("decision") == "APTO"),
        "no_aptos":     sum(1 for r in resultados_batch if r.get("decision") == "NO_APTO"),
        "errores":      sum(1 for r in resultados_batch if r.get("decision") == "ERROR"),
        "resultados":   resultados_batch,
    }


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
    # TODO completo en thread pool — SistacRAGPipeline() + evaluate() son bloqueantes
    # (carga de SentenceTransformer + requests a Azure), correrlos en el thread pool
    # evita bloquear el event loop de FastAPI → previene "Failed to Fetch"
    def _run_pipeline() -> dict:
        from rag.pipeline import SistacRAGPipeline
        p = SistacRAGPipeline(config=config)
        if config in {"c2", "c3"}:
            p.index(cv_texts={cv_id: cv_text}, jd_texts={cargo_id: cargo["descripcion"]})
        return p.evaluate(
            cv_id=cv_id,
            cv_text=cv_text,
            jd_id=cargo_id,
            jd_text=cargo["descripcion"],
        )

    try:
        resultado = await run_in_threadpool(_run_pipeline)
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
        "chunks":           resultado.get("chunks", []),
        "anonimizado":      resultado.get("anonymized", False),
        "tiempo_segundos":  resultado.get("time_seconds", 0),
        "config":           config,
        "fecha":            datetime.now().isoformat(),
    }
    _resultados.insert(0, entrada)
    _cargos[cargo_id]["candidatos"] += 1
    if resultados_col is not None:
        try:
            resultados_col.insert_one(dict(entrada))
        except Exception as e:
            print(f"[WARN] Error guardando resultado en MongoDB: {e}")
    if cargos_col is not None:
        try:
            cargos_col.update_one({"id": cargo_id}, {"$inc": {"candidatos": 1}})
        except Exception as e:
            print(f"[WARN] Error incrementando candidatos en MongoDB: {e}")

    return entrada


@app.get("/api/resultados")
def listar_resultados(cargo_id: Optional[str] = None, limite: int = 100):
    if resultados_col is not None:
        try:
            query = {}
            if cargo_id:
                query["cargo_id"] = cargo_id
            db_res = list(resultados_col.find(query, {"_id": 0}).sort([("fecha", -1)]).limit(limite))
            return {"resultados": db_res, "total": resultados_col.count_documents(query)}
        except Exception as e:
            print(f"[WARN] Error consultando resultados de MongoDB: {e}")
            
    resultados = _resultados
    if cargo_id:
        resultados = [r for r in resultados if r["cargo_id"] == cargo_id]
    return {"resultados": resultados[:limite], "total": len(resultados)}


# ── API: Generación de Casos Sintéticos (Gold Standard) ─────────────────────────

@app.post("/api/casos/simular-candidato")
async def simular_candidato(
    cargo_id: str = Form(...),
    gender: Optional[str] = Form(None),
    age_group: Optional[str] = Form(None),
    afinidad: Optional[str] = Form(None),
):
    """
    Genera un candidato aleatorio (con PII y afinidad aleatoria o parametrizada) basado en la JD del cargo.
    """
    if cargo_id not in _cargos:
        raise HTTPException(status_code=404, detail="Cargo no encontrado.")
    
    cargo = _cargos[cargo_id]
    jd_desc = cargo["descripcion"]
    
    # Pools locales de nombres y apellidos uruguayos (rioplatenses)
    nombres_f = [
        "Ana Laura", "María José", "Valentina", "Florencia", "Camila",
        "Lucía", "Sofía", "Natalia", "Carolina", "Gabriela",
        "Verónica", "Alejandra", "Patricia", "Jimena", "Romina"
    ]
    nombres_m = [
        "Santiago", "Martín", "Alejandro", "Federico", "Nicolás",
        "Gonzalo", "Pablo", "Sebastián", "Diego", "Matías",
        "Andrés", "Carlos", "Jorge", "Roberto", "Hernán"
    ]
    apellidos = [
        "González", "Rodríguez", "García", "Fernández", "López",
        "Martínez", "Sánchez", "Pérez", "Gómez", "Díaz",
        "Ruiz", "Suárez", "Molina", "Morales", "Castro"
    ]
    barrios = ["Pocitos", "Punta Carretas", "Malvín", "Buceo", "Carrasco", "Centro", "Cordón"]
    calles = ["Av. Brasil", "Bulevar Artigas", "Av. Italia", "Av. 18 de Julio", "Calle Colonia", "Rivera"]
    
    # Seleccionar género, edad y afinidad
    if not gender or gender not in {"F", "M"}:
        gender = random.choice(["F", "M"])
        
    if not age_group or age_group not in {"23-35", "36-45", "46-58"}:
        age_group = random.choice(["23-35", "36-45", "46-58"])
    
    if age_group == "23-35":
        age = random.randint(23, 35)
    elif age_group == "36-45":
        age = random.randint(36, 45)
    else:
        age = random.randint(46, 58)
        
    if not afinidad or afinidad not in {"alto", "medio", "bajo"}:
        afinidad = random.choice(["alto", "medio", "bajo"])
    
    # Generar PII
    nombre = random.choice(nombres_f if gender == "F" else nombres_m)
    apellido1 = random.choice(apellidos)
    apellido2 = random.choice(apellidos)
    nombre_completo = f"{nombre} {apellido1} {apellido2}"
    
    email = f"{nombre.split()[0].lower()}.{apellido1.lower()}{random.randint(1,99)}@gmail.com"
    telefono = f"+34 6{random.randint(10,99)} {random.randint(100,999)} {random.randint(100,999)}"
    direccion = f"{random.choice(calles)} {random.randint(800, 3500)}, {random.choice(barrios)}, Montevideo"
    
    prompt = f"""
    Genera el contenido de un currículum vitae (CV) en formato de texto plano para un/a candidato/a en Uruguay.
    Nombre del candidato: {nombre_completo}
    Género: {gender}
    Edad: {age} años
    El currículum debe ser para postular al siguiente cargo (Descripción de Puesto - JD):
    ---
    {jd_desc}
    ---
    Nivel de adecuación/afinidad deseado con el cargo: {afinidad}
    * Si es 'alto', debe ser muy calificado, con experiencia y habilidades completas y alineadas con la JD.
    * Si es 'medio', debe ser aceptable pero con algunas brechas de experiencia o falta de algunas tecnologías requeridas.
    * Si es 'bajo', debe no cumplir con los requisitos básicos (ej. campo de estudio errado, muy poca experiencia, o falta total de las habilidades técnicas requeridas).
    
    Por favor redacta el currículum de forma natural y realista. Incluye los siguientes datos de contacto:
    Email: {email}
    Teléfono: {telefono}
    Dirección: {direccion}
    Resumen profesional, historial de experiencia laboral detallada con años y roles (los años deben ser coherentes con la edad de {age} años del candidato), estudios universitarios en Uruguay, y habilidades técnicas.
    
    Retorna SOLAMENTE el currículum formateado en texto plano, sin comentarios ni explicaciones adicionales, ni introducciones como 'Aquí tienes el currículum...'. Empieza directamente con el nombre del candidato.
    """
    
    from llm.provider import get_chat_completion
    try:
        cv_text = await run_in_threadpool(
            get_chat_completion,
            prompt=prompt,
            system="Eres un redactor experto de currículums profesionales en español rioplatense."
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al generar con LLM: {exc}")
        
    return {
        "nombre": nombre_completo,
        "gender": gender,
        "age_group": age_group,
        "age": age,
        "cv_text": cv_text.strip(),
        "afinidad": afinidad
    }


@app.post("/api/casos/guardar-decision")
async def guardar_decision(
    cargo_id: str = Form(...),
    cv_text: str = Form(...),
    decision: str = Form(...),
    gender: str = Form(...),
    age_group: str = Form(...),
    time_spent_seconds: float = Form(...),
):
    """
    Guarda el CV y registra la decisión del reclutador en el Gold Standard.
    """
    if cargo_id not in _cargos:
        raise HTTPException(status_code=404, detail="Cargo no encontrado.")
    
    # Asegurar directorios creados
    GOLD_STANDARD_DIR.mkdir(parents=True, exist_ok=True)
    CVS_RAW.mkdir(parents=True, exist_ok=True)
    
    # Generar el siguiente ID correlativo
    gt_path = GOLD_STANDARD_DIR / "ground_truth.csv"
    max_num = 300
    if gt_path.exists():
        try:
            with open(gt_path, mode="r", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    cv_id = row.get("cv_id", "")
                    if cv_id.startswith("CV_"):
                        try:
                            num = int(cv_id.split("_")[1])
                            if num > max_num:
                                max_num = num
                        except (IndexError, ValueError):
                            pass
        except Exception as e:
            print(f"[WARN] Error leyendo ground_truth.csv: {e}")
            
    next_id = f"CV_{max_num + 1:03d}"
    
    # Guardar el CV .txt en data/raw/cvs/
    cv_file_path = CVS_RAW / f"{next_id}.txt"
    try:
        cv_file_path.write_text(cv_text, encoding="utf-8-sig")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al escribir el archivo del CV: {exc}")
        
    # Registrar en ground_truth.csv
    expected_score = 85 if decision == "APTO" else 30
    escribir_cabecera_gt = not gt_path.exists()
    try:
        with open(gt_path, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["cv_id", "jd_id", "expected_label", "expected_score", "group_gender", "group_age", "eval_source"])
            if escribir_cabecera_gt:
                writer.writeheader()
            writer.writerow({
                "cv_id": next_id,
                "jd_id": cargo_id,
                "expected_label": decision,
                "expected_score": expected_score,
                "group_gender": gender,
                "group_age": age_group,
                "eval_source": "aplicacion_interactiva"
            })
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al escribir en ground_truth.csv: {exc}")
        
    # Registrar en c0_times.csv
    c0_path = GOLD_STANDARD_DIR / "c0_times.csv"
    escribir_cabecera_c0 = not c0_path.exists()
    try:
        with open(c0_path, mode="a", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=["cv_id", "jd_id", "time_seconds", "decision", "evaluator_id"])
            if escribir_cabecera_c0:
                writer.writeheader()
            writer.writerow({
                "cv_id": next_id,
                "jd_id": cargo_id,
                "time_seconds": round(time_spent_seconds, 1),
                "decision": decision,
                "evaluator_id": "EVAL_INTERACTIVE"
            })
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Error al escribir en c0_times.csv: {exc}")
        
    # Persistir en las colecciones de MongoDB para mantenerlas sincronizadas en tiempo real
    if db is not None:
        try:
            lineas = [l.strip() for l in cv_text.splitlines() if l.strip()]
            nombre_candidato = lineas[0] if lineas else "Candidato Simulado"
            
            # 1. Colección cvs
            db["cvs"].update_one(
                {"id": next_id},
                {"$set": {
                    "id": next_id,
                    "nombre": nombre_candidato,
                    "contenido": cv_text,
                    "archivo": f"{next_id}.txt",
                    "fecha_importacion": datetime.now().isoformat()
                }},
                upsert=True
            )
            
            # 2. Colección ground_truth
            db["ground_truth"].update_one(
                {"cv_id": next_id, "jd_id": cargo_id},
                {"$set": {
                    "cv_id": next_id,
                    "jd_id": cargo_id,
                    "expected_label": decision,
                    "expected_score": expected_score,
                    "group_gender": gender,
                    "group_age": age_group,
                    "eval_source": "aplicacion_interactiva"
                }},
                upsert=True
            )
            
            # 3. Colección c0_times
            db["c0_times"].update_one(
                {"cv_id": next_id, "jd_id": cargo_id},
                {"$set": {
                    "cv_id": next_id,
                    "jd_id": cargo_id,
                    "time_seconds": round(time_spent_seconds, 1),
                    "decision": decision,
                    "evaluator_id": "EVAL_INTERACTIVE"
                }},
                upsert=True
            )
            print(f"[INFO] Caso {next_id} guardado en MongoDB con éxito.")
        except Exception as e:
            print(f"[WARN] Error al guardar el caso simulado en MongoDB: {e}")
        
    return {
        "status": "success",
        "cv_id": next_id,
        "decision": decision,
        "time_seconds": round(time_spent_seconds, 1)
    }


# ── API: Administración y Experimentos ──────────────────────────────────────────

@app.post("/api/admin/reset-indice")
async def reset_indice():
    """
    Borra y recrea el índice sistac-cvs en Azure AI Search (create_index.py --delete).
    """
    try:
        from rag.create_index import delete_index, create_index
        await run_in_threadpool(delete_index)
        await run_in_threadpool(create_index)
        return {"status": "success", "message": "El índice vectorial en Azure AI Search ha sido borrado y recreado desde cero."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Fallo al resetear el índice en Azure: {exc}")


_indexacion_activa = False
_experimento_activo = False


@app.post("/api/admin/indexar-corpus")
async def indexar_corpus(background_tasks: BackgroundTasks, config: str = "c2"):
    """
    Indexa los CVs y JDs en Azure AI Search en segundo plano.
    """
    global _indexacion_activa
    if _indexacion_activa:
        raise HTTPException(status_code=400, detail="La indexación ya está en ejecución en segundo plano.")

    try:
        from rag.index_corpus import index_corpus, load_corpus
        
        def run_indexing():
            global _indexacion_activa
            try:
                cv_texts, jd_texts = load_corpus()
                index_corpus(cv_texts, jd_texts, config=config)
            finally:
                _indexacion_activa = False
            
        _indexacion_activa = True
        background_tasks.add_task(run_indexing)
        return {
            "status": "success", 
            "message": f"La indexación del corpus (config={config.upper()}) se ha iniciado en segundo plano. Esto demorará unos minutos."
        }
    except Exception as exc:
        _indexacion_activa = False
        raise HTTPException(status_code=500, detail=f"Fallo al iniciar la indexación del corpus: {exc}")


@app.get("/api/admin/estado-indexacion")
async def estado_indexacion():
    global _indexacion_activa
    return {"activo": _indexacion_activa}


@app.post("/api/admin/ejecutar-experimento")
async def ejecutar_experimento(background_tasks: BackgroundTasks):
    """
    Inicia la ejecución del experimento completo de los 300 CVs en segundo plano.
    """
    global _experimento_activo
    if _experimento_activo:
        raise HTTPException(status_code=400, detail="El experimento ya está en ejecución en segundo plano.")

    from experiments.orquestador_c0_c3 import main as run_experiment
    try:
        def run_wrapper():
            global _experimento_activo
            try:
                run_experiment()
            finally:
                _experimento_activo = True  # En realidad queremos ponerlo a False, pero espera:
                # Si ponemos _experimento_activo = False en la finalización:
                _experimento_activo = False
                
        _experimento_activo = True
        background_tasks.add_task(run_wrapper)
        return {"status": "success", "message": "El experimento factorial completo (C0-C3) se ha iniciado en segundo plano."}
    except Exception as exc:
        _experimento_activo = False
        raise HTTPException(status_code=500, detail=f"Error al iniciar el experimento: {exc}")


@app.get("/api/admin/estado-experimento")
async def estado_experimento():
    global _experimento_activo
    return {"activo": _experimento_activo}



def _eliminar_archivo_temp(path: str):
    import os
    import shutil
    try:
        if os.path.exists(path):
            os.remove(path)
        parent = os.path.dirname(path)
        if os.path.exists(parent) and ("tmp" in parent or "temp" in parent):
            shutil.rmtree(parent, ignore_errors=True)
    except Exception as e:
        print(f"[WARN] Error al limpiar archivo temporal: {e}")


@app.get("/api/admin/descargar-tablas")
def descargar_tablas(background_tasks: BackgroundTasks):
    """
    Genera el reporte Excel, compila los gráficos y tablas en carpetas ordenadas
    y los descarga en un único archivo ZIP.
    """
    from config import TABLES_DIR
    import shutil
    import tempfile
    from fastapi.responses import FileResponse
    
    # 1. Intentar generar el reporte Excel actualizado
    try:
        from evaluation.export_excel_report import generate_excel_report
        generate_excel_report()
    except Exception as e:
        print(f"[WARN] No se pudo generar el reporte Excel dinámico: {e}")
        
    if not TABLES_DIR.exists() or not any(TABLES_DIR.iterdir()):
        raise HTTPException(
            status_code=404,
            detail="No hay tablas ni métricas generadas para descargar. Ejecutá el experimento primero."
        )
    
    # 2. Crear una estructura temporal limpia para organizar el ZIP
    temp_workspace = tempfile.mkdtemp()
    zip_dir = Path(temp_workspace) / "resultados_tfe_sistac"
    zip_dir.mkdir()
    
    # Copiar tablas a /tablas
    tablas_dest = zip_dir / "tablas"
    shutil.copytree(str(TABLES_DIR), str(tablas_dest))
    
    # Copiar figuras de matplotlib si existen a /graficos
    figures_source = _PROJECT_ROOT / "paper" / "figures" / "cap5"
    if figures_source.exists() and any(figures_source.iterdir()):
        graficos_dest = zip_dir / "graficos"
        shutil.copytree(str(figures_source), str(graficos_dest))
        
    # 3. Crear el archivo ZIP comprimido
    zip_output_dir = tempfile.mkdtemp()
    zip_base = Path(zip_output_dir) / "tablas_resultados_sistac"
    
    try:
        shutil.make_archive(str(zip_base), "zip", root_dir=str(zip_dir))
        full_zip_path = Path(f"{zip_base}.zip")
        
        if not full_zip_path.exists():
            raise HTTPException(status_code=500, detail="Error al generar el archivo ZIP.")
            
        # Programar la limpieza de todo el espacio de trabajo temporal
        background_tasks.add_task(_eliminar_archivo_temp, str(full_zip_path))
        background_tasks.add_task(_eliminar_archivo_temp, str(temp_workspace))
        
        return FileResponse(
            path=full_zip_path,
            filename="tablas_resultados_sistac.zip",
            media_type="application/zip"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al comprimir tablas y gráficos: {str(e)}")


@app.get("/api/admin/metricas")
async def obtener_metricas():
    """
    Lee las métricas consolidadas (H1, H2, H3) desde paper/tables/ si existen.
    Si no existen, retorna status "no_data".
    """
    from config import TABLES_DIR
    import csv
    
    h1_path = TABLES_DIR / "tab_resultados_h1.csv"
    h2_path = TABLES_DIR / "tab_resultados_h2.csv"
    h3_path = TABLES_DIR / "tab_resultados_h3.csv"
    ragas_path = TABLES_DIR / "tab_ragas_c2.csv"
    
    if not (h1_path.exists() or h2_path.exists() or h3_path.exists()):
        return {"status": "no_data", "message": "No se encontraron archivos de métricas generados. Ejecutá el experimento primero."}
        
    def _cargar_csv(path: Path) -> list[dict]:
        if not path.exists():
            return []
        try:
            with open(path, mode="r", encoding="utf-8") as f:
                return list(csv.DictReader(f))
        except Exception as e:
            print(f"[WARN] Error leyendo {path.name}: {e}")
            return []
            
    h1_data = await run_in_threadpool(_cargar_csv, h1_path)
    h2_data = await run_in_threadpool(_cargar_csv, h2_path)
    h3_data = await run_in_threadpool(_cargar_csv, h3_path)
    ragas_data = await run_in_threadpool(_cargar_csv, ragas_path)
    
    return {
        "status": "success",
        "h1": h1_data,
        "h2": h2_data,
        "h3": h3_data,
        "ragas": ragas_data
    }


class GuardarMetricasRequest(BaseModel):
    comentario: str
    datos_metricas: dict


@app.post("/api/admin/metricas/guardar")
async def guardar_metricas(req: GuardarMetricasRequest):
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB no está conectado. Verifica tu MONGO_URI en el archivo .env.")
    try:
        doc = {
            "fecha": datetime.now().isoformat(),
            "comentario": req.comentario,
            "h1": req.datos_metricas.get("h1", []),
            "h2": req.datos_metricas.get("h2", []),
            "h3": req.datos_metricas.get("h3", []),
            "ragas": req.datos_metricas.get("ragas", []),
        }
        res = db["metricas_historial"].insert_one(doc)
        return {"status": "success", "message": "Métricas persistidas en MongoDB con éxito.", "version_id": str(res.inserted_id)}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Fallo al guardar métricas en MongoDB: {exc}")


@app.get("/api/admin/metricas/historial")
async def obtener_historial_metricas():
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB no está conectado. Verifica tu MONGO_URI en el archivo .env.")
    try:
        cursor = db["metricas_historial"].find({}, {"_id": 1, "fecha": 1, "comentario": 1}).sort("fecha", -1)
        versiones = []
        for doc in cursor:
            versiones.append({
                "id": str(doc["_id"]),
                "fecha": doc["fecha"],
                "comentario": doc["comentario"]
            })
        return {"status": "success", "versiones": versiones}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Fallo al obtener historial de métricas: {exc}")


@app.get("/api/admin/metricas/version/{version_id}")
async def obtener_version_metricas(version_id: str):
    if db is None:
        raise HTTPException(status_code=500, detail="MongoDB no está conectado. Verifica tu MONGO_URI en el archivo .env.")
    try:
        doc = db["metricas_historial"].find_one({"_id": ObjectId(version_id)})
        if not doc:
            raise HTTPException(status_code=404, detail="Versión de métricas no encontrada.")
        return {
            "status": "success",
            "fecha": doc["fecha"],
            "comentario": doc["comentario"],
            "h1": doc.get("h1", []),
            "h2": doc.get("h2", []),
            "h3": doc.get("h3", []),
            "ragas": doc.get("ragas", []),
        }
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Fallo al obtener la versión de métricas: {exc}")

# ── API: Gestión de .env ──────────────────────────────────────────────────────

class EnvUpdateRequest(BaseModel):
    variables: dict[str, str]

@app.get("/api/admin/env")
def get_env_variables():
    """
    Retorna las variables de entorno activas del archivo .env
    """
    env_path = _PROJECT_ROOT / ".env"
    result = {}
    if env_path.exists():
        try:
            content = env_path.read_text(encoding="utf-8")
            for line in content.splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, val = line.split("=", 1)
                    val = val.strip()
                    if (val.startswith('"') and val.endswith('"')) or (val.startswith("'") and val.endswith("'")):
                        val = val[1:-1]
                    result[key.strip()] = val
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error al leer el archivo .env: {e}")
            
    # Garantizar que las variables estándar están presentes
    std_keys = [
        "LLM_PROVIDER", "ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GOOGLE_API_KEY",
        "AZURE_SEARCH_ENDPOINT", "AZURE_SEARCH_KEY", "AZURE_SEARCH_INDEX",
        "HF_TOKEN", "USE_EXTERNAL_DATA", "AZURE_SEARCH_INDEX_EXTERNAL", "MONGO_URI"
    ]
    for k in std_keys:
        if k not in result:
            result[k] = os.getenv(k, "")
            
    return {"status": "success", "variables": result}

def _auto_restart():
    import time
    import os
    time.sleep(1.0)
    print("[INFO] Autoreinicio del contenedor para aplicar variables de entorno...")
    os._exit(0)

@app.post("/api/admin/env")
async def update_env_variables(req: EnvUpdateRequest, background_tasks: BackgroundTasks):
    """
    Actualiza el archivo .env y fuerza la recarga de uvicorn tocando main.py
    """
    env_path = _PROJECT_ROOT / ".env"
    try:
        lines = []
        if env_path.exists():
            lines = env_path.read_text(encoding="utf-8").splitlines()
        
        updated_keys = set()
        new_lines = []
        for line in lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#") and "=" in stripped:
                key, _ = stripped.split("=", 1)
                key = key.strip()
                if key in req.variables:
                    new_lines.append(f"{key}={req.variables[key]}")
                    updated_keys.add(key)
                    continue
            new_lines.append(line)
            
        for k, v in req.variables.items():
            if k not in updated_keys:
                new_lines.append(f"{k}={v}")
                
        env_content = "\n".join(new_lines) + "\n"
        env_path.write_text(env_content, encoding="utf-8")
        
        # Actualizar os.environ para el proceso actual por si acaso
        for k, v in req.variables.items():
            os.environ[k] = v
            
        # Tocar app/main.py para forzar el reinicio de uvicorn si está en modo reload
        main_py = Path(__file__)
        if main_py.exists():
            main_py.touch()
            
        # Registrar el autoreinicio del contenedor en segundo plano
        background_tasks.add_task(_auto_restart)
            
        return {"status": "success", "message": "Variables de entorno guardadas correctamente. El servidor se está reiniciando para aplicar los cambios."}
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Fallo al escribir en el archivo .env: {exc}")



# ── Diagnóstico ───────────────────────────────────────────────────────────────

@app.get("/api/diagnostico")
def diagnostico():
    """
    Verifica el estado de cada componente del sistema.
    Útil para debuggear antes de evaluar CVs.
    """
    import importlib
    resultado = {}

    # LLM keys
    from config import ANTHROPIC_API_KEY, OPENAI_API_KEY, AZURE_SEARCH_ENDPOINT, AZURE_SEARCH_KEY, GOOGLE_API_KEY
    resultado["anthropic_key"] = "OK" if ANTHROPIC_API_KEY else "FALTA (.env → ANTHROPIC_API_KEY)"
    resultado["openai_key"]    = "OK" if OPENAI_API_KEY    else "FALTA (.env → OPENAI_API_KEY) — opcional"
    resultado["google_key"]    = "OK" if GOOGLE_API_KEY    else "FALTA (.env → GOOGLE_API_KEY) — para PDF escaneados e imágenes"
    resultado["azure_endpoint"] = "OK" if AZURE_SEARCH_ENDPOINT else "FALTA (.env → AZURE_SEARCH_ENDPOINT)"
    resultado["azure_key"]      = "OK" if AZURE_SEARCH_KEY      else "FALTA (.env → AZURE_SEARCH_KEY)"

    # Dependencias Python críticas
    deps = {
        "fastapi":              "fastapi",
        "python-multipart":     "multipart",
        "pdfplumber":           "pdfplumber",
        "python-docx":          "docx",
        "anthropic":            "anthropic",
        "sentence-transformers":"sentence_transformers",
        "langchain-text-splitters": "langchain_text_splitters",
        "requests":             "requests",
    }
    dep_status = {}
    for nombre, modulo in deps.items():
        try:
            importlib.import_module(modulo)
            dep_status[nombre] = "OK"
        except ImportError:
            dep_status[nombre] = "NO INSTALADO — pip install " + nombre
    resultado["dependencias"] = dep_status

    # Estado del pipeline C1 (solo LLM, sin Azure ni embeddings)
    c1_ok = bool(ANTHROPIC_API_KEY or OPENAI_API_KEY)
    resultado["c1_listo"] = c1_ok
    resultado["c2_listo"] = c1_ok and bool(AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY)
    resultado["c3_listo"] = resultado["c2_listo"]

    resultado["consejo"] = (
        "Podés evaluar con C1 (solo LLM) sin Azure ni modelos locales. "
        "Seleccioná C1 en el pipeline si Azure no está configurado."
        if not resultado["c2_listo"] else
        "Sistema listo para C1/C2/C3."
    )

    return resultado


# ── Frontend ──────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def frontend():
    html_path = Path(__file__).parent / "static" / "index.html"
    if html_path.exists():
        return html_path.read_text(encoding="utf-8")
    return HTMLResponse("<h1>SISTAC</h1><p>Frontend no encontrado en app/static/index.html</p>")
