import os
import sys
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

# 1. Create Data Store
print("\nCreating Data Store...")
try:
    ds_client = discoveryengine.DataStoreServiceClient(client_options=client_options)
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
    print(f"Waiting for Data Store creation to complete... Operation: {operation.operation.name}")
    response = operation.result()
    print(f"Data Store created: {response.name}")
except Exception as e:
    print(f"Error creating Data Store: {e}")

# 2. Create Engine
print("\nCreating Engine/Search App...")
try:
    engine_client = discoveryengine.EngineServiceClient(client_options=client_options)
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
    print(f"Waiting for Engine creation to complete... Operation: {operation.operation.name}")
    response = operation.result()
    print(f"Engine created: {response.name}")
except Exception as e:
    print(f"Error creating Engine: {e}")

print("\nDone trying to initialize GCP resources!")
