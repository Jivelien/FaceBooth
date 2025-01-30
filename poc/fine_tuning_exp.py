# Installation des dépendances
import os
import random

import torch
from PIL import Image
from diffusers import (
    StableDiffusionXLPipeline,
    AutoencoderKL,
    UNet2DConditionModel,
    DDPMScheduler
)
from peft import LoraConfig, get_peft_model
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from transformers import CLIPTokenizer, CLIPTextModel, CLIPTextModelWithProjection

# Configuration
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "expandable_segments:True"
MODEL_NAME = "stabilityai/stable-diffusion-xl-base-1.0"
VAE_NAME = "madebyollin/sdxl-vae-fp16-fix"
DATASET_PATH = "../mon_dataset"
TOKEN = "julien_delannoy"  # Remplacez par votre token
BATCH_SIZE = 1
NUM_EPOCHS = 100
LEARNING_RATE = 1e-5
OUTPUT_DIR = "../lora_model"
RESOLUTION = 1024  # 1024 si VRAM >24GB

os.makedirs(OUTPUT_DIR, exist_ok=True)


# Classe Dataset
class CustomDataset(Dataset):
    def __init__(self, root_dir, token):
        self.image_dir = os.path.join(root_dir, "images")
        self.image_files = [f for f in os.listdir(self.image_dir) if f.endswith((".jpg", ".png"))]

        self.transform = transforms.Compose([
            transforms.Resize((RESOLUTION, RESOLUTION)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ColorJitter(0.1, 0.1, 0.1),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5])
        ])

        self.prompts = [
            f"sharp photo of {token} person, 8k hd",
            f"portrait of {token} person, studio lighting",
            f"closeup of {token} face, detailed skin texture"
        ]

    def __len__(self):
        return len(self.image_files) * 3  # Data augmentation x3

    def __getitem__(self, idx):
        img_idx = idx % len(self.image_files)
        image_path = os.path.join(self.image_dir, self.image_files[img_idx])
        image = Image.open(image_path).convert("RGB")
        image = self.transform(image)
        prompt = self.prompts[idx % len(self.prompts)]

        # 25% de prompts génériques
        if random.random() < 0.25:
            prompt = random.choice(["photo of a person", "human portrait"])

        return {"pixel_values": image, "prompt": prompt}


# Initialisation des modèles
device = "cuda" if torch.cuda.is_available() else "cpu"
torch.cuda.empty_cache()

# Composants SDXL
vae = AutoencoderKL.from_pretrained(VAE_NAME, torch_dtype=torch.bfloat16).to(device)
unet = UNet2DConditionModel.from_pretrained(MODEL_NAME, subfolder="unet", torch_dtype=torch.bfloat16)
tokenizer1 = CLIPTokenizer.from_pretrained(MODEL_NAME, subfolder="tokenizer", use_fast=False)
tokenizer2 = CLIPTokenizer.from_pretrained(MODEL_NAME, subfolder="tokenizer_2", use_fast=False)
text_encoder1 = CLIPTextModel.from_pretrained(MODEL_NAME, subfolder="text_encoder", torch_dtype=torch.bfloat16).to(
    device)
text_encoder2 = CLIPTextModelWithProjection.from_pretrained(MODEL_NAME, subfolder="text_encoder_2",
                                                            torch_dtype=torch.bfloat16).to(device)

# Configuration LoRA
lora_config = LoraConfig(
    # r=24,
    r=8,
    # lora_alpha=48,
    lora_alpha=16,
    target_modules=["to_k", "to_q", "to_v"],
    use_dora=True,
    init_lora_weights="gaussian"
)
unet = get_peft_model(unet, lora_config)
unet.enable_gradient_checkpointing()
unet.to(device, dtype=torch.bfloat16)

# Optimiseur
from bitsandbytes.optim import Adam8bit

optimizer = Adam8bit(unet.parameters(), lr=LEARNING_RATE)
noise_scheduler = DDPMScheduler.from_pretrained(MODEL_NAME, subfolder="scheduler")

