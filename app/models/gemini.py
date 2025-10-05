# gemini_langchain_simple.py
import os
from dotenv import load_dotenv
import google.generativeai as genai
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Modelo Gemini
model = genai.GenerativeModel("gemini-2.5-flash-lite")

# Función simple para usar Gemini con LangChain
def gemini_generate(full_prompt:str):        
    # La API de Gemini funciona con una lista de "turnos".
    # Aquí combinamos todo en el primer turno del usuario.
    messages = [
        {
            'role': 'user',
            'parts': [full_prompt]
        }
    ]

    print('GENERANDO CHUNKS RESPUESTA',flush=True)
    return model.generate_content(messages, stream=True)

# --- Ejemplo con PromptTemplate + LLMChain estilo manual ---
# prompt = PromptTemplate.from_template("Explica qué es un agujero negro en una sola frase, de forma sencilla.")
# final_prompt = prompt.format()  # Aquí podrías pasar variables si las hubiera

# respuesta = gemini_generate(final_prompt)
# print("Respuesta de Gemini:")
# print(respuesta)