import os
from dotenv import load_dotenv
from openai import OpenAI
import requests

load_dotenv()

AZURE_SEARCH_ENDPOINT = os.getenv("AZURE_SEARCH_ENDPOINT")
AZURE_SEARCH_KEY = os.getenv("AZURE_SEARCH_KEY")
AZURE_SEARCH_INDEX = os.getenv("AZURE_SEARCH_INDEX")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

client = OpenAI(api_key=OPENAI_API_KEY)

chunks = [
    {
        "id": "cv001_chunk001",
        "cv_text": "Candidato con experiencia en Python, machine learning, análisis de datos y modelos predictivos.",
        "job_text": "Cargo requiere experiencia en ciencia de datos, Python, machine learning y análisis estadístico.",
        "chunk_text": "Experiencia en Python, machine learning, análisis de datos y modelos predictivos."
    },
    {
        "id": "cv001_chunk002",
        "cv_text": "Experiencia en SAP BPC, presupuestación financiera, planificación y reportes corporativos.",
        "job_text": "Cargo requiere conocimientos de planificación financiera, SAP y presupuestación.",
        "chunk_text": "Experiencia en SAP BPC, presupuestación financiera, planificación y reportes corporativos."
    },
    {
        "id": "cv002_chunk001",
        "cv_text": "Candidato con experiencia en ventas, atención al cliente y gestión comercial.",
        "job_text": "Cargo requiere ciencia de datos, Python y machine learning.",
        "chunk_text": "Experiencia en ventas, atención al cliente y gestión comercial."
    }
]


def generate_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    return response.data[0].embedding


def upload_documents(documents):
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


def main():
    documents = []

    for chunk in chunks:
        print(f"Generando embedding para {chunk['id']}...")
        embedding = generate_embedding(chunk["chunk_text"])

        documents.append({
            **chunk,
            "embedding": embedding
        })

    print("Subiendo documentos a Azure AI Search...")
    upload_documents(documents)

    print("Proceso terminado.")


if __name__ == "__main__":
    main()