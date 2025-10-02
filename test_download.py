# test_download.py
from transformers import AutoTokenizer, AutoModelForCausalLM
import os

# --- INSTRUCCIÓN IMPORTANTE ---
# Pega tu token de Hugging Face aquí, aunque ya hayas iniciado sesión con la CLI.
# Esto fuerza al script a usarlo y puede resolver problemas de configuración.
# Ve a https://huggingface.co/settings/tokens para obtenerlo.
my_token = "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" 

model_id = "Qwen/Qwen2-1B-Instruct"

print("--------------------------------------------------")
print(f"Intentando descargar el modelo: {model_id}")
print("Forzando el uso de un token de autenticación...")

try:
    # Pasamos el token explícitamente a la función de descarga
    tokenizer = AutoTokenizer.from_pretrained(
        model_id,
        token=my_token
    )

    print("\n✅ Tokenizador descargado exitosamente.")

    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        token=my_token,
        device_map="auto" # Usamos auto para que se adapte a CPU/GPU
    )
    print("✅ Modelo descargado exitosamente.")
    print("\n¡Prueba exitosa! El problema podría estar en tu otro código.")

except Exception as e:
    print("\n------------------- ¡ERROR! -------------------")
    print("La descarga falló con el script de diagnóstico.")
    print(f"Error específico: {e}")
    print("\n--- ANÁLISIS DEL ERROR ---")
    print("Si el error sigue siendo 'not a valid model identifier',")
    print("es casi 100% seguro un problema de RED (proxy/firewall).")
    print("Revisa los siguientes pasos.")