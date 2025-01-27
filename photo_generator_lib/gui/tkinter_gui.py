import time
import tkinter as tk
from enum import Enum

from PIL import Image, ImageTk

from photo_generator_lib.dreambooth import DreamboothModel
from photo_generator_lib.prompt.prompt_generator import ShotType, PersonType, Archetype, ArtStyle, PromptGenerator
from photo_generator_lib.seed_generator import SeedGenerator


class TemporaryPersonaEnum(str, Enum):
    JULIEN_DELANNOY = "julien_delannoy"


class TkinterGui(tk.Tk):
    def __init__(self, dreambooth: DreamboothModel, prompt_generator=PromptGenerator, seed_generator=SeedGenerator):
        super().__init__()

        self.dreambooth = dreambooth
        self.prompt_generator = prompt_generator
        self.seed_generator = seed_generator

        self.title("FACEBOOTH: Factory for Artistic Creation and Expression, Building Original Outputs from Trained Human models")

        self.model_var = tk.StringVar(value=TemporaryPersonaEnum.JULIEN_DELANNOY.name)
        self.shot_type_var = tk.StringVar(value=ShotType.NONE.name)
        self.person_type_var = tk.StringVar(value=PersonType.PERSON.name)
        self.archetype_var = tk.StringVar(value=Archetype.NONE.name)
        self.art_style_var = {choix: tk.BooleanVar() for choix in ArtStyle}

        self.selected_index = 0
        self.denoising_step_var = tk.DoubleVar(value=self.dreambooth.num_inference_steps)
        self.seed_var = tk.IntVar(value=self.seed_generator.actual_seed())

        # self.load_state()

        self._create_interface()
        self.update_prompt()

    def _create_interface(self):
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        self._create_left_configuration_frame(main_frame)
        self.create_right_frame(main_frame)

    def _create_left_configuration_frame(self, main_frame):
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        self._create_unique_choice_box(left_frame, "Model", TemporaryPersonaEnum, self.model_var)
        self._create_prompt_parameters_frame(left_frame)
        self._create_prompt_frame(left_frame)
        self._create_dreambooth_parameter_frame(left_frame)
        self.create_generate_button(left_frame)

    def _create_prompt_parameters_frame(self, left_frame):
        prompt_command_frame = tk.LabelFrame(left_frame, text="Prompt parameters", bd=2)
        prompt_command_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        self._create_unique_choice_box(prompt_command_frame, "Person type", PersonType, self.person_type_var)
        self._create_unique_choice_box(prompt_command_frame, "Shot type", ShotType, self.shot_type_var)
        self._create_unique_choice_box(prompt_command_frame, "Archetype", Archetype, self.archetype_var)
        self._create_multiple_choice_box(prompt_command_frame)

    def _create_unique_choice_box(self, parent, text: str, values: Enum, var):
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        frame.grid_columnconfigure(0, weight=1, minsize=200)
        frame.grid_columnconfigure(1, weight=1, minsize=350)

        label_unique = tk.Label(frame, text=text)
        label_unique.grid(row=0, column=0, padx=5, sticky="w")

        option_menu = tk.OptionMenu(frame, var, *[choix.name for choix in values])
        option_menu.grid(row=0, column=1, padx=5, sticky="ew")

        var.trace("w", lambda *args: self.update_prompt())

    def _create_dreambooth_parameter_frame(self, left_frame):
        model_parameter_frame = tk.LabelFrame(left_frame, text="Dreambooth parameters", bd=2)
        model_parameter_frame.pack(fill=tk.BOTH, padx=5, pady=5)
        self._create_denoising_slider(model_parameter_frame)
        self._create_seed_zone(model_parameter_frame)

    def _create_multiple_choice_box(self, parent):
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        frame.grid_columnconfigure(0, weight=0, minsize=250)
        label_multiple = tk.Label(frame, text="Art Style", anchor="w")
        label_multiple.grid(row=0, column=0, sticky="nw", padx=5)

        self.listbox = tk.Listbox(frame, selectmode=tk.MULTIPLE, height=5)
        self.listbox.grid(row=0, column=1, sticky="nsew")

        for choix in ArtStyle:
            self.listbox.insert(tk.END, choix.name)

        frame.grid_columnconfigure(1, weight=1)

        self.listbox.bind("<<ListboxSelect>>", lambda event: self.update_art_style())

    def _create_prompt_frame(self, parent):
        prompt_frame = tk.LabelFrame(parent, text="Prompt", bd=2)
        prompt_frame.pack(fill=tk.BOTH, padx=5, pady=5)

        self.text_zone = tk.Text(prompt_frame, height=21, width=40, wrap=tk.WORD)
        self.text_zone.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

        self.text_zone.bind("<KeyRelease>", self.update_prompt_to_generator)

    def update_prompt_to_generator(self, event=None):
        current_text = self.text_zone.get("1.0", tk.END).strip()
        self.prompt_generator.actual_prompt = current_text  #

    def _create_denoising_slider(self, parent):
        denoising_frame = tk.Frame(parent)
        denoising_frame.pack(fill=tk.X, pady=5)

        label_denoising = tk.Label(denoising_frame, text="Denoising Step")
        label_denoising.pack(side=tk.LEFT, padx=5)

        slider_denoising = tk.Scale(denoising_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                    variable=self.denoising_step_var)
        slider_denoising.pack(fill=tk.X, padx=5)

        self.denoising_step_var.trace("w", lambda *args: self.update_prompt())

    def _create_seed_zone(self, parent):
        frame_seed = tk.Frame(parent)
        frame_seed.pack(fill=tk.X, pady=5)

        frame_seed.grid_columnconfigure(0, weight=1, minsize=220)
        frame_seed.grid_columnconfigure(1, weight=1, minsize=230)
        frame_seed.grid_columnconfigure(2, weight=1, minsize=100)

        label_seed = tk.Label(frame_seed, text="Seed")
        label_seed.grid(row=0, column=0, padx=5, sticky="w")

        spinbox_seed = tk.Spinbox(frame_seed, from_=self.seed_generator.min, to=self.seed_generator.max,
                                  textvariable=self.seed_var)

        spinbox_seed.grid(row=0, column=1, padx=5, sticky="ew")

        button_dice = tk.Button(frame_seed, text="🎲", width=4, height=2, command=self.roll_seed)
        button_dice.grid(row=0, column=2, padx=5, sticky="e")

        self.seed_var.trace("w", lambda *args: self.update_seed())

    def create_right_frame(self, main_frame):
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        self.create_image_zone(right_frame)

    def create_image_zone(self, parent):
        image_frame = tk.Frame(parent)
        image_frame.pack(side=tk.TOP, pady=10)

        self.label_image = tk.Label(image_frame)
        self.label_image.pack(side=tk.LEFT, padx=10)

        self.afficher_image()

        small_images_frame = tk.Frame(image_frame)
        small_images_frame.pack(side=tk.LEFT, padx=10)

        self.create_small_images(small_images_frame)

    def create_small_images(self, parent):
        self.small_image_labels = []
        for i in range(6):
            small_image_label = tk.Label(parent, bd=2, relief="solid")
            small_image_label.pack(pady=5)
            self.afficher_petite_image(small_image_label, f"output_last/{i}.png")
            small_image_label.bind("<Button-1>", lambda event, index=i: self.change_large_image(event, index))
            self.small_image_labels.append(small_image_label)

    def roll_seed(self):
        self.seed_generator.randomize()
        self.seed_var.set(self.seed_generator.actual_seed())
        self.update_seed()

    def update_seed(self):
        self.seed_generator.seed =  self.seed_var.get()
        self.seed_var.set(self.seed_generator.actual_seed())

    def update_prompt(self):
        prompt_text = f"Model: {self.model_var.get()}\n"

        self.prompt_generator.taking(a_part=PersonType[self.person_type_var.get()])
        self.prompt_generator.taking(a_part=ShotType[self.shot_type_var.get()])
        self.prompt_generator.taking(a_part=Archetype[self.archetype_var.get()])

        art_styles = [ArtStyle[self.listbox.get(i)] for i in self.listbox.curselection()]
        self.prompt_generator.taking(a_part=art_styles)

        self.prompt_generator.generate_prompt()
        prompt_text = self.prompt_generator.actual_prompt

        self.text_zone.delete(1.0, tk.END)
        self.text_zone.insert(tk.END, prompt_text)

    def update_art_style(self):
        art_styles = [ArtStyle[self.listbox.get(i)] for i in self.listbox.curselection()]
        self.prompt_generator.taking(a_part=art_styles)


    def change_large_image(self, event, index):
        self.afficher_image(f"output_last/{index}.png")

        if self.selected_index is not None:
            self.small_image_labels[self.selected_index].config(bd=2, relief="solid")

        self.small_image_labels[index].config(bd=4, relief="groove", bg="yellow")

        self.selected_index = index

    def afficher_image(self, chemin_image="output_last/0.png"):
        img = Image.open(chemin_image)
        img = img.resize((512 * 3, 512 * 3))
        img_tk = ImageTk.PhotoImage(img)
        self.label_image.config(image=img_tk)
        self.label_image.image = img_tk

    def afficher_petite_image(self, label, chemin_image):
        img = Image.open(chemin_image)
        img = img.resize((int(512 / 2.1), int(512 / 2.1)))
        img_tk = ImageTk.PhotoImage(img)
        label.config(image=img_tk)
        label.image = img_tk

    def create_generate_button(self, parent):
        button_valider = tk.Button(parent, text="Generate", command=self.generate, height=4, width=20)
        button_valider.pack(fill=tk.X, pady=5)

    def generate(self):
        self.dreambooth.generate(prompt=[self.prompt_generator.prompt()] * 6)
        print(self.prompt_generator.prompt())
        for i in range(6):
            filename = f"{int(time.time())}_{i}_{self.seed_generator.actual_seed()}.png"
            self.dreambooth.last_result[i].save(f"output/{filename}")
            self.dreambooth.last_result[i].save(f"output_last/{i}.png")
            self.afficher_petite_image(self.small_image_labels[i], f"output_last/{i}.png")

        self.afficher_image(f"output_last/{self.selected_index}.png")
        denoising_step = self.denoising_step_var.get()

        # self.save_state()

    # def save_state(self):
    #     state = {
    #         "model": self.model_var.get(),
    #         "shot_type": self.shot_type_var.get(),
    #         "person_type": self.person_type_var.get(),
    #         "archetype": self.archetype_var.get(),
    #         "art_style": {choix: var.get() for choix, var in self.art_style_var.items()},
    #         "seed": self.seed_var.get(),
    #         "denoising_step": self.denoising_step_var.get(),
    #         "multiple_choice": [self.listbox.get(i) for i in self.listbox.curselection()]
    #     }
    #     with open("app_state.json", "w") as f:
    #         json.dump(state, f)
    #
    # def load_state(self):
    #     if os.path.exists("app_state.json"):
    #         with open("app_state.json", "r") as f:
    #             state = json.load(f)
    #
    #             self.model_var.set(state["model"])
    #             self.shot_type_var.set(state["shot_type"])
    #             self.person_type_var.set(state["person_type"])
    #             self.archetype_var.set(state["archetype"])
    #             for choix, var in self.art_style_var.items():
    #                 var.set(state["art_style"].get(choix, False))
    #             self.seed_var.set(state["seed"])
    #             self.denoising_step_var.set(state["denoising_step"])
    #
    #             for i in range(self.listbox.size()):
    #                 if self.listbox.get(i) in state["multiple_choice"]:
    #                     self.listbox.select_set(i)
