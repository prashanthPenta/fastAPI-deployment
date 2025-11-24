from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from azure.cosmos import CosmosClient
import certifi
import os
from dotenv import load_dotenv



endpoint = os.getenv("COSMOS_ENDPOINT")
key = os.getenv("COSMOS_KEY")
database_name = os.getenv("COSMOS_DATABASE")
container_name = os.getenv("COSMOS_CONTAINER")

# Initialize Cosmos client
client = CosmosClient(endpoint, credential=key, connection_verify=certifi.where())
database = client.get_database_client(database_name)
container = database.get_container_client(container_name)

app = FastAPI()

class Account(BaseModel):
    entity_type: str
    id: int
    name: str
    parent_entity: str
    parent_id: int

@app.post("/accounts")
def create_account(account: Account):
    container.create_item(account.dict())
    return {"message": "Account created successfully"}

@app.get("/accounts")
def get_accounts():
    query = "SELECT * FROM c"
    accounts = list(container.query_items(query=query, enable_cross_partition_query=True))
    return accounts

@app.get("/accounts/{account_id}")
def get_account(account_id: str):
    try:
        account = container.read_item(item=account_id, partition_key=account_id)
        return account
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

@app.put("/accounts/{account_id}")
def update_account(account_id: str, account: Account):
    container.upsert_item(account.dict())
    return {"message": "Account updated successfully"}

@app.delete("/accounts/{account_id}")
def delete_account(account_id: str):
    try:
        container.delete_item(item=account_id, partition_key=account_id)
        return {"message": "Account deleted successfully"}
    except Exception:
        raise HTTPException(status_code=404, detail="Account not found")

