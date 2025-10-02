import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
from langchain_community.llms.huggingface_pipeline import HuggingFacePipeline
from langchain_core.prompts import PromptTemplate

# --- 1. Carga del Modelo y Tokenizador (Igual que antes) ---
print("Cargando el modelo y tokenizador...")
model_id = "Qwen/Qwen2-1.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    torch_dtype="auto",
    device_map="auto"
)
print("¡Modelo cargado!")

# --- 2. Creación de un "pipeline" de Transformers ---
# LangChain necesita un 'pipeline' de la librería transformers como puente.
# Este objeto estandariza la entrada y salida del modelo.
pipe = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer,
    max_new_tokens=256,
    do_sample=True,
    temperature=0.7,
    top_p=0.95
)

# --- 3. Creación del Objeto LLM de LangChain ---
# Usamos la clase HuggingFacePipeline para "envolver" nuestro pipeline
# y hacerlo compatible con el resto de LangChain.
llm = HuggingFacePipeline(pipeline=pipe)

# --- 4. Uso Básico del Modelo con .invoke() ---
# print("\n--- Probando el LLM con .invoke() ---")
# prompt_basico = "Cuéntame un chiste corto sobre programadores."
# # Aplicamos la plantilla de chat que el modelo espera
# messages = [{"role": "user", "content": prompt_basico}]
# formatted_prompt = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

# respuesta = llm.invoke(formatted_prompt)
# print(f"Prompt: {prompt_basico}")
# print(f"Respuesta: {respuesta.strip()}")

# --- 5. Uso con LangChain Expression Language (LCEL) ---
# Esta es la forma moderna y recomendada de usar LangChain.
# Permite encadenar componentes de forma muy intuitiva.
print("\n--- Probando con una cadena LCEL ---")

# Creamos una plantilla de prompt. La variable {topic} será llenada dinámicamente.
template = """
<|im_start|>system
Eres un experto explicando temas complejos de forma sencilla.
Siempre responde en menos de 100 palabras.<|im_end|>
<|im_start|>user
Tipo de documento	                      ¿Obligatorio por contabilidad?	                  Valor probatorio esperado	                                         Acción recomendada
Estados financieros y pólizas	             Sí (art. 28 cff y NIF)	                     Alto: soporte financiero de operaciones	            Conciliaciones periódicas y auxiliares por operación
CFDI y contratos/órdenes	                 Sí (comprobación)	                     Alto: materialidad y causa del ingreso/egreso	                 Expediente por cliente/proveedor con anexos
Estudios de mercado / precios	                 No siempre	                              Medio-Alto: justificación económica	                       Versión pública y nota metodológica
Presupuestos y proyecciones	                         No	                                  Medio: planeación y razonabilidad	                            Resguardo con control de cambios
Modelos de transfer pricing	                   Sí (cuando aplica)	                         Alto: sustento de vinculación	                       Estudios actualizados y papeles de trabajo
Soporte bancario	                           Sí (trazabilidad)	                   Alto: flujo de efectivo y correspondencia	                     Conciliar depósitos y pagos por operación

**Segun la información anterior, responde: '{prompt}'<|im_end|>
<|im_start|>assistant
"""
prompt_template = PromptTemplate(template=template, input_variables=["prompt"])

# Creamos la cadena (chain) usando el operador "|" (pipe)
# 1. El input (un diccionario) se pasa a la plantilla.
# 2. El prompt formateado se pasa al modelo (llm).
chain = prompt_template | llm

# Ejecutamos la cadena con un tema específico
prompt = input("Inserta tu prompt:")
respuesta_cadena = chain.invoke({"prompt": prompt})

print(f"Pregunta sobre: {prompt}")
print(f"Respuesta de la cadena: {respuesta_cadena.strip()}")