from enum import Enum
from typing import Optional, List


class ShotType(str, Enum):
    NONE = None
    CLOSEUP = "closeup portrait"
    FULLBODY = "fullbody photography"
    ACTION = "action shot"

class Persona:
    def __init__(self, name: str):
        self.name = name

    def __repr__(self):
        return self.name

class PersonType(str, Enum):
    MAN = "man"
    WOMAN = "woman"
    PERSON = "person"

class Archetype(str, Enum):
    NONE = None
    VIKING = (
        "a viking, powerful and fierce, horns and braids in hair, "
        "fur-lined cape, and helmet, axe in hand, "
        "looking towards the camera, "
        "golden hour lighting"
        "ultra realistic, concept art, intricate details, highly detailed, photorealistic, octane render, 8 k, unreal engine"
    )
    PALADIN = (
        "a paladin, wearing brilliant white armor and a crown, "
        "beautiful landscape in the background, "
        "golden hour lighting, "
        "fantasy concept art, artstation trending, highly detailed, ultra realistic"
    )
    HOBBIT = (
        "a Hobbit, small, big brown eyes, green and brown clothing, "
        "detailed facial features, small feet, wispy hair, "
        "looking into camera, "
        "earthy colors, "
        "fantasy concept art, artstation trending, highly detailed"
    )
    HARRY_POTTER = (
        "a Harry Potter character, magical world, wands, robes, "
        "Hogwarts castle in the background, enchanted forest, "
        "detailed lighting, "
        "digital painting, concept art"
    )
    ELF = (
        "an elf with long blond hair, intricate details, detailed armor, majestic background, "
        "looking towards the viewer, "
        "smooth lighting, "
        "fantasy concept art, digital painting"
    )
    SOCCER = (
        "a soccer player, wearing a orange uniform, "
        "grassy field in the background, motion blur,"
        "intense facial expression, "
        "bright sunlight, dramatic lighting"
    )
    AIKIDO = (
        "a aikidoka, wearing a white kimono and dark green hakama, "
        "a dojo in the background, motion blur, "
        "intense facial expression, "
        "dramatic lighting"
    )
    CLOWN = (
        "a clown, highly detailed, surreal, expressionless face, "
        "abstract background, "
        "bright colors, contrast lighting, "
        "cartoonish, comic book style"
    )
    JEDI = (
        "a jedi with a lightsaber, highly detailed, science fiction, "
        "star wars concept art, intricate details, bright colors, "
        "golden hour, "
        "digital painting, ")
    WIZARD = (
        "a wizard, highly detailed, fantasy concept art, holding a staff,  "
        "intricate details and textures, magical, colorful, "
        "looking into the distance, "
        "fire and stars in the background.")
    CYBERPUNK = (
        "a cyberpunk, dark and gritty, highly detailed, "
        "retro-futuristic style, cyberpunk city in the background, "
        "neon lighting, "
        "8 k resolution, ultra-realistic, octane render, unreal engine")
    ASTRONAUT = (
        "an astronaut, futuristic, highly detailed, "
        "ultra realistic, concept art, intricate textures, space travel, "
        "interstellar background")
    SAMURAI = (
        "a samurai warrior, war-torn landscape in the background, "
        "wearing a black and red armor, ready to fight, detailed textures, "
        "concept art, noir art, digital painting, ultra-realistic")
    NINJA = (
        "a ninja, wearing a black hood and suit, stealthy movements, "
        "dark night background, shadows and mist, detailed and realistic,"
        "digital painting, photorealism, 8k resolution")
    PIRATE = (
        "a pirate, wild and crazy, bandana, eye patch, golden hoop "
        "earrings, tattered and ripped clothes, detailed tattoos, rough and rugged"
        "noir photorealism, ultra real")
    SUPER_HERO = (
        "a superhero, dynamic lighting, intense colors, "
        "detailed costume, artstation trending,"
        "noir photorealism, film")
    KNIGHT = (
        "a knight wearing a full suit of armor, intricate details, "
        "majestic and powerful, bright shining silver armor, matching blue cape, a golden crown, "
        "artstation trending, highly detailed, digital painting")
    CYBORG = (
        "a cyborg, mechanical parts, ultra realistic, concept art, "
        "intricate details, eerie, highly detailed, photorealistic, 8k, unreal engine, "
        "cyberpunk, robotic, steampunk, neon colors, metallic textures, "
        "golden hour")
    MONSTER = (
        "monster with glowing eyes and sharp teeth, dark shadows, "
        "foggy background, highly detailed, photorealism, concept art, digital painting")
    VAMPIRE = (
        "a vampire, pale skin, dark eyes, sharp fangs, detailed "
        "shadows and highlights, eerie atmosphere, mystical and magical, "
        "noir photorealism, surreal and dreamlike, deep red hues")
    ZOMBIE = (
        "a zombie, decaying skin and clothing, dark and eerie, highly detailed, "
        "photorealistic, 8k, ultra realistic, horror style")
    WITCH = (
        "a witch surrounded by magical elements, highly detailed, "
        "photorealism, digital painting, dark colors, grayscale, intricate details, "
        "ultra realism, magical elements")

