import os
from fastapi import HTTPException, APIRouter
router = APIRouter()
from pymilvus import (
    connections,
    utility,
    Collection,
)

MILVUS_ALIAS = "default"
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"

@router.on_event("startup")
def startup():
    connections.connect(MILVUS_ALIAS, host=MILVUS_HOST, port=MILVUS_PORT)  # Conexion Global
    print("Milvus Conectado",flush=True)
    
def list_collections():
    return utility.list_collections()

def connect_collection_securely(collect:str):
    colecciones_existentes = list_collections()
    print('colecciones existentes', colecciones_existentes, flush=True)
    if collect in colecciones_existentes:
        collection = Collection(collect)
        if str(utility.load_state(collect)) == "NotLoad":
            collection.load()
        return collection
    else: raise HTTPException(status_code=404, detail=f"Collection '{collect}' not found")