# generate.py
import torch
from diffusers import StableDiffusionXLPipeline, AutoencoderKL, UNet2DConditionModel
from transformers import CLIPTokenizer, CLIPTextModel, CLIPTextModelWithProjection

# Configuration
MODEL_NAME = "stabilityai/stable-diffusion-xl-base-1.0"
VAE_NAME = "madebyollin/sdxl-vae-fp16-fix"
LORA_PATH = "../lora_model"  # Chemin vers votre modèle LoRA entraîné
TOKEN = "julien_delannoy"  # Doit correspondre à l'entraînement
RESOLUTION = 1024
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"

# 1. Charger le pipeline de base
pipe = StableDiffusionXLPipeline.from_pretrained(
    MODEL_NAME,
    torch_dtype=torch.bfloat16,
    variant="fp16",
    use_safetensors=True
).to(DEVICE)

# 2. Remplacer les composants personnalisés
pipe.vae = AutoencoderKL.from_pretrained(VAE_NAME, torch_dtype=torch.bfloat16).to(DEVICE)
pipe.unet = UNet2DConditionModel.from_pretrained(LORA_PATH, torch_dtype=torch.bfloat16).to(DEVICE)
pipe.text_encoder = CLIPTextModel.from_pretrained(MODEL_NAME, subfolder="text_encoder", torch_dtype=torch.bfloat16).to(DEVICE)
pipe.text_encoder_2 = CLIPTextModelWithProjection.from_pretrained(MODEL_NAME, subfolder="text_encoder_2", torch_dtype=torch.bfloat16).to(DEVICE)

# 3. Configuration de génération
prompt = (f"closeup portrait of julien_delannoy man, "
          f"with a shaved head, wearing a formal suit, "
          f"in a flowerish garden, multicolor garden, "
          f"julien_delannoy is smiling, profesional picture, "
          f"digital painting, golden hour"
          )
negative_prompt = "blurry, deformed, cartoon, 3d render"

# 4. Génération d'image
image = pipe(
    prompt=prompt,
    negative_prompt=negative_prompt,
    num_inference_steps=50,
    guidance_scale=7.5,
    height=RESOLUTION,
    width=RESOLUTION,
    target_size=(RESOLUTION, RESOLUTION),
    original_size=(RESOLUTION, RESOLUTION)
).images[0]

# 5. Sauvegarde
image.save("result.png")
print("Génération réussie!")