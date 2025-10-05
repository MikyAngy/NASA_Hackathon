from langchain_community.document_loaders import (
    TextLoader,
    PyPDFLoader,
    UnstructuredFileLoader,
    CSVLoader,
    WebBaseLoader,
)
from pathlib import Path
from fastapi import APIRouter, UploadFile, HTTPException, Body
import os
import uuid
import shutil

router = APIRouter()

# Directorio para guardar archivos temporalmente
TEMP_DIR = Path("temp_uploads")
TEMP_DIR.mkdir(exist_ok=True)


# --- Endpoint para Cargar y Procesar Archivos ---
@router.post("/process-document/")
def get_document_content(file: UploadFile):
    """
    Recibe un archivo, lo guarda temporalmente y lo carga con el loader adecuado y regresa el contenido.
    """
    # Crea una ruta de archivo temporal única para evitar colisiones
    temp_file_path = TEMP_DIR / f"{uuid.uuid4()}_{file.filename}"
    
    try:
        # 1. GUARDAR EL UploadFile EN EL DISCO
        # Guarda el contenido del archivo subido en la ruta temporal
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # 2. SELECCIONAR EL LOADER ADECUADO SEGÚN LA EXTENSIÓN
        file_extension = temp_file_path.suffix.lower()
        
        if file_extension == ".txt":
            loader = TextLoader(str(temp_file_path))
        elif file_extension == ".pdf":
            loader = PyPDFLoader(str(temp_file_path))
        elif file_extension == ".csv":
            loader = CSVLoader(str(temp_file_path))
        elif file_extension in [".doc", ".docx", ".png", ".jpg", ".jpeg"]:
            # Unstructured maneja Word, imágenes (con OCR), etc.
            loader = UnstructuredFileLoader(str(temp_file_path))
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Tipo de archivo '{file_extension}' no soportado."
            )

        # 3. CARGAR EL CONTENIDO CON loader.load()
        documents = loader.load()
        
        return documents
    
    except Exception as e:
        # Si algo sale mal, devuelve un error
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        # 4. LIMPIEZA: ELIMINAR EL ARCHIVO TEMPORAL
        # Este bloque se ejecuta siempre, incluso si hay un error.
        if temp_file_path.exists():
            os.remove(temp_file_path)
            
# --- Nuevo Endpoint para Cargar desde URL ---
@router.post("/process-url/")
def get_url_content(payload: dict = Body(...)):
    """
    Recibe una URL en un JSON, la carga con WebBaseLoader y regresa el contenido
    Ejemplo de payload: {"url": "https://www.ejemplo.com"}
    """
    url = payload.get("url")
    if not url:
        raise HTTPException(status_code=400, detail="Falta la 'url' en el payload.")
        
    # 1. INICIALIZAR EL LOADER PARA URL
    loader = WebBaseLoader(url)
    
    # 2. CARGAR Y CHUNKEAR
    return loader.load()