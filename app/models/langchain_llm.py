# import torch
# from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
# from langchain_core.prompts import PromptTemplate
# import threading

# # --- 1. Carga del modelo y tokenizador ---
# print("Cargando el modelo y tokenizador...")
# # model_id = "Qwen/Qwen2-1.5B-Instruct"
# # model_id = "Qwen/Qwen2.5-0.5B-Instruct"
# model_id = "Qwen/Qwen2.5-3B-Instruct"

# tokenizer = AutoTokenizer.from_pretrained(model_id)
# model = AutoModelForCausalLM.from_pretrained(
#     model_id,
#     dtype="auto",
#     device_map="auto"
# ).eval()

# print("¡Modelo cargado!")

# # --- 2. Creamos un streamer ---
# streamer = TextIteratorStreamer(tokenizer, skip_prompt=True, skip_special_tokens=True)

# def generate_stream(prompt):
#     inputs = tokenizer(prompt, return_tensors="pt").to(model.device)

#     thread = threading.Thread(
#         target=model.generate,
#         kwargs=dict(
#             **inputs,
#             max_new_tokens=256,
#             do_sample=True,
#             temperature=0.7,
#             top_p=0.95,
#             streamer=streamer
#         )
#     )
#     thread.start()

#     return streamer

# # --- 3. Integrar con LangChain ---
# template = """
# <|im_start|>system
# Eres un experto explicando temas complejos de forma sencilla. Te llamas MikyChat
# Siempre responde en menos de 100 palabras.<|im_end|>
# <|im_start|>user
# ---------------------
# {knowledge}
# ---------------------
# ** Segun la información anterior, responde: '{prompt}'<|im_end|>
# <|im_start|>assistant
# """
# prompt_template = PromptTemplate(template=template, input_variables=["prompt","knowledge"])

# # Función que combina LangChain con streaming
# def get_prompt_template(user_prompt: str):
#     # Renderiza el prompt con LangChain
#     return prompt_template.format(prompt=user_prompt,knowledge="")
#     # print("final prompt", final_prompt,flush=True)
#     # Inicia generación en streaming
#     # for token in generate_stream(final_prompt):
#         # print(token, end="", flush=True)  # aquí podrías enviar tokens a WebSocket/API

# # --- 4. Ejecutar ---
# # while True:
# #     prompt = input("Inserta tu prompt: ")
# #     run_chain_with_streaming(prompt)
