# backend/chart_tool.py
import json
from typing import Dict
from dotenv import load_dotenv
load_dotenv()
from models.gemini import model 
# LangChain imports (importar desde submódulos modernos)
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.tools import Tool
from langchain_google_genai import ChatGoogleGenerativeAI

# --- Configura tu LLM aquí ---
# Reemplaza por tu LLM (ChatOpenAI, Gemini wrapper, etc.)
# Debes tener un objeto `llm` compatible con LangChain:
#   - ejemplo: from langchain.chat_models import ChatOpenAI; llm = ChatOpenAI(model="gpt-4o-mini")
#   - o usar el wrapper Gemini que ya creaste: llm = GeminiLC(...)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=0.7,
)
# --- Prompt que obliga a salida JSON Vega-Lite ---
TEMPLATE = """
Eres un asistente que, a partir de:
- DOCUMENT: texto(s) con información / métricas
- USER_REQUEST: requerimiento del usuario sobre el gráfico

Extraes los requisitos y generas **únicamente** un objeto JSON con clave "vega_lite"
que contenga un spec válido de **Vega-Lite** (versión 5) y, si aplica, "data" (array de objetos).
No agregues explicaciones. Si algún campo no aplica, úsalo vacío o omitelo.

Formato de salida EXACTO:
{{
  "vega_lite": {{ ...vega-lite spec... }}
}}

DOCUMENT:
{text}

USER_REQUEST:
{user_request}
"""

prompt = PromptTemplate.from_template(TEMPLATE)
chain = LLMChain(llm=llm, prompt=prompt)

def generate_chart_spec(document: str, user_request: str) -> Dict:
    """
    Llama al LLM para obtener JSON (vega-lite spec).
    Devuelve dict (parsed JSON) o lanza excepción si no es JSON.
    """
    # Junta la entrada y corre el chain
    raw = chain.run({"text": document, "user_request": user_request})

    # A veces el LLM puede añadir texto antes/después; intentamos localizar el JSON
    # Buscamos el primer "{" y el último "}" y parseamos
    try:
        start = raw.index("{")
        end = raw.rindex("}") + 1
        j = raw[start:end]
        parsed = json.loads(j)
    except Exception as e:
        raise ValueError(f"Salida del LLM no es JSON parseable: {e}\nRAW OUTPUT:\n{raw}")

    # Validación mínima: que venga "vega_lite"
    if "vega_lite" not in parsed:
        raise ValueError("El JSON debe contener la clave 'vega_lite'. Salida: " + str(parsed))
    return parsed

# --- Crear Tool para LangChain Agent ---
def _chart_tool_entrypoint(combined: str) -> str:
    """
    Función que recibirá un único string con formato:
      DOCUMENT: ... ### USER_REQUEST: ...
    Retorna JSON string (la misma estructura generada).
    """
    # parse simple
    if "### USER_REQUEST:" in combined:
        doc, user_req = combined.split("### USER_REQUEST:", 1)
        doc = doc.replace("DOCUMENT:", "").strip()
        user_req = user_req.strip()
    else:
        # si solo pasan prompt, tratamos todo como user_request
        doc = ""
        user_req = combined

    spec = generate_chart_spec(doc, user_req)
    return json.dumps(spec, ensure_ascii=False)

chart_tool = Tool.from_function(
    func=_chart_tool_entrypoint,
    name="chart_generator",
    description=(
        "Genera un Vega-Lite spec JSON para un gráfico especializado. "
        "Input: 'DOCUMENT:... ### USER_REQUEST: ...'. Output: JSON string with key 'vega_lite'."
    ),
)
