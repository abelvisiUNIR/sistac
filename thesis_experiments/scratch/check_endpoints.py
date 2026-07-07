import os
from dotenv import load_dotenv
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.api_core.client_options import ClientOptions

load_dotenv()

project_id = os.getenv("GCP_PROJECT_ID", "bps-process-gen")

locations = ["global", "us", "eu"]

for loc in locations:
    print(f"\nChecking location: {loc}")
    if loc == "global":
        endpoint = "discoveryengine.googleapis.com"
    else:
        endpoint = f"{loc}-discoveryengine.googleapis.com"
        
    client_options = ClientOptions(api_endpoint=endpoint)
    
    try:
        client = discoveryengine.DataStoreServiceClient(client_options=client_options)
        parent = f"projects/{project_id}/locations/{loc}/collections/default_collection"
        request = discoveryengine.ListDataStoresRequest(parent=parent)
        datastores = list(client.list_data_stores(request=request))
        print(f"[{loc}] Found {len(datastores)} data stores:")
        for ds in datastores:
            print(f" - ID: {ds.name.split('/')[-1]}, Name: {ds.display_name}")
    except Exception as e:
        print(f"[{loc}] Error listing data stores: {e}")

    try:
        engine_client = discoveryengine.EngineServiceClient(client_options=client_options)
        parent = f"projects/{project_id}/locations/{loc}/collections/default_collection"
        request = discoveryengine.ListEnginesRequest(parent=parent)
        engines = list(engine_client.list_engines(request=request))
        print(f"[{loc}] Found {len(engines)} engines/apps:")
        for eng in engines:
            print(f" - ID: {eng.name.split('/')[-1]}, Name: {eng.display_name}")
    except Exception as e:
        print(f"[{loc}] Error listing engines: {e}")
