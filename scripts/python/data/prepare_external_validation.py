"""
prepare_external_validation.py — Descarga, traducción e imputación del dataset público

Este script actúa como el pipeline de preparación de datos para el Dataset de Validación
Externa (que simula ser los datos reales de la empresa).

Realiza las siguientes acciones:
  1. Descarga 150 ejemplos (75 de éxito 'match' y 75 de descarte 'mismatch') del dataset
     público 'netsol/resume-score-details' de Hugging Face.
  2. Almacena las descargas en un directorio de caché local para evitar descargas redundantes.
  3. Mapea las descripciones de puestos (JDs) únicas (15 en total) y los CVs.
  4. Traduce las JDs y CVs del inglés al español rioplatense usando el LLM configurado.
     - En la llamada de traducción de CVs, le pide al LLM que infiera el género ('M' o 'F')
       del candidato a partir de su nombre de pila en la misma llamada, optimizando costos.
  5. Imputa los datos faltantes:
     - Tiempos de cribado manual C0: Uniforme 10-20 min (APTO), 5-12 min (NO_APTO).
     - Rango de edad: Distribuido de manera balanceada y uniforme entre las tres categorías.
     - ID de evaluador y Score en base 100.
  6. Guarda los archivos en data/raw/cvs_external/, data/raw/job_descriptions_external/ y
     los CSVs de Ground Truth y tiempos en data/raw/gold_standard_external/.

Uso:
    python scripts/python/data/prepare_external_validation.py
"""

import os
import sys
import json
import csv
import random
import hashlib
from pathlib import Path
import requests
from tqdm import tqdm

# Semilla fija para reproducibilidad
random.seed(42)

# Configurar rutas del proyecto
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
if str(PROJECT_ROOT / "scripts" / "python") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "scripts" / "python"))

from config import DATA_RAW, ensure_dirs
from llm.provider import get_chat_completion

# Rutas específicas para el dataset externo
CVS_EXT_DIR = DATA_RAW / "cvs_external"
JDS_EXT_DIR = DATA_RAW / "job_descriptions_external"
GOLD_EXT_DIR = DATA_RAW / "gold_standard_external"
CACHE_JSON_DIR = DATA_RAW / "cache_json"
TRANSLATION_CACHE_FILE = DATA_RAW / "translation_cache.json"

# Crear directorios si no existen
CVS_EXT_DIR.mkdir(parents=True, exist_ok=True)
JDS_EXT_DIR.mkdir(parents=True, exist_ok=True)
GOLD_EXT_DIR.mkdir(parents=True, exist_ok=True)
CACHE_JSON_DIR.mkdir(parents=True, exist_ok=True)


# ── Caché de Traducción ──────────────────────────────────────────────────────

def load_translation_cache() -> dict:
    if TRANSLATION_CACHE_FILE.exists():
        try:
            with open(TRANSLATION_CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"[WARN] Error cargando caché de traducciones: {e}")
    return {}

def save_translation_cache(cache: dict) -> None:
    try:
        with open(TRANSLATION_CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"[WARN] Error guardando caché de traducciones: {e}")

def get_text_hash(text: str) -> str:
    return hashlib.md5(text.encode("utf-8")).hexdigest()


# ── Traducciones con LLM ─────────────────────────────────────────────────────

def translate_jd(jd_text: str, cache: dict) -> str:
    text_hash = get_text_hash(jd_text)
    if text_hash in cache:
        return cache[text_hash]

    system_prompt = "Eres un traductor experto en terminología de recursos humanos y reclutamiento laboral."
    prompt = (
        "Traduce la siguiente descripción de puesto de trabajo (Job Description) del inglés al español "
        "(variedad de Argentina y Uruguay). Usa términos profesionales locales comunes en Sudamérica "
        "(por ejemplo, usa 'jornada completa', 'obra social', 'relación de dependencia', 'rango salarial', etc.). "
        "Mantén exactamente la misma estructura y formato original del texto.\n\n"
        f"TEXTO A TRADUCIR:\n{jd_text}"
    )

    print(f"  [LLM] Traduciendo Job Description...")
    translated = get_chat_completion(prompt=prompt, system=system_prompt, max_tokens=1500)
    cache[text_hash] = translated
    save_translation_cache(cache)
    return translated


def translate_cv_and_detect_gender(cv_text: str, cache: dict) -> tuple[str, str]:
    text_hash = get_text_hash(cv_text)
    if text_hash in cache:
        cached_data = cache[text_hash]
        if isinstance(cached_data, dict) and "translated_cv" in cached_data:
            return cached_data["translated_cv"], cached_data.get("gender", "M")

    system_prompt = "Eres un traductor y anotador de datos experto en reclutamiento de personal."
    prompt = (
        "Traduce el siguiente currículum vitae (CV) del inglés al español (variedad de Argentina y Uruguay). "
        "Adapta nombres de cargos, formación académica y terminología laboral local de forma natural "
        "(por ejemplo, usa 'carrera de grado', 'secundario completo', 'monotributista', 'remuneración pretendida', etc.). "
        "Mantén intactos los nombres propios de personas, empresas, instituciones, fechas y ciudades.\n\n"
        "Además, analiza el nombre del candidato en el CV y determina su género ('M' para masculino, 'F' para femenino). "
        "Si el nombre es ambiguo, realiza tu mejor estimación basada en el nombre de pila.\n\n"
        "Debes responder ÚNICAMENTE con un objeto JSON válido, estructurado de la siguiente manera, sin texto adicional:\n"
        "{\n"
        '  "translated_cv": "texto completo del CV traducido",\n'
        '  "gender": "M o F"\n'
        "}\n\n"
        f"TEXTO DEL CV:\n{cv_text}"
    )

    print(f"  [LLM] Traduciendo CV e infiriendo género...")
    response_text = get_chat_completion(prompt=prompt, system=system_prompt, max_tokens=2048)

    # Limpiar posibles bloques de código markdown de la respuesta del LLM
    clean_response = response_text.strip()
    if clean_response.startswith("```json"):
        clean_response = clean_response[7:]
    if clean_response.endswith("```"):
        clean_response = clean_response[:-3]
    clean_response = clean_response.strip()

    try:
        data = json.loads(clean_response)
        translated_cv = data["translated_cv"]
        gender = data["gender"].upper().strip()
        if gender not in ["M", "F"]:
            gender = "M"
    except Exception as e:
        print(f"  [WARN] Error decodificando respuesta JSON del LLM: {e}. Usando fallback.")
        # Fallback si falla el parseo JSON
        translated_cv = response_text
        gender = "M"

    cache[text_hash] = {
        "translated_cv": translated_cv,
        "gender": gender
    }
    save_translation_cache(cache)
    return translated_cv, gender


# ── Descarga del Dataset Público ─────────────────────────────────────────────

def download_sample(sample_type: str, idx: int) -> dict:
    """Descarga un ejemplo desde Hugging Face usando caché local."""
    cache_path = CACHE_JSON_DIR / f"{sample_type}_{idx}.json"
    if cache_path.exists():
        with open(cache_path, "r", encoding="utf-8") as f:
            return json.load(f)

    url = f"https://huggingface.co/datasets/netsol/resume-score-details/raw/main/{sample_type}_{idx}.json"
    r = requests.get(url)
    if r.status_code != 200:
        raise RuntimeError(f"Error {r.status_code} descargando {url}")

    data = r.json()
    with open(cache_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return data


# ── Simulación de Tiempos C0 y Edades ────────────────────────────────────────

def get_simulated_c0_time(label: str) -> float:
    if label == "APTO":
        # Entre 10 y 20 minutos (600 - 1200 s)
        return round(random.uniform(600, 1200), 1)
    else:
        # Entre 5 y 12 minutos (300 - 700 s)
        return round(random.uniform(300, 700), 1)


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("SISTAC — Preparación del Dataset de Validación Externa")
    print("=" * 60)

    # 1. Cargar caché de traducción
    translation_cache = load_translation_cache()

    # 2. Descargar 75 match y 75 mismatch
    print("\n[1/4] Descargando muestras de Hugging Face...")
    samples = []
    
    # 75 Matches
    for i in tqdm(range(75), desc="Matches"):
        try:
            data = download_sample("match", i)
            data["_label"] = "APTO"
            samples.append(data)
        except Exception as e:
            print(f"  [ERROR] No se pudo descargar match_{i}: {e}")
            
    # 75 Mismatches
    for i in tqdm(range(75), desc="Mismatches"):
        try:
            data = download_sample("mismatch", i)
            data["_label"] = "NO_APTO"
            samples.append(data)
        except Exception as e:
            print(f"  [ERROR] No se pudo descargar mismatch_{i}: {e}")

    print(f"Descargados {len(samples)} registros en total.")

    # 3. Procesar y traducir JDs únicas
    print("\n[2/4] Mapeando y traduciendo Job Descriptions únicas...")
    unique_jds = {}
    jd_counter = 1
    
    # Primero identificamos las JDs únicas para no traducir el mismo texto varias veces
    for sample in samples:
        jd_original = sample["input"]["job_description"]
        if jd_original not in unique_jds:
            jd_id = f"JD_EXT_{jd_counter:03d}"
            unique_jds[jd_original] = jd_id
            jd_counter += 1

    # Traducir y guardar cada JD única
    for jd_orig, jd_id in tqdm(unique_jds.items(), desc="Traduciendo JDs"):
        jd_translated = translate_jd(jd_orig, translation_cache)
        # Extraer cargo/título básico del texto o usar un default
        first_line = jd_orig.split("\n")[0]
        title = first_line.replace("Job Title:", "").replace("Title:", "").strip()
        if not title or len(title) > 50:
            title = "Posición Técnica Externa"

        jd_text_formatted = (
            f"CARGO: {title}\n"
            f"EMPRESA: Compañía de Validación Externa S.A.\n\n"
            f"{jd_translated}"
        )
        jd_path = JDS_EXT_DIR / f"{jd_id}.txt"
        jd_path.write_text(jd_text_formatted, encoding="utf-8")

    # 4. Procesar y traducir CVs, e imputar metadatos
    print("\n[3/4] Traduciendo CVs e imputando metadatos...")
    
    ground_truth_rows = []
    c0_times_rows = []
    
    evaluators = ["EVAL_01", "EVAL_02", "EVAL_03"]
    age_ranges = ["23-35", "36-45", "46-58"]

    for idx, sample in enumerate(tqdm(samples, desc="Procesando CVs"), start=1):
        cv_id = f"CV_EXT_{idx:03d}"
        label = sample["_label"]
        
        # Obtener JD_ID
        jd_orig = sample["input"]["job_description"]
        jd_id = unique_jds[jd_orig]

        # Traducir CV y detectar género
        cv_orig = sample["input"]["resume"]
        cv_translated, gender = translate_cv_and_detect_gender(cv_orig, translation_cache)

        # Guardar archivo de CV traducido
        cv_path = CVS_EXT_DIR / f"{cv_id}.txt"
        cv_path.write_text(cv_translated, encoding="utf-8")

        # Imputar Edad (distribuida balanceada)
        age_group = age_ranges[(idx - 1) % 3]

        # Extraer Score macro y mapear a base 100
        score_10 = 5.0  # default
        try:
            score_10 = sample["output"]["scores"]["aggregated_scores"]["macro_scores"]
        except KeyError:
            pass
        score_100 = round(score_10 * 10)
        # Asegurar concordancia aproximada con la etiqueta original
        if label == "APTO" and score_100 < 60:
            score_100 = random.randint(65, 85)
        elif label == "NO_APTO" and score_100 >= 60:
            score_100 = random.randint(20, 55)

        # Ground Truth row
        ground_truth_rows.append({
            "cv_id": cv_id,
            "jd_id": jd_id,
            "expected_label": label,
            "expected_score": score_100,
            "group_gender": gender,
            "group_age": age_group,
            "eval_source": "dataset_publico_traducido"
        })

        # C0 Time row
        t = get_simulated_c0_time(label)
        c0_times_rows.append({
            "cv_id": cv_id,
            "jd_id": jd_id,
            "time_seconds": t,
            "decision": label,
            "evaluator_id": random.choice(evaluators)
        })

    # 5. Guardar archivos Ground Truth y Tiempos C0
    print("\n[4/4] Guardando archivos CSV consolidados...")
    
    gt_path = GOLD_EXT_DIR / "ground_truth.csv"
    gt_fields = ["cv_id", "jd_id", "expected_label", "expected_score", "group_gender", "group_age", "eval_source"]
    with open(gt_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=gt_fields)
        writer.writeheader()
        writer.writerows(ground_truth_rows)
    print(f"  -> Guardado Ground Truth en: {gt_path} ({len(ground_truth_rows)} filas)")

    c0_path = GOLD_EXT_DIR / "c0_times.csv"
    c0_fields = ["cv_id", "jd_id", "time_seconds", "decision", "evaluator_id"]
    with open(c0_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=c0_fields)
        writer.writeheader()
        writer.writerows(c0_times_rows)
    print(f"  -> Guardado Tiempos C0 en: {c0_path} ({len(c0_times_rows)} filas)")

    print("\n" + "=" * 60)
    print("Dataset de Validación Externa completado exitosamente.")
    print("Para activar este dataset en tus experimentos, agrega la siguiente línea a tu archivo .env:")
    print("  USE_EXTERNAL_DATA=true")
    print("=" * 60)


if __name__ == "__main__":
    main()
