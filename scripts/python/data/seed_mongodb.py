"""
scripts/python/data/seed_mongodb.py
Lee los currículums, puestos, ground truth y tiempos C0 del disco local y los
importa (siembra/seed) en la base de datos MongoDB.
"""

from __future__ import annotations

import csv
import os
from pathlib import Path
from pymongo import MongoClient

import sys

# Rutas via PROJECT_ROOT
SCRIPTS_DIR = Path(__file__).parent.parent
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

from config import CVS_RAW, JOB_DESCRIPTIONS, GOLD_STANDARD_DIR

CVS_DIR = CVS_RAW
JDS_DIR = JOB_DESCRIPTIONS
GOLD_DIR = GOLD_STANDARD_DIR

def seed_database():
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=2000)
        # Validar conexión
        client.server_info()
        db = client["sistac_tfe"]
        print(f"[SEED] Conectado a MongoDB en {mongo_uri}")
    except Exception as e:
        print(f"[SEED] Advertencia: No se pudo conectar a MongoDB para sembrar: {e}")
        return

    # Asegurar que las carpetas existan en el contenedor
    from config import ensure_dirs, EVAL_SETS
    ensure_dirs()
    CVS_DIR.mkdir(parents=True, exist_ok=True)
    JDS_DIR.mkdir(parents=True, exist_ok=True)
    GOLD_DIR.mkdir(parents=True, exist_ok=True)

    cargos_col = db["cargos"]
    cvs_col = db["cvs"]
    gt_col = db["ground_truth"]
    c0_col = db["c0_times"]

    # ==========================================
    # 1. Fase de Importación (Disco -> MongoDB)
    # ==========================================
    
    # 1.1 Importar Cargos
    if JDS_DIR.exists():
        jd_count = 0
        for jd_file in JDS_DIR.glob("JD_*.txt"):
            jd_id = jd_file.stem
            # Si ya existe en MongoDB, no lo sobreescribimos desde disco
            if cargos_col.find_one({"id": jd_id}):
                continue
                
            content = jd_file.read_text(encoding="utf-8")
            
            # Extraer el nombre del cargo
            nombre_cargo = "Cargo Simulado"
            for line in content.splitlines():
                if line.upper().startswith("CARGO:"):
                    nombre_cargo = line[6:].strip()
                    break
            
            # Limpiar markdown de nombre_cargo
            nombre_cargo = nombre_cargo.replace("#", "").replace("*", "").strip()
            
            # Si el nombre es genérico como "Posición Técnica Externa" o similar, buscar un título real
            if "Posición" in nombre_cargo or "Cargo" in nombre_cargo:
                for line in content.splitlines():
                    cleaned_line = line.strip().replace("#", "").replace("*", "").strip()
                    if line.strip().startswith("##") or line.strip().startswith("###"):
                        upper_line = cleaned_line.upper()
                        if cleaned_line and not any(kw in upper_line for kw in ["RESPONSABILIDADES", "HABILIDADES", "REQUISITOS", "POR QUÉ", "CÓMO", "EMPRESA"]):
                            nombre_cargo = cleaned_line
                            break
                            
            # Si todavía sigue siendo genérico, intentar extraer de patrones "como **Cargo**"
            if "Posición" in nombre_cargo or "Cargo" in nombre_cargo:
                import re
                for line in content.splitlines():
                    match = re.search(r"como\s+\*\*([^*]+)\*\*", line, re.IGNORECASE)
                    if match:
                        nombre_cargo = match.group(1).strip()
                        break
            
            cargo_data = {
                "id": jd_id,
                "nombre": nombre_cargo,
                "descripcion": content,
                "archivo": jd_file.name,
                "config": "c2",
                "fecha": "2026-06-06T00:00:00",
                "candidatos": 0
            }
            cargos_col.update_one({"id": jd_id}, {"$set": cargo_data}, upsert=True)
            jd_count += 1
        if jd_count > 0:
            print(f"[SEED] {jd_count} nuevos cargos (JDs) importados a MongoDB.")

    # 1.2 Importar CVs
    if CVS_DIR.exists():
        cv_count = 0
        for cv_file in CVS_DIR.glob("CV_*.txt"):
            cv_id = cv_file.stem
            # Si ya existe en MongoDB, no sobreescribir
            if cvs_col.find_one({"id": cv_id}):
                continue
                
            content = cv_file.read_text(encoding="utf-8")
            
            # Extraer la primera línea no vacía para el nombre
            lineas = [l.strip() for l in content.splitlines() if l.strip()]
            nombre_candidato = lineas[0] if lineas else "Candidato Simulado"
            
            cv_data = {
                "id": cv_id,
                "nombre": nombre_candidato,
                "contenido": content,
                "archivo": cv_file.name,
                "fecha_importacion": "2026-06-06T00:00:00"
            }
            cvs_col.update_one({"id": cv_id}, {"$set": cv_data}, upsert=True)
            cv_count += 1
        if cv_count > 0:
            print(f"[SEED] {cv_count} nuevos currículums (CVs) importados a MongoDB.")

    # 1.3 Importar Ground Truth
    gt_path = GOLD_DIR / "ground_truth.csv"
    if gt_path.exists():
        gt_count = 0
        with open(gt_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Si ya existe en MongoDB, no sobreescribir
                if gt_col.find_one({"cv_id": row["cv_id"], "jd_id": row["jd_id"]}):
                    continue
                    
                gt_data = {
                    "cv_id": row["cv_id"],
                    "jd_id": row["jd_id"],
                    "expected_label": row["expected_label"],
                    "expected_score": float(row["expected_score"]) if row.get("expected_score") else None,
                    "group_gender": row.get("group_gender", ""),
                    "group_age": row.get("group_age", ""),
                    "eval_source": row.get("eval_source", "sintetico_original")
                }
                gt_col.update_one(
                    {"cv_id": row["cv_id"], "jd_id": row["jd_id"]},
                    {"$set": gt_data},
                    upsert=True
                )
                gt_count += 1
        if gt_count > 0:
            print(f"[SEED] {gt_count} nuevos registros de Ground Truth importados a MongoDB.")

    # 1.4 Importar Tiempos C0
    c0_path = GOLD_DIR / "c0_times.csv"
    if c0_path.exists():
        c0_count = 0
        with open(c0_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if c0_col.find_one({"cv_id": row["cv_id"], "jd_id": row["jd_id"]}):
                    continue
                c0_data = {
                    "cv_id": row["cv_id"],
                    "jd_id": row["jd_id"],
                    "time_seconds": float(row["time_seconds"]) if row.get("time_seconds") else 0.0,
                    "decision": row.get("decision", ""),
                    "evaluator_id": row.get("evaluator_id", "")
                }
                c0_col.update_one(
                    {"cv_id": row["cv_id"], "jd_id": row["jd_id"]},
                    {"$set": c0_data},
                    upsert=True
                )
                c0_count += 1
        if c0_count > 0:
            print(f"[SEED] {c0_count} nuevos tiempos C0 importados a MongoDB.")

    # ==========================================
    # 2. Fase de Restauración (MongoDB -> Disco)
    # ==========================================
    
    # 2.1 Restaurar Cargos
    db_cargos = list(cargos_col.find({}))
    cargos_restaurados = 0
    for c in db_cargos:
        jd_id = c["id"]
        jd_file = JDS_DIR / f"{jd_id}.txt"
        if not jd_file.exists():
            jd_file.write_text(c["descripcion"], encoding="utf-8")
            cargos_restaurados += 1
    if cargos_restaurados > 0:
        print(f"[RESTORE] {cargos_restaurados} cargos (JDs) restaurados en el disco local.")

    # 2.2 Restaurar CVs
    db_cvs = list(cvs_col.find({}))
    cvs_restaurados = 0
    for cv in db_cvs:
        cv_id = cv["id"]
        cv_file = CVS_DIR / f"{cv_id}.txt"
        if not cv_file.exists():
            cv_file.write_text(cv["contenido"], encoding="utf-8-sig")
            cvs_restaurados += 1
    if cvs_restaurados > 0:
        print(f"[RESTORE] {cvs_restaurados} currículums (CVs) restaurados en el disco local.")

    # 2.3 Restaurar Ground Truth (Siempre lo escribimos para asegurar sincronización completa)
    db_gt = list(gt_col.find({}, {"_id": 0}))
    if db_gt:
        try:
            with open(gt_path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["cv_id", "jd_id", "expected_label", "expected_score", "group_gender", "group_age", "eval_source"])
                writer.writeheader()
                for row in db_gt:
                    writer.writerow({
                        "cv_id": row["cv_id"],
                        "jd_id": row["jd_id"],
                        "expected_label": row["expected_label"],
                        "expected_score": row.get("expected_score"),
                        "group_gender": row.get("group_gender", ""),
                        "group_age": row.get("group_age", ""),
                        "eval_source": row.get("eval_source", "")
                    })
            print(f"[RESTORE] ground_truth.csv regenerado con {len(db_gt)} filas desde MongoDB.")
        except Exception as e:
            print(f"[WARN] Error escribiendo ground_truth.csv: {e}")

    # 2.4 Restaurar Tiempos C0 (Siempre lo escribimos para asegurar sincronización completa)
    db_c0 = list(c0_col.find({}, {"_id": 0}))
    if db_c0:
        try:
            with open(c0_path, mode="w", newline="", encoding="utf-8-sig") as f:
                writer = csv.DictWriter(f, fieldnames=["cv_id", "jd_id", "time_seconds", "decision", "evaluator_id"])
                writer.writeheader()
                for row in db_c0:
                    writer.writerow({
                        "cv_id": row["cv_id"],
                        "jd_id": row["jd_id"],
                        "time_seconds": row.get("time_seconds", 0.0),
                        "decision": row.get("decision", ""),
                        "evaluator_id": row.get("evaluator_id", "")
                    })
            print(f"[RESTORE] c0_times.csv regenerado con {len(db_c0)} filas desde MongoDB.")
        except Exception as e:
            print(f"[WARN] Error escribiendo c0_times.csv: {e}")

    # ==========================================
    # 3. Fase de Partición (Estratificación)
    # ==========================================
    train_ids_path = EVAL_SETS / "train_ids.csv"
    test_ids_path = EVAL_SETS / "test_ids.csv"
    
    if gt_path.exists() and (not train_ids_path.exists() or not test_ids_path.exists() or cvs_restaurados > 0 or cargos_restaurados > 0):
        try:
            from data.split_corpus import stratified_split, save_split
            print("[RESTORE] Re-generando train/test splits...")
            with open(gt_path, encoding="utf-8-sig") as f:
                rows = list(csv.DictReader(f))
            train, test = stratified_split(rows)
            save_split(train, train_ids_path, "TRAIN")
            save_split(test, test_ids_path, "TEST")
            print("[RESTORE] train/test splits creados exitosamente en disco.")
        except Exception as e:
            print(f"[WARN] No se pudo re-generar el split train/test: {e}")

if __name__ == "__main__":
    seed_database()
