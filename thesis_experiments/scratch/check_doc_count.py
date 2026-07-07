import os
from dotenv import load_dotenv
from google.cloud import discoveryengine_v1beta as discoveryengine

load_dotenv()

project_id = os.getenv("GCP_PROJECT_ID", "bps-process-gen")
location = os.getenv("GCP_LOCATION", "global")
datastore_id = os.getenv("GCP_DATA_STORE_ID", "sistac-cvs-datastore-v2")

print(f"Checking document count for datastore: {datastore_id}")

try:
    client = discoveryengine.DocumentServiceClient()
    parent = client.branch_path(
        project=project_id,
        location=location,
        data_store=datastore_id,
        branch="default_branch",
    )
    docs = list(client.list_documents(parent=parent))
    print(f"Total documents found in index: {len(docs)}")
except Exception as e:
    print(f"Error checking document count: {e}")
