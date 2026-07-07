import requests
import os
from dotenv import load_dotenv

load_dotenv()
endpoint = os.getenv('AZURE_SEARCH_ENDPOINT')
key = os.getenv('AZURE_SEARCH_KEY')
headers = {'Content-Type': 'application/json', 'api-key': key}

url = f'{endpoint}/indexes?api-version=2024-07-01'
r = requests.get(url, headers=headers)

if r.status_code == 200:
    indexes = r.json().get('value', [])
    print(f"Encontrados {len(indexes)} índices en Azure AI Search:")
    for index in indexes:
        name = index['name']
        c_url = f'{endpoint}/indexes/{name}/docs/$count?api-version=2024-07-01'
        cr = requests.get(c_url, headers=headers)
        docs_count = cr.text if cr.status_code == 200 else "Error"
        print(f"- Índice: {name} | Documentos/Chunks: {docs_count}")
else:
    print(f"Error {r.status_code}: {r.text}")
