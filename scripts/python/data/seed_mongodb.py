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

# Rutas via PROJECT_ROOT
SCRIPTS_DIR = Path(__file__).parent.parent.parent
PROJECT_ROOT = SCRIPTS_DIR.parent
DATA_RAW = PROJECT_ROOT / "data" / "raw"
CVS_DIR = DATA_RAW / "cvs"
JDS_DIR = DATA_RAW / "job_descriptions"
GOLD_DIR = DATA_RAW / "gold_standard"

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

    # 1. Sembrar JDs en la colección 'cargos'
    cargos_col = db["cargos"]
    if JDS_DIR.exists():
        jd_count = 0
        for jd_file in JDS_DIR.glob("JD_*.txt"):
            jd_id = jd_file.stem
            content = jd_file.read_text(encoding="utf-8")
            
            # Extraer el nombre del cargo
            nombre_cargo = "Cargo Simulado"
            for line in content.splitlines():
                if line.startswith("CARGO:"):
                    nombre_cargo = line.replace("CARGO:", "").strip()
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
        print(f"[SEED] {jd_count} cargos (JDs) sembrados en la colección 'cargos'.")

    # 2. Sembrar CVs en la colección 'cvs'
    cvs_col = db["cvs"]
    if CVS_DIR.exists():
        cv_count = 0
        for cv_file in CVS_DIR.glob("CV_*.txt"):
            cv_id = cv_file.stem
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
        print(f"[SEED] {cv_count} currículums (CVs) sembrados en la colección 'cvs'.")

    # 3. Sembrar Ground Truth en la colección 'ground_truth'
    gt_col = db["ground_truth"]
    gt_path = GOLD_DIR / "ground_truth.csv"
    if gt_path.exists():
        gt_count = 0
        with open(gt_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                gt_data = {
                    "cv_id": row["cv_id"],
                    "jd_id": row["jd_id"],
                    "expected_label": row["expected_label"],
                    "expected_score": float(row["expected_score"]) if row.get("expected_score") else None,
                    "group_gender": row.get("group_gender", ""),
                    "group_age": row.get("group_age", "")
                }
                gt_col.update_one(
                    {"cv_id": row["cv_id"], "jd_id": row["jd_id"]},
                    {"$set": gt_data},
                    upsert=True
                )
                gt_count += 1
        print(f"[SEED] {gt_count} registros de ground truth sembrados en la colección 'ground_truth'.")

    # 4. Sembrar Tiempos C0 en la colección 'c0_times'
    c0_col = db["c0_times"]
    c0_path = GOLD_DIR / "c0_times.csv"
    if c0_path.exists():
        c0_count = 0
        with open(c0_path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
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
        print(f"[SEED] {c0_count} registros de tiempos C0 sembrados en la colección 'c0_times'.")

if __name__ == "__main__":
    seed_database()
