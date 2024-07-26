import torch
from diffusers import StableDiffusionPipeline
from django.core.cache import cache
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Load model weights into memory at server startup.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model-id',
            type=str,
            default='runwayml/stable-diffusion-v1-5',
            help='The model ID of the Stable Diffusion model to load (default: runwayml/stable-diffusion-v1-5)'
        )

    def handle(self, *args, **options):
        model_id = options['model_id']

        try:
            self.stdout.write(f'Loading model weights for model ID: {model_id}')
            pipeline = StableDiffusionPipeline.from_pretrained(model_id)

            if torch.cuda.is_available():
                device = torch.device("cuda")
                self.stdout.write(self.style.SUCCESS('GPU is available. Loading model on GPU.'))
            else:
                device = torch.device("cpu")
                self.stdout.write(self.style.WARNING('GPU is not available. Loading model on CPU.'))

            pipeline.to(device)
            cache.set('stable_diffusion_pipeline', pipeline, None)

            self.stdout.write(self.style.SUCCESS('Model weights loaded successfully.'))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error loading model weights: {e}"))
            raise
