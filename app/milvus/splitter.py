import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from typing import List
from langchain.schema import Document
from fastapi import APIRouter

router = APIRouter()

tokenizer = tiktoken.get_encoding("cl100k_base")

def tiktoken_len(text):
    tokens = tokenizer.encode(text, disallowed_special=())
    return len(tokens)

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50, # Solapamiento de 50 tokens entre chunks
    length_function=tiktoken_len,
    separators=["\n\n", "\n", " ", ""]
)

@router.get("/split-document/")
def chunk_documents(
    documents: List[Document], 
) -> List[Document]:
    """
    Recibe una lista de documentos y un objeto text_splitter,
    y devuelve una lista aplanada de chunks.
    
    Args:
        documents: La lista de objetos Document (salida de loader.load()).
        text_splitter: Una instancia configurada de un TextSplitter.

    Returns:
        Una lista de objetos Document, donde cada uno es un chunk.
    """    
    # split_documents hace todo el trabajo pesado
    chunks = text_splitter.split_documents(documents)
    
    print(f"Se han creado {len(chunks)} chunks en total.")
    return chunks