# DataLoader
dataset = CustomDataset(DATASET_PATH, TOKEN)
train_loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True, pin_memory=True)

# Entraînement
global_step = 0
for epoch in range(NUM_EPOCHS):
    unet.train()
    text_encoder1.eval()
    text_encoder2.eval()

    for batch in train_loader:
        optimizer.zero_grad(set_to_none=True)

        # Conversion images -> latents
        with torch.no_grad(), torch.amp.autocast(device_type='cuda', dtype=torch.bfloat16):
            latents = vae.encode(batch["pixel_values"].to(device)).latent_dist.sample()
            latents = latents * vae.config.scaling_factor

        # Génération bruit
        noise = torch.randn_like(latents, dtype=torch.bfloat16)
        timesteps = torch.randint(
            0, noise_scheduler.config.num_train_timesteps,
            (BATCH_SIZE,), device=device
        ).long()
        noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

        # Encodage textuel
        with torch.no_grad(), torch.amp.autocast(device_type='cuda', dtype=torch.bfloat16):
            inputs1 = tokenizer1(
                batch["prompt"],
                padding="max_length",
                max_length=77,
                truncation=True,
                return_tensors="pt"
            ).to(device)

            inputs2 = tokenizer2(
                batch["prompt"],
                padding="max_length",
                max_length=77,
                truncation=True,
                return_tensors="pt"
            ).to(device)

            encoder_out1 = text_encoder1(**inputs1)
            encoder_out2 = text_encoder2(**inputs2)

            text_embeddings = torch.cat([encoder_out1.last_hidden_state, encoder_out2.last_hidden_state], dim=-1)
            time_ids = torch.tensor([[RESOLUTION, RESOLUTION, 0, 0, RESOLUTION, RESOLUTION]]).to(device)
            added_cond_kwargs = {
                "text_embeds": encoder_out2.text_embeds,
                "time_ids": time_ids
            }

        # Forward pass
        with torch.amp.autocast(device_type='cuda', dtype=torch.bfloat16):
            noise_pred = unet(
                noisy_latents,
                timesteps,
                encoder_hidden_states=text_embeddings,
                added_cond_kwargs=added_cond_kwargs,
                return_dict=False
            )[0]

        # Calcul loss
        loss = torch.nn.functional.mse_loss(noise_pred.float(), noise.float())
        loss.backward()
        torch.nn.utils.clip_grad_norm_(unet.parameters(), 1.0)
        optimizer.step()

        # Logging
        if global_step % 10 == 0:
            mem = torch.cuda.memory_allocated() / 1e9
            print(
                f"Epoch: {epoch + 1}/{NUM_EPOCHS} | Step: {global_step} | Loss: {loss.item():.4f} | VRAM: {mem:.2f}GB")
            torch.cuda.empty_cache()

        global_step += 1

# Fusion LoRA et sauvegarde
unet = unet.merge_and_unload()
unet.save_pretrained(OUTPUT_DIR)

# Pipeline final
pipe = StableDiffusionXLPipeline.from_pretrained(
    MODEL_NAME,
    vae=vae,
    unet=unet,
    text_encoder=text_encoder1,
    text_encoder_2=text_encoder2,
    tokenizer=tokenizer1,
    tokenizer_2=tokenizer2,
    torch_dtype=torch.bfloat16,
    variant="fp16"
).to(device)

# Activation des optimisations
try:
    pipe.enable_xformers_memory_efficient_attention()
except:
    print("Xformers non disponible")

# Génération
prompt = f"{TOKEN}"
image = pipe(
    prompt=prompt,
    num_inference_steps=30,
    guidance_scale=7.0,
    height=RESOLUTION,
    width=RESOLUTION,
    target_size=(RESOLUTION, RESOLUTION),
    original_size=(RESOLUTION, RESOLUTION)
).images[0]

image.save("result.jpg")
print("Génération réussie!")
