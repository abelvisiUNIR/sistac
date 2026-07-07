import os
import sys
import time
from dotenv import load_dotenv
from google.cloud import discoveryengine_v1beta as discoveryengine
from google.api_core.client_options import ClientOptions

load_dotenv()

project_id = os.getenv("GCP_PROJECT_ID", "bps-process-gen")
location = os.getenv("GCP_LOCATION", "global")
datastore_id = os.getenv("GCP_DATA_STORE_ID", "sistac-cvs-datastore")
engine_id = os.getenv("GCP_SEARCH_APP_ID_EXTERNAL", "sistac-search-app-external")

print(f"Project ID: {project_id}")
print(f"Location: {location}")
print(f"Datastore ID: {datastore_id}")
print(f"Engine ID: {engine_id}")

client_options = (ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com") 
                  if location != "global" else None)

ds_client = discoveryengine.DataStoreServiceClient(client_options=client_options)
engine_client = discoveryengine.EngineServiceClient(client_options=client_options)

# 1. Delete Engine/App if exists
print("\nDeleting Engine...")
try:
    engine_name = f"projects/{project_id}/locations/{location}/collections/default_collection/engines/{engine_id}"
    operation = engine_client.delete_engine(name=engine_name)
    print(f"Waiting for Engine deletion... Operation: {operation.operation.name}")
    operation.result()
    print("Engine deleted successfully.")
except Exception as e:
    print(f"Engine might not exist or failed to delete: {e}")

# 2. Delete Data Store if exists
print("\nDeleting Data Store...")
try:
    ds_name = f"projects/{project_id}/locations/{location}/collections/default_collection/dataStores/{datastore_id}"
    operation = ds_client.delete_data_store(name=ds_name)
    print(f"Waiting for Data Store deletion... Operation: {operation.operation.name}")
    operation.result()
    print("Data Store deleted successfully.")
except Exception as e:
    print(f"Data Store might not exist or failed to delete: {e}")

# Wait a few seconds for propagation
time.sleep(5)

# 3. Create Data Store with NO_CONTENT
print("\nRecreating Data Store with NO_CONTENT...")
try:
    parent = ds_client.collection_path(project_id, location, "default_collection")
    
    data_store = discoveryengine.DataStore(
        display_name=datastore_id,
        industry_vertical=discoveryengine.IndustryVertical.GENERIC,
        solution_types=[discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH],
        content_config=discoveryengine.DataStore.ContentConfig.NO_CONTENT,
    )
    
    request = discoveryengine.CreateDataStoreRequest(
        parent=parent,
        data_store_id=datastore_id,
        data_store=data_store,
    )
    
    operation = ds_client.create_data_store(request=request)
    print(f"Waiting for Data Store creation... Operation: {operation.operation.name}")
    response = operation.result()
    print(f"Data Store created: {response.name}")
except Exception as e:
    print(f"Error creating Data Store: {e}")

# 4. Create Engine
print("\nRecreating Engine/Search App...")
try:
    parent = engine_client.collection_path(project_id, location, "default_collection")
    
    engine = discoveryengine.Engine(
        display_name=engine_id,
        solution_type=discoveryengine.SolutionType.SOLUTION_TYPE_SEARCH,
        data_store_ids=[datastore_id],
    )
    
    request = discoveryengine.CreateEngineRequest(
        parent=parent,
        engine_id=engine_id,
        engine=engine,
    )
    
    operation = engine_client.create_engine(request=request)
    print(f"Waiting for Engine creation... Operation: {operation.operation.name}")
    response = operation.result()
    print(f"Engine created: {response.name}")
except Exception as e:
    print(f"Error creating Engine: {e}")

print("\nDone recreating GCP resources!")
