import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from transformers.generation.streamers import TextIteratorStreamer
from threading import Thread
import os

# --- 1. Configuración ---
MODEL_ID = "Qwen/Qwen-VL-Chat"

# --- MODIFICA ESTAS LÍNEAS ---
IMAGE_PATH = "manati_real_smoking.jpg"
TEXT_PROMPT = input("Escribe tu prompt: ")
# --- FIN DE LA MODIFICACIÓN ---

try:
    # --- 2. Carga del Modelo y Tokenizador ---
    print(f"Cargando el modelo: {MODEL_ID}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID, 
        device_map="auto", 
        trust_remote_code=True
    ).eval()
    print("¡Modelo cargado exitosamente!")

    # --- 3. Preparación para el Streaming ---
    # Creamos el streamer que recibirá los tokens.
    streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

    # --- 4. Creación del Prompt Multimodal ---
    print(f"\nProcesando la imagen: {IMAGE_PATH}")
    print(f"Pregunta: {TEXT_PROMPT}")

    if not os.path.exists(IMAGE_PATH):
        raise FileNotFoundError(f"No se pudo encontrar la imagen en la ruta: {IMAGE_PATH}")

    query = tokenizer.from_list_format([
        {'image': IMAGE_PATH},
        {'text': TEXT_PROMPT},
    ])
    inputs = tokenizer(query, return_tensors='pt').to(model.device)

   # --- 5. Generación Directa (MODO DEPURACIÓN) ---
    # Al llamar a model.generate() directamente, cualquier error que ocurra
    # será "atrapado" por nuestro bloque try...except principal.
    # El efecto de streaming no se verá en tiempo real, pero podremos diagnosticar.
    print("\n--- Ejecutando en modo de depuración para ver el error completo ---")
    generation_kwargs = dict(inputs, streamer=streamer, max_new_tokens=512)
    
    # Esta línea ahora se ejecutará en el hilo principal y revelará el error
    model.generate(**generation_kwargs)
    
    # --- 6. Consumir el Stream (se imprimirá todo de golpe al final) ---
    print("\n--- Respuesta del Modelo ---")
    full_response = ""
    for new_text in streamer:
        full_response += new_text
        print(new_text, end="", flush=True)

    print("\n\n--- Fin de la generación ---")
    
except FileNotFoundError as e:
    print(f"\nERROR: {e}")
    print("Por favor, asegúrate de que la variable IMAGE_PATH apunte a un archivo de imagen válido.")
except Exception as e:
    print(f"\nHa ocurrido un error inesperado: {e}")