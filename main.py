import random
import time

from PIL import Image

from photo_generator_lib.dreambooth import DreamboothModel
from photo_generator_lib.prompt.prompt_generator import PromptGenerator, Archetype, PersonType, ShotType, ArtStyle
from photo_generator_lib.seed_generator import SeedGenerator


def image_grid(imgs, rows, cols):
    assert len(imgs) == rows * cols

    w, h = imgs[0].size
    grid = Image.new('RGB', size=(cols * w, rows * h))
    grid_w, grid_h = grid.size

    for i, img in enumerate(imgs):
        grid.paste(img, box=(i % cols * w, i // cols * h))
    return grid


seed_generator = SeedGenerator()
prompt_generator = PromptGenerator(name="julien_delannoy")

prompt_generator.taking(a_part=ShotType.CLOSEUP)
prompt_generator.taking(a_part=PersonType.MAN)
prompt_generator.taking(a_part=Archetype.CYBERPUNK)
prompt_generator.taking(a_part=[ArtStyle.TheOnlyOne])

prompt_generator.generate_prompt()
nb_images = 9

prompt = [prompt_generator.actual_prompt] * nb_images

dreambooth = DreamboothModel(seed_generator=seed_generator)
images = dreambooth.generate(prompt=prompt)

print(f"{seed_generator.actual_seed()=}")
grid = image_grid(dreambooth.last_result, rows=3, cols=3)

for i in range(nb_images):
    filename = f"{int(time.time())}_{i}_{seed_generator.actual_seed()}.png"
    dreambooth.last_result[i].save(f"output/{filename}")

grid.save("test.png")
