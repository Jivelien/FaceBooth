from typing import List

import PIL.Image
import torch
from diffusers import StableDiffusionPipeline

from photo_generator_lib.seed_generator import SeedGenerator


class DreamboothModel:
    def __init__(self, seed_generator: SeedGenerator):
        self.MODEL_FOLDER = 'model'
        self.model_name = 'julien_delannoy'
        self.model_id = f"{self.MODEL_FOLDER}/{self.model_name}"
        self.seed_generator = seed_generator
        self.generator = torch.Generator("cpu")
        self.pipe = StableDiffusionPipeline.from_pretrained(self.model_id, revision='fp16',
                                                            torch_dtype=torch.float16)
        self.pipe.enable_model_cpu_offload()

        self.num_inference_steps = 50
        self.guidance_scale = 7.5

        self.last_result = []

    def generate(self, prompt: str | List[str]) -> None:
        self.generator = self.generator.manual_seed(self.seed_generator.actual_seed())
        result = self.pipe(prompt, num_inference_steps=self.num_inference_steps,
                           guidance_scale=self.guidance_scale,
                           generator=self.generator)
        self.last_result = result.images
