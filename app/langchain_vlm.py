import torch
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from langchain_core.prompts import PromptTemplate
import threading

# --- 1. Carga del modelo y tokenizador ---
print("Cargando el modelo y tokenizador...")
model_id = "Qwen/Qwen-VL-Chat"

# --- MODIFICA ESTAS LÍNEAS ---
IMAGE_PATH = "app\manati_real_smoking.jpg" 
# --- FIN DE LA MODIFICACIÓN ---

tokenizer = AutoTokenizer.from_pretrained(model_id)
model = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="auto"
).eval()

print("¡Modelo cargado!")

# --- 2. Creamos un streamer ---
streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

def generate_stream(prompt):
    inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

    thread = threading.Thread(
        target=model.generate,
        kwargs=dict(
            **inputs,
            max_new_tokens=256,
            do_sample=True,
            temperature=0.7,
            top_p=0.95,
            streamer=streamer
        )
    )
    thread.start()

    return streamer

# --- 3. Integrar con LangChain ---
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

** Segun la información anterior, responde: '{prompt}'<|im_end|>
<|im_start|>assistant
"""
prompt_template = PromptTemplate(template=template, input_variables=["prompt"])

# Función que combina LangChain con streaming
def run_chain_with_streaming(user_prompt: str):
    # Renderiza el prompt con LangChain
    query = tokenizer.from_list_format([
        {'image': IMAGE_PATH},
        {'text': user_prompt},
    ])
    # Inicia generación en streaming
    for token in generate_stream(query):
        print(token, end="", flush=True)  # aquí podrías enviar tokens a WebSocket/API
    print()

# --- 4. Ejecutar ---
while True:
    prompt = input("Inserta tu prompt: ")
    run_chain_with_streaming(prompt)