class ArtStyle(Enum):
    ArtNouveau = ["Alphonse Mucha", "Charlie Bowater", "Magali Villeneuve"]
    EpicFantasy = ["Greg Rutkowski", "John Howe", "Alan Lee"]
    Dreamlike = ["WLOP", "Leesha Hannigan", "Kai Carpenter"]
    WhimsicalFantasy = ["Jim Kay", "Kazu Kibuishi", "Ronald Brenzell"]
    BoldAndVibrant = ["RossDraws", "Max Grecke", "Yahoo Kim"]
    ModernAnime = ["Kazuya Yamashita", "Yuya Kanzaki", "RossDraws"]
    DarkAndGritty = ["Marko Djurdjevic", "Mike Mignola", "Fred Perry"]
    FuturisticSciFi = ["Stephan Martiniere", "Eddie Hong", "BARONTiER"]
    EasternFantasy = ["Yang Zhizhuo", "Yuya Kanzaki", "Kazuya Yamashita"]
    GeometricAbstract = ["Viktor Hulík", "James White", "Fabrizio Bortolussi"]
    Surrealism = ["Fabrizio Bortolussi", "Yahoo Kim", "Leesha Hannigan"]
    ComicBookStyle = ["Fred Perry", "Marko Djurdjevic", "Kazu Kibuishi"]
    TheOnlyOne = ["Akira Toriyama", "Masashi Kishimoto", "Eiichiro Oda"]


class PromptGenerator:
    def __init__(self, name: str):
        self.shot_type: Optional[ShotType] = None
        self.persona = Persona(name=name)
        self.person_type: Optional[PersonType] = None
        self.archetype: Optional[Archetype] = None
        self.art_style: List[str] = []

        self.actual_prompt = self.generate_prompt()

    def generate_prompt(self):
        prompt = ""
        if self.shot_type and self.shot_type != ShotType.NONE:
            prompt += f"{self.shot_type.value} of "
        prompt += str(self.persona)
        if self.person_type:
            prompt += f" {self.person_type.value}"
        if self.archetype and self.archetype != Archetype.NONE:
            prompt += f" as {self.archetype.value}"
        if len(self.art_style)>0:
            prompt += f". Art by "
            if len(self.art_style) > 1:
                prompt += ', '.join(self.art_style[:-1]) + ' and ' + self.art_style[-1]
            else:
                prompt += ''.join(self.art_style)

        self.actual_prompt = prompt

    def taking(self, a_part):
        if isinstance(a_part, ShotType):
            self.shot_type = a_part
        if isinstance(a_part, Archetype):
            self.archetype = a_part
        if isinstance(a_part, PersonType):
            self.person_type = a_part
        if isinstance(a_part, List):
            self.art_style = []
            for obj in a_part:
                if isinstance(obj, ArtStyle):
                    self.art_style += obj.value

        return self
