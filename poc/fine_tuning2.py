# train_lora_corrected.py
import os
import torch
import random
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
from diffusers import StableDiffusionXLPipeline, AutoencoderKL, UNet2DConditionModel, DDPMScheduler, \
    DPMSolverMultistepScheduler
from transformers import CLIPTokenizer, CLIPTextModel, CLIPTextModelWithProjection
from peft import LoraConfig, get_peft_model
from PIL import Image


class Config:
    MODEL_NAME = "stabilityai/stable-diffusion-xl-base-1.0"
    VAE_NAME = "madebyollin/sdxl-vae-fp16-fix"
    DATASET_PATH = "../mon_dataset"
    OUTPUT_DIR = "../lora_model"
    TOKEN = "julien_delannoy"
    RESOLUTION = 1024
    EPOCHS = 200
    LR = 1e-5
    BATCH_SIZE = 1
    SEED = 42
    DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
    VALIDATION_STEPS = 50


# Seed initialization
torch.manual_seed(Config.SEED)
random.seed(Config.SEED)


class FaceDataset(Dataset):
    def __init__(self, root_dir, token):
        self.image_dir = os.path.join(root_dir, "images")
        self.image_files = [f for f in os.listdir(self.image_dir) if f.endswith((".jpg", ".png"))]

        self.transform = transforms.Compose([
            transforms.Resize((Config.RESOLUTION, Config.RESOLUTION)),
            transforms.RandomHorizontalFlip(p=0.5),
            transforms.ToTensor(),
            transforms.Normalize([0.5], [0.5])
        ])

        self.prompts = [
            f"sharp photo of {token}, 8k uhd",
            f"portrait of {token}, studio lighting",
            f"closeup of {token}, detailed skin texture"
        ]

    def __len__(self):
        return len(self.image_files) * 3

    def __getitem__(self, idx):
        img_idx = idx % len(self.image_files)
        image_path = os.path.join(self.image_dir, self.image_files[img_idx])
        image = Image.open(image_path).convert("RGB")
        image = self.transform(image)
        prompt = self.prompts[idx % len(self.prompts)]

        if random.random() < 0.25:
            prompt = random.choice(["photo of a person", "human portrait"])

        return {"pixel_values": image, "prompt": prompt}


def load_models():
    vae = AutoencoderKL.from_pretrained(Config.VAE_NAME, torch_dtype=torch.bfloat16).to(Config.DEVICE)
    unet = UNet2DConditionModel.from_pretrained(Config.MODEL_NAME, subfolder="unet", torch_dtype=torch.bfloat16)

    text_encoder1 = CLIPTextModel.from_pretrained(
        Config.MODEL_NAME,
        subfolder="text_encoder",
        torch_dtype=torch.bfloat16
    ).to(Config.DEVICE)

    text_encoder2 = CLIPTextModelWithProjection.from_pretrained(
        Config.MODEL_NAME,
        subfolder="text_encoder_2",
        torch_dtype=torch.bfloat16
    ).to(Config.DEVICE)

    tokenizers = (
        CLIPTokenizer.from_pretrained(Config.MODEL_NAME, subfolder="tokenizer"),
        CLIPTokenizer.from_pretrained(Config.MODEL_NAME, subfolder="tokenizer_2")
    )

    return vae, unet, text_encoder1, text_encoder2, tokenizers


def setup_lora(unet):
    config = LoraConfig(
        r=16,
        lora_alpha=32,
        target_modules=["to_k", "to_q", "to_v", "to_out.0"],
        use_dora=True
    )
    return get_peft_model(unet, config)


def generate_validation_image(unet, vae, text_encoder1, text_encoder2, tokenizer1, tokenizer2, step):
    pipe = StableDiffusionXLPipeline.from_pretrained(
        Config.MODEL_NAME,
        vae=vae,
        unet=unet,
        text_encoder=text_encoder1,
        text_encoder_2=text_encoder2,
        tokenizer=tokenizer1,
        tokenizer_2=tokenizer2,
        torch_dtype=torch.bfloat16,
        variant="fp16"
    ).to(Config.DEVICE)

    try:
        image = pipe(
            prompt=f"portrait of {Config.TOKEN} person",
            num_inference_steps=50,
            guidance_scale=7.5,
            height=Config.RESOLUTION,
            width=Config.RESOLUTION
        ).images[0]
        image.save(f"validation/step_{step}.png")
        image.save(f"result.png")
    except Exception as e:
        print(f"Validation error: {e}")
    finally:
        del pipe
        torch.cuda.empty_cache()


def train():
    os.makedirs("../validation", exist_ok=True)
    vae, unet, text_encoder1, text_encoder2, (tokenizer1, tokenizer2) = load_models()

    # LoRA setup
    lora_unet = setup_lora(unet).to(Config.DEVICE)
    lora_unet.enable_gradient_checkpointing()

    optimizer = torch.optim.AdamW(lora_unet.parameters(), lr=Config.LR)
    noise_scheduler = DDPMScheduler.from_pretrained(Config.MODEL_NAME, subfolder="scheduler")

    dataset = FaceDataset(Config.DATASET_PATH, Config.TOKEN)
    train_loader = DataLoader(dataset, batch_size=Config.BATCH_SIZE, shuffle=True)

    global_step = 0
    for epoch in range(Config.EPOCHS):
        lora_unet.train()

        for batch in train_loader:
            images = batch["pixel_values"].to(Config.DEVICE).to(torch.bfloat16)

            # VAE Encoding
            with torch.no_grad():
                latents = vae.encode(images).latent_dist.sample() * vae.config.scaling_factor

            # Noise generation
            noise = torch.randn_like(latents)
            timesteps = torch.randint(
                0, noise_scheduler.config.num_train_timesteps,
                (Config.BATCH_SIZE,),
                device=Config.DEVICE
            ).long()

            noisy_latents = noise_scheduler.add_noise(latents, noise, timesteps)

            # Text encoding
            with torch.no_grad():
                # First text encoder
                text_inputs1 = tokenizer1(
                    batch["prompt"],
                    padding="max_length",
                    max_length=77,
                    truncation=True,
                    return_tensors="pt"
                ).to(Config.DEVICE)
                text_embeddings1 = text_encoder1(**text_inputs1).last_hidden_state

                # Second text encoder
                text_inputs2 = tokenizer2(
                    batch["prompt"],
                    padding="max_length",
                    max_length=77,
                    truncation=True,
                    return_tensors="pt"
                ).to(Config.DEVICE)
                text_embeddings2 = text_encoder2(**text_inputs2)

                # Prepare embeddings
                pooled_prompt_embeds = text_embeddings2.text_embeds
                time_ids = torch.tensor(
                    [[Config.RESOLUTION, Config.RESOLUTION, 0, 0, Config.RESOLUTION, Config.RESOLUTION]]).to(
                    Config.DEVICE)

                # Concatenate embeddings
                prompt_embeds = torch.cat([text_embeddings1, text_embeddings2.last_hidden_state], dim=-1)

            # Forward pass
            noise_pred = lora_unet(
                noisy_latents,
                timesteps,
                encoder_hidden_states=prompt_embeds,
                added_cond_kwargs={
                    "text_embeds": pooled_prompt_embeds,
                    "time_ids": time_ids
                }
            ).sample

            # Loss calculation
            loss = torch.nn.functional.mse_loss(noise_pred.float(), noise.float())
            loss.backward()

            # Optimization
            torch.nn.utils.clip_grad_norm_(lora_unet.parameters(), 1.0)
            optimizer.step()
            optimizer.zero_grad()

            # Validation
            if global_step % Config.VALIDATION_STEPS == 0:
                generate_validation_image(
                    lora_unet,
                    vae,
                    text_encoder1,
                    text_encoder2,
                    tokenizer1,
                    tokenizer2,
                    global_step
                )

            if global_step % 10 == 0:
                mem = torch.cuda.memory_allocated() / 1e9
                print(f"Epoch: {epoch + 1}/{Config.EPOCHS} | Step: {global_step} | Loss: {loss.item():.4f} | VRAM: {mem:.2f}GB")

            global_step += 1

    generate_validation_image(
        lora_unet,
        vae,
        text_encoder1,
        text_encoder2,
        tokenizer1,
        tokenizer2,
        global_step
    )
    # Save final model
    lora_unet.save_pretrained(Config.OUTPUT_DIR)
    print("Training completed successfully!")


if __name__ == "__main__":
    train()