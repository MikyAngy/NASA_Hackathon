# check_gpu.py
import torch

print(f"Versión de PyTorch: {torch.__version__}")
print("--------------------------------------------------")

if torch.cuda.is_available():
    print("✅ ¡Éxito! PyTorch puede acceder a tu GPU NVIDIA.")
    print(f"Número de GPUs disponibles: {torch.cuda.device_count()}")
    print(f"Nombre de la GPU: {torch.cuda.get_device_name(0)}")
else:
    print("❌ ERROR: PyTorch NO puede encontrar una GPU compatible con CUDA.")
    print("Esto es casi seguro la causa de tu problema.")
    print("Revisa el Paso 2 de la guía para reinstalar PyTorch correctamente.")