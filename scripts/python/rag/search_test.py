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


def generate_embedding(text: str):
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )

    return response.data[0].embedding


def search_documents(query_text: str):

    embedding = generate_embedding(query_text)

    url = (
        f"{AZURE_SEARCH_ENDPOINT}/indexes/"
        f"{AZURE_SEARCH_INDEX}/docs/search?api-version=2024-07-01"
    )

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
                "k": 3
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    print("Status:", response.status_code)

    results = response.json()

    print("\nRESULTADOS:\n")

    for doc in results["value"]:
        print("ID:", doc["id"])
        print("Texto:", doc["chunk_text"])
        print("Score:", doc["@search.score"])
        print("-" * 50)


if __name__ == "__main__":

    query = "Busco experiencia en SAP y presupuestación financiera"

    search_documents(query)