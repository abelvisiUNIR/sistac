import os
import csv
import json
from pathlib import Path

import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

BASE_DIR = Path(__file__).resolve().parents[3]
GT_PATH = BASE_DIR / "data" / "ground_truth" / "ground_truth.csv"
JOB_DIR = BASE_DIR / "data" / "raw" / "jobs"
RESULTS_DIR = BASE_DIR / "results"
RESULTS_DIR.mkdir(exist_ok=True)


def generate_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def search_chunks(cv_id: str, job_id: str, query_text: str, top_k: int = 5):
    embedding = generate_embedding(query_text)

    url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX}/docs/search?api-version=2024-07-01"

    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_SEARCH_KEY
    }

    payload = {
        "count": True,
        "select": "id,chunk_text",
        "vectorQueries": [
            {
                "kind": "vector",
                "vector": embedding,
                "fields": "embedding",
                "k": 20
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()

    results = response.json()["value"]

    pair_prefix = f"{cv_id}_{job_id}_"

    filtered = [
        doc for doc in results
        if doc["id"].startswith(pair_prefix)
    ]

    return filtered[:top_k]


def evaluate_with_llm(cv_id: str, job_id: str, job_text: str, chunks: list[dict]):
    context = "\n\n".join(
        [f"Fragmento {i+1}:\n{doc['chunk_text']}" for i, doc in enumerate(chunks)]
    )

    prompt = f"""
Eres un evaluador de preselección curricular.

Debes asignar un score de compatibilidad entre 0 y 100. La decisión final APTO/NO_APTO será calculada luego por el sistema usando la regla: score >= 70 es APTO; score < 70 es NO_APTO.

Descripción del cargo:
{job_text}

Fragmentos recuperados por RAG:
{context}

Responde únicamente en JSON válido con esta estructura:
{{
  "cv_id": "{cv_id}",
  "job_id": "{job_id}",
  "score": número entre 0 y 100,
  "justification": "explicación breve basada en la evidencia recuperada"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": "Eres un evaluador técnico de currículums. Responde solo JSON válido."},
            {"role": "user", "content": prompt}
        ],
        temperature=0
    )

    content = response.choices[0].message.content.strip()

    content = content.replace("```json", "")
    content = content.replace("```", "")
    content = content.strip()

    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return {
            "cv_id": cv_id,
            "job_id": job_id,
            "score": None,
            "decision": "ERROR",
            "justification": content
        }


def main():
    output = []

    with open(GT_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)

        for row in reader:
            cv_id = row["cv_id"]
            job_id = row["job_id"]

            job_text = (JOB_DIR / f"{job_id}.txt").read_text(encoding="utf-8")

            print(f"Evaluando {cv_id} contra {job_id}...")

            chunks = search_chunks(cv_id, job_id, job_text, top_k=5)

            result = evaluate_with_llm(cv_id, job_id, job_text, chunks)

            score = result.get("score")

            if score is not None:
                if score >= 70:
                    result["decision"] = "APTO"
                else:
                    result["decision"] = "NO_APTO"

                result["decision_rule"] = "score >= 70 => APTO; score < 70 => NO_APTO"

            result["expected_label"] = row["expected_label"]
            result["expected_score"] = row["expected_score"]

            output.append(result)

            print(result)
            print("-" * 60)

    output_path = RESULTS_DIR / "pilot_c2_results.json"

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Resultados guardados en: {output_path}")


if __name__ == "__main__":
    main()