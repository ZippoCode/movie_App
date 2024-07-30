import torch
from diffusers import DiffusionPipeline
from django.conf import settings


def generate_image(title: str, overview: str):
    pipeline = DiffusionPipeline.from_pretrained('stabilityai/stable-diffusion-xl-base-1.0')

    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    pipeline.to(device)
    generator = torch.Generator(device=device).manual_seed(settings.SEED)
    prompt = f"Poster Movie - title {title} and overview {overview}, 8k"

    image = pipeline(prompt, generator=generator, guidance_scale=3.5, height=768, width=512).images[0]
    return image
