from transformers import Qwen2VLForConditionalGeneration, AutoProcessor
from qwen_vl_utils import process_vision_info
import torch
from PIL import Image

# Cargar el modelo 2B (mucho más ligero)
model = Qwen2VLForConditionalGeneration.from_pretrained(
    "Qwen/Qwen2-VL-2B-Instruct",
    dtype=torch.bfloat16,
    device_map="auto",
    trust_remote_code=True  # Agregar esto
)

processor = AutoProcessor.from_pretrained("Qwen/Qwen2-VL-2B-Instruct")

img = Image.open("manati_real.jpg").convert("RGB")

# El resto del código es exactamente igual
messages = [
    {
        "role": "user",
        "content": [
            {
                "type": "image",
                "image": "<image>",
            },
            {"type": "text", "text": "¿Qué hay en esta imagen?"},
        ],
    }
]

text = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
# image_inputs, video_inputs = process_vision_info(messages)
inputs = processor(text=[text], images=[img], padding=True, return_tensors="pt").to("cuda")

generated_ids = model.generate(**inputs, max_new_tokens=128)
generated_ids_trimmed = [out_ids[len(in_ids):] for in_ids, out_ids in zip(inputs.input_ids, generated_ids)]
output_text = processor.batch_decode(generated_ids_trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)
print(output_text[0])