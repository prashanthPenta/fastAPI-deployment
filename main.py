from fastapi import FastAPI
from azure.cosmos import CosmosClient
import certifi
import os

app = FastAPI()

def get_container():
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    database_name = os.getenv("COSMOS_DATABASE")
    container_name = os.getenv("COSMOS_CONTAINER")

    if not all([endpoint, key, database_name, container_name]):
        raise RuntimeError("Missing Cosmos DB environment variables")

    client = CosmosClient(endpoint, credential=key, connection_verify=certifi.where())
    database = client.get_database_client(database_name)
    return database.get_container_client(container_name)

# Initialize once
container = get_container()

@app.get("/test-cosmos")
def test_cosmos():
    try:
        # Try a simple query
        query = "SELECT TOP 1 * FROM c"
        items = list(container.query_items(query=query, enable_cross_partition_query=True))
        return {"status": "success", "items": items}
    except Exception as e:
        return {"status": "error", "detail": str(e)}
