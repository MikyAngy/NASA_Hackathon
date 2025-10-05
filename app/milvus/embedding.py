from langchain_google_genai import GoogleGenerativeAIEmbeddings
import os
from dotenv import load_dotenv
import os
from fastapi import APIRouter
router = APIRouter()
load_dotenv()

VECTOR_DIM = 768
EMBEDDING_MODEL = "models/text-embedding-004"
# 2048 tokens de entrada, y para Milvus se recomienda usar un índice HNSW con la métrica de distancia IP (Producto Interno)

# Instancia el objeto de embeddings de Google, especificando el modelo.
embeddings = GoogleGenerativeAIEmbeddings(
    model=EMBEDDING_MODEL,
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

@router.get("/embed-query/")
def embed_query(query):
    return embeddings.embed_query(query)