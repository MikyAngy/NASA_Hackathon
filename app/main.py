from typing import Optional
from fastapi import FastAPI, HTTPException, WebSocket, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from models import langchain_llm as llm
from models import gemini
from milvus.connection import connect_collection_securely, router as connection_router
from milvus.loader import get_url_content
from milvus.splitter import chunk_documents 
from milvus.embedding import embeddings, EMBEDDING_MODEL
import datetime
from utils.helpers import leer_columnas_csv, parse_json_string
from collections import defaultdict

app = FastAPI()

app.include_router(connection_router)

# Lista de orígenes permitidos (tu frontend de React)
# Asegúrate de que el puerto sea el correcto (3000, 5173, etc.)
origins = [
    "http://localhost:5173", # Puerto común para Vite
    "http://127.0.0.1:5173",
]

# --- AÑADE ESTE CÓDIGO ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Permite los orígenes especificados
    allow_credentials=True, # Permite cookies y credenciales
    allow_methods=["*"],    # Permite todos los métodos (GET, POST, etc.)
    allow_headers=["*"],    # Permite todos los encabezados
)
# -------------------------

def semantic_search(prompt,limit=10):
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
        limit=limit,
        output_fields=["content","title"]
    )

    # --- 6. Procesar y Devolver los Resultados ---
    hits = results[0]
    print(f"Se encontraron {len(hits)} resultados.")
    # return [
    #     hit.entity.get('content')
    #     for hit in hits
    # ]
    return hits

def contar_chunks_por_titulo(resultados_milvus: list) -> dict:
    """
    Procesa los resultados de una búsqueda en Milvus para contar cuántos chunks
    pertenecen a cada título único.

    Args:
        resultados_milvus: El objeto de resultados devuelto por collection.search().

    Returns:
        Un diccionario mapeando cada título al número de chunks encontrados.
        Ej: {'Título A': 2, 'Título B': 1, 'Título C': 2}
    """
    # Usamos defaultdict para simplificar el conteo. Si una clave no existe,
    # la inicializa con un valor de 0 (gracias a int).
    conteo_de_titulos = defaultdict(int)

    # Los resultados de la búsqueda están en el primer elemento de la lista
    if not resultados_milvus:
        return {}
        
    # Iteramos sobre cada resultado (hit)
    for hit in resultados_milvus:
        # Extraemos el título de la entidad del resultado
        titulo = hit.entity.get('title')
        
        # Si el título existe, incrementamos su contador en el diccionario
        if titulo:
            conteo_de_titulos[titulo] += 1
            
    return dict(conteo_de_titulos) # Convertimos a un dict normal para la salida

class requestAnalyzeArticle(BaseModel):
    title:Optional[str]=None,
    url:Optional[str]=None

@app.post("/analyze_article")
def analyze_article(request:requestAnalyzeArticle):
    if request.title:  
        url = leer_columnas_csv('./utils/SB_publication_PMC.csv',title=request.title)
        # print('[DEBUG] Link encontrado por titulo',url,flush=True)
    else: url = request.url
    documents = get_url_content({"url":url}) 

    page_contents = "\n".join([doc.page_content for doc in documents])
    # print('[DEBUG] Contenido de las paginas como string',page_contents,flush=True)

    full_prompt = (f"""
    # ROL Y OBJETIVO
    Actúa como un analizador de contenido que debe cuantificar el enfoque de un texto científico. Tu objetivo es leer el siguiente artículo y estimar, en términos de porcentaje, cuánto de su contenido y discusión se dedica a cada una de las siguientes tres categorías.

    # DEFINICIÓN DE CATEGORÍAS
    1.  **Progreso Científico:** Contenido que presenta nuevos hallazgos, confirma hipótesis, o introduce métodos novedosos.
    2.  **Lagunas de Conocimiento:** Contenido que menciona explícitamente limitaciones, preguntas sin resolver, o áreas para futura investigación.
    3.  **Consenso y Desacuerdo:** Contenido que cita, compara o contrasta los hallazgos del artículo con los de otros estudios previos.

    # INSTRUCCIONES
    1.  Lee el artículo completo.
    2.  Asigna un porcentaje a cada una de las tres categorías basándote en la inclusion de cada una de ellas en el artículo.
    3.  Los porcentajes de cada categoria son independientes.
    4.  Proporciona una justificación muy breve para cada porcentaje asignado.
    5.  Responde únicamente con el objeto JSON solicitado, limpio y serializable

    **Artículo**
    ---
    {page_contents}
    ---

    **JSON**"""
    +
    """
    {
        "analisis_cuantitativo": {
            "progreso_cientifico": {
            "porcentaje": 0,
            "justificacion": "Explicación de por qué se asignó este porcentaje."
            },
            "lagunas_de_conocimiento": {
            "porcentaje": 0,
            "justificacion": "Explicación de por qué se asignó este porcentaje."
            },
            "consenso_y_desacuerdo": {
            "porcentaje": 0,
            "justificacion": "Explicación de por qué se asignó este porcentaje."
            }
        }
    }
    """)

    # print('[DEBUG] Prompt formateado',full_prompt,flush=True)

    chunks = gemini.gemini_generate(full_prompt)
    # print('CHUNKS DEVUELTOS',chunks,flush=True)
    finall_answer = ""
    for chunk in chunks:
        finall_answer += chunk.text
        # print(chunk.text,end="",flush=True)
        # await websocket.send_text(chunk.text)
    
    # print('RESPUESTA FINAL',finall_answer,flush=True)
    return parse_json_string(finall_answer)

class requestLlmResponse(BaseModel):
    prompt: str

@app.post("/data_ingestion")
def article_search(request: requestLlmResponse):
    knowledge = semantic_search(request.prompt, 4)
    # print('KNOWLEDGE',knowledge,flush=True)
    return contar_chunks_por_titulo(knowledge)
    # print("TITULOS RELEVANTES",relevant_docs,flush=True)
    
@app.websocket("/llm_response")
async def llm_response(websocket: WebSocket):
    await websocket.accept()
    while True:
        prompt = await websocket.receive_text()
        print('PROMPT DEL USUARIO',flush=True)
        knowledge = semantic_search(prompt)
        # print('KNOWLEDGE',knowledge,flush=True)
        relevant_docs = contar_chunks_por_titulo(knowledge)
        print("TITULOS RELEVANTES",relevant_docs,flush=True)
        content = [
            hit.entity.get('content')
            for hit in knowledge
        ]
        full_prompt = f"""
        Con el contexto proporcionado, responde acertivamente la pregunta del usuario.

        **Contexto Proporcionado (Knowledge):**
        ---
        {content}
        ---

        **Pregunta del Usuario:**
        {prompt}
        """
        # print('CONTENT',content,flush=True)
        chunks = gemini.gemini_generate(full_prompt)
        # print('CHUNKS DEVUELTOS',chunks,flush=True)
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