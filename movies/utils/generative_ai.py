import torch
from django.core.cache import cache


def generate_image(prompt):
    pipeline = cache.get('stable_diffusion_pipeline')
    if not pipeline:
        raise RuntimeError("Model weights are not loaded.")
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")
    pipeline.to(device)
    image = pipeline(prompt).images[0]
    return image
