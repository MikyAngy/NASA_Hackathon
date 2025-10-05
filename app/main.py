from fastapi import FastAPI, HTTPException, WebSocket, UploadFile
from pydantic import BaseModel
from models import langchain_llm as llm
from models import gemini
from milvus.connection import connect_collection_securely, router as connection_router
from milvus.loader import get_url_content
from milvus.splitter import chunk_documents 
from milvus.embedding import embeddings, EMBEDDING_MODEL
import datetime
from utils.helpers import leer_columnas_csv

app = FastAPI()

app.include_router(connection_router)

def semantic_search(prompt):
    query_vector = embeddings.embed_query(prompt)
    print('EMBEDDING GENERADO',flush=True)
    # Cambiamos la métrica a "COSINE". La interpretación del score cambia.
    search_params = {
        "metric_type": "COSINE",  # <--- LÍNEA MODIFICADA
        "params": {"nprobe": 64},
    }

    collection = connect_collection_securely('NASA_data_2')

    # --- 5. Ejecutar la Búsqueda ---
    print("\nRealizando búsqueda semántica con métrica COSINE...")
    results = collection.search(
        data=[query_vector],
        anns_field="embedding",
        param=search_params,
        limit=5,
        output_fields=["content"]
    )

    # --- 6. Procesar y Devolver los Resultados ---
    # formatted_results = []
    hits = results[0]
    print(f"Se encontraron {len(hits)} resultados.")
    return [
        hit.entity.get('content')
        for hit in hits
    ]

class requestLlmResponse(BaseModel):
    prompt: str
    
@app.websocket("/llm_response")
async def llm_response(websocket: WebSocket):
    await websocket.accept()
    while True:
        prompt = await websocket.receive_text()
        print('PROMPT DEL USUARIO',flush=True)
        knowledge = semantic_search(prompt)
        print('KNOWLEDGE',knowledge,flush=True)
        chunks = gemini.gemini_generate(prompt,knowledge)
        print('CHUNKS DEVUELTOS',chunks,flush=True)
        for chunk in chunks:
            await websocket.send_text(chunk.text)    

class requestDataIngestion(BaseModel):
    url: str

@app.post("/data_ingestion")
def data_ingestion(request: requestDataIngestion):
    collection = connect_collection_securely('NASA_data_2')
    print('[DEBUG] Milvus Collection Loaded', flush=True)
    # Extraer contenido del documento
    titulos, links = leer_columnas_csv('./utils/SB_publication_PMC.csv')
    # print('CANTIDAD URLS EXPORTADAS: ', type(data))
    n = 308  # por ejemplo, comenzar desde el índice 3
    for idx, (title, url) in enumerate(zip(titulos[n:], links[n:]), start=n):
        print('*** ARTICULO ',idx+1)
        documents = get_url_content({"url":url})
        print('[DEBUG] Document Loaded', flush=True)
        #Separar documento extenso en partes mas pequeñas
        chunks = chunk_documents(documents)
        print('[DEBUG] Document Splitted', flush=True)
        # Prepara los datos para la inserción
        data_to_insert = []
        for chunk in chunks:
            # Genera el embedding para el texto del chunk
            embedding_vector = embeddings.embed_query(chunk.page_content)
            
            # Crea la fila de datos para insertar
            data_to_insert.append({
                "embedding": embedding_vector,
                "title": title,
                "content": chunk.page_content
            })
        # Inserta los datos en la colección de Milvus
        mr = collection.insert(data_to_insert)
        print('[DEBUG] Data Inserted', flush=True)

    return {'done':True}