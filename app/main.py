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
import json
from utils.helpers import leer_columnas_csv, parse_json_string
from collections import defaultdict
from models.generate_chart import _chart_tool_entrypoint  # o chart_tool.func
import traceback

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

def procesar_articulos_desde_milvus(resultados_milvus: list) -> dict:
    """
    Agrupa chunks por título, cuenta cuántos hay por cada uno, y genera una
    categoría y resumen para cada artículo único usando una API de LLM.

    Args:
        resultados_milvus: Una lista de resultados de búsqueda de Milvus.

    Returns:
        Un diccionario con el análisis de cada artículo único.
    """
    if not resultados_milvus:
        return {}

    # Paso 1: Agrupar contenido y contar chunks por título
    articulos_agrupados = defaultdict(lambda: {"chunks": [], "count": 0})
    for hit in resultados_milvus:
        titulo = hit.entity.get('title')
        if titulo: # Asegurarse de que el título no sea nulo
            articulos_agrupados[titulo]["chunks"].append(hit.entity.get('content', ''))
            articulos_agrupados[titulo]["count"] += 1

    # Paso 2: Procesar cada artículo único con el LLM
    resultado_final = {}
    for titulo, data in articulos_agrupados.items():
        contenido_completo = "\n---\n".join(data["chunks"])
        
        full_prompt = f"""
        Recibirás un título de un artículo de divulgación de la NASA y su contenido.
        Tus objetivos son:
        1. Darme un nuevo titulo de maximo dos palabras que describa al articulo lo mejor posible.
        2. Darme la categoría mas adecuada del articulo. Implicitamente sabes que va a ser de Astrobiologia, asi que categoriza a un nivel mas bajo.
        3. Darme un resumen conciso de lo más importante del artículo.
        
        La salida debe ser estrictamente un diccionario JSON como este: {{"littletitle": "...", "category": "...", "summarize": "..."}}

        **Título del artículo:**
        {titulo}

        **Contenido del artículo (Knowledge):**
        ---
        {contenido_completo}
        ---
        """
        
        try:
            # Hacemos la llamada a la API
            respuesta_llm_str = ""
            chunks = gemini.gemini_generate(full_prompt)
            # for chunk in chunks:
            #     respuesta_llm_str += chunk.text
            # Parseamos la respuesta JSON del LLM
            analisis = parse_json_string(chunks.text)
            # Construimos la entrada final para este título
            resultado_final[titulo] = {
                "littletitle": analisis.get('littletitle','N/A'),
                "count": data["count"],
                "category": analisis.get("category", "N/A"),
                "summarize": analisis.get("summarize", "N/A")
            }
        except (json.JSONDecodeError, TypeError) as e:
            # traceback.print_exc()
            print(f"Error al procesar el artículo '{titulo}': {e}")
            # Opcional: añadir una entrada de error al resultado
            resultado_final[titulo] = {
                "littletitle": "Error al procesar titulo nuevo",
                "count": data["count"],
                "category": "Error de procesamiento",
                "summarize": "No se pudo generar el resumen."
            }
            
    return resultado_final

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

@app.post("/article_search")
def article_search(request: requestLlmResponse):
    knowledge = semantic_search(request.prompt)
    # print('KNOWLEDGE',knowledge,flush=True)
    return procesar_articulos_desde_milvus(knowledge)
    # print(asdasd,'AKANSLKJNDAKJSNDJLA',flush=True)
    # print("TITULOS RELEVANTES",relevant_docs,flush=True)
    
@app.websocket("/llm_response")
async def llm_response(websocket: WebSocket):
    await websocket.accept()
    while True:
        prompt = await websocket.receive_text()
        print('PROMPT DEL USUARIO',flush=True)
        knowledge = semantic_search(prompt)
        # print('KNOWLEDGE',knowledge,flush=True)
        content = [
            hit.entity.get('content')
            for hit in knowledge
        ]
        full_prompt = f"""
        Toma el contexto proporcionado como base principal para responder acertivamente la pregunta del usuario.
        Si el contexto no contiene información relevante a la pregunta del usuario, intenta responder de otras fuentes.

        **Contexto Proporcionado (Knowledge):**
        ---
        {content}
        ---

        **Pregunta del Usuario:**
        {prompt}
        """
        # print('CONTENT',content,flush=True)
        chunks = gemini.gemini_generate(full_prompt,stream=True)
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

class GenRequest(BaseModel):
    document: str = ""        # texto a leer (puede ser largo)
    user_request: str         # requerimiento del usuario (tipo de gráfico, ejes, filtros, etc.)

@app.post("/api/generate_chart")
def generate_chart(req: GenRequest):
    combined = f"DOCUMENT: {req.document}\n### USER_REQUEST: {req.user_request}"
    result_json_str = _chart_tool_entrypoint(combined)
    # devolvemos ya parsed JSON
    import json
    return json.loads(result_json_str)
