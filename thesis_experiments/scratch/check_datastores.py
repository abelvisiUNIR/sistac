import os
from dotenv import load_dotenv
from google.cloud import discoveryengine_v1beta as discoveryengine

load_dotenv()

project_id = os.getenv("GCP_PROJECT_ID", "bps-process-gen")
location = os.getenv("GCP_LOCATION", "global")

print(f"Project ID: {project_id}")
print(f"Location: {location}")
print(f"Credentials Env: {os.getenv('GOOGLE_APPLICATION_CREDENTIALS')}")

client = discoveryengine.DataStoreServiceClient()
engine_client = discoveryengine.EngineServiceClient()

for location in ["global", "us", "us-central1", "europe-west1"]:
    print(f"\nChecking location: {location}")
    parent = f"projects/{project_id}/locations/{location}/collections/default_collection"


    print(f"Listing data stores in parent: {parent}")
    try:
        request = discoveryengine.ListDataStoresRequest(parent=parent)
        page_result = client.list_data_stores(request=request)
        datastores = list(page_result)
        print(f"Found {len(datastores)} data stores:")
        for ds in datastores:
            print(f" - ID: {ds.name.split('/')[-1]}, Name: {ds.display_name}")
    except Exception as e:
        print(f"Error listing data stores: {e}")

    print("Listing search engines/apps:")
    try:
        engine_client = discoveryengine.EngineServiceClient()
        request = discoveryengine.ListEnginesRequest(parent=parent)
        page_result = engine_client.list_engines(request=request)
        engines = list(page_result)
        print(f"Found {len(engines)} engines/apps:")
        for eng in engines:
            print(f" - ID: {eng.name.split('/')[-1]}, Name: {eng.display_name}")
    except Exception as e:
        print(f"Error listing engines: {e}")

