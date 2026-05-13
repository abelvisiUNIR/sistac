import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
import requests

# Permite importar chunking.py desde la misma carpeta
CURRENT_DIR = Path(__file__).resolve().parent
sys.path.append(str(CURRENT_DIR))

from chunking import chunk_text


load_dotenv()

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

BASE_DIR = Path(__file__).resolve().parents[3]
CV_DIR = BASE_DIR / "data" / "raw" / "cvs"
JOB_DIR = BASE_DIR / "data" / "raw" / "jobs"


def read_txt(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def generate_embedding(text: str) -> list[float]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def upload_documents(documents: list[dict]) -> None:
    url = f"{AZURE_SEARCH_ENDPOINT}/indexes/{AZURE_SEARCH_INDEX}/docs/index?api-version=2024-07-01"

    headers = {
        "Content-Type": "application/json",
        "api-key": AZURE_SEARCH_KEY
    }

    payload = {
        "value": [
            {
                "@search.action": "upload",
                **doc
            }
            for doc in documents
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    print("Status:", response.status_code)
    print("Response:", response.text)


def build_documents() -> list[dict]:
    documents = []

    cv_files = sorted(CV_DIR.glob("*.txt"))
    job_files = sorted(JOB_DIR.glob("*.txt"))

    for cv_file in cv_files:
        cv_id = cv_file.stem
        cv_text = read_txt(cv_file)

        for job_file in job_files:
            job_id = job_file.stem
            job_text = read_txt(job_file)

            combined_text = f"""
            CV:
            {cv_text}

            DESCRIPCION DEL CARGO:
            {job_text}
            """

            chunks = chunk_text(combined_text, chunk_size=800, overlap=120)

            for idx, chunk in enumerate(chunks, start=1):
                chunk_id = f"{cv_id}_{job_id}_chunk_{idx:03d}"

                print(f"Generando embedding: {chunk_id}")

                embedding = generate_embedding(chunk)

                documents.append({
                    "id": chunk_id,
                    "cv_text": cv_text,
                    "job_text": job_text,
                    "chunk_text": chunk,
                    "embedding": embedding
                })

    return documents


def main():
    print("Leyendo corpus piloto...")
    print(f"CV_DIR: {CV_DIR}")
    print(f"JOB_DIR: {JOB_DIR}")

    documents = build_documents()

    print(f"Total documentos/chunks a subir: {len(documents)}")

    if not documents:
        print("No se encontraron documentos para indexar.")
        return

    upload_documents(documents)

    print("Indexación del corpus piloto finalizada.")


if __name__ == "__main__":
    main()