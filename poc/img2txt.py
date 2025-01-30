import os

import torch
from PIL import Image
from transformers import Blip2Processor, Blip2ForConditionalGeneration

processor = Blip2Processor.from_pretrained("Salesforce/blip2-opt-2.7b")
model = Blip2ForConditionalGeneration.from_pretrained(
    "Salesforce/blip2-opt-2.7b",
    device_map="cuda",
    load_in_8bit=False,
    torch_dtype=torch.bfloat16
)

def describe_image(image_path, max_new_tokens=150):
    try:
        image = Image.open(image_path).convert('RGB')
        inputs = processor(images=image, return_tensors="pt").to("cuda")

        # Génération avec contraintes de fluidité
        generated_ids = model.generate(
            **inputs,
            max_new_tokens=max_new_tokens,
            temperature=0.7,  # Contrôle de la créativité
            repetition_penalty=1.2
        )

        return processor.decode(generated_ids[0], skip_special_tokens=True)

    except Exception as e:
        print(f"Erreur : {str(e)}")
        return None


def lister_fichiers_par_extension(repertoire, extension):
    list = []
    for racine, repertoires, fichiers in os.walk(repertoire):
        for fichier in fichiers:
            if fichier.endswith(extension):
                list.append(os.path.join(racine, fichier))
    return list


image_list = lister_fichiers_par_extension("training/images", ".png")

for image in image_list:
    print(f"{image} : {describe_image(image,300)}")
