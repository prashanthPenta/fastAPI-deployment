from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from azure.cosmos import CosmosClient
import certifi

app = FastAPI()

# Cosmos DB values
COSMOS_ENDPOINT = "https://<your-account>.documents.azure.com:443/"
COSMOS_KEY = "nHnpv76wetzKIbKD6aEjS56FlHCMbQHb1CHCKfigMXurlbRMFA0UXoRE9WsxuARHTfrOzkf62tnxACDbMwyfhw=="
COSMOS_DATABASE = "CDM"
COSMOS_CONTAINER = "ACCOUNT"

def get_container():
    client = CosmosClient(COSMOS_ENDPOINT, credential=COSMOS_KEY, connection_verify=certifi.where())
    database = client.get_database_client(COSMOS_DATABASE)
    return database.get_container_client(COSMOS_CONTAINER)

class Account(BaseModel):
    entity_type: str
    id: int
    name: str
    parent_entity: str
    parent_id: int

@app.post("/accounts")
def create_account(account: Account):
    container = get_container()
    container.create_item(account.dict())
    return {"message": "Account created successfully"}

@app.get("/accounts")
def get_accounts():
    container = get_container()
    query = "SELECT * FROM c"
    return list(container.query_items(query=query, enable_cross_partition_query=True))

@app.get("/accounts/{account_id}")
def get_account(account_id: str):
    container = get_container()
    try:
        return container.read_item(item=account_id, partition_key=account_id)
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

@app.put("/accounts/{account_id}")
def update_account(account_id: str, account: Account):
    container = get_container()
    container.upsert_item(account.dict())
    return {"message": "Account updated successfully"}

@app.delete("/accounts/{account_id}")
def delete_account(account_id: str):
    container = get_container()
    try:
        container.delete_item(item=account_id, partition_key=account_id)
        return {"message": "Account deleted successfully"}
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")
