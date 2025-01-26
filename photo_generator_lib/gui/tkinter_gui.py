import tkinter as tk
from enum import Enum
from tkinter import messagebox
from PIL import Image, ImageTk

from photo_generator_lib.prompt.prompt_generator import ShotType, PersonType, Archetype, ArtStyle


# Définir les Enums
class ChoixUnique(Enum):
    OPTION1 = "Option 1"
    OPTION2 = "Option 2"
    OPTION3 = "Option 3"


class ChoixMultiple(Enum):
    OPTION_A = "Option A"
    OPTION_B = "Option B"
    OPTION_C = "Option C"
    OPTION_D = "Option D"
    OPTION_E = "Option E"
    OPTION_F = "Option F"
    OPTION_G = "Option G"
    OPTION_H = "Option H"
    OPTION_I = "Option I"
    OPTION_J = "Option J"
    OPTION_K = "Option K"
    OPTION_L = "Option L"
    OPTION_M = "Option M"
    OPTION_N = "Option N"
    OPTION_O = "Option O"
    OPTION_P = "Option P"
    OPTION_Q = "Option Q"
    OPTION_R = "Option R"
    OPTION_S = "Option S"
    OPTION_T = "Option T"
    OPTION_U = "Option U"
    OPTION_V = "Option V"
    OPTION_W = "Option W"
    OPTION_X = "Option X"
    OPTION_Y = "Option Y"
    OPTION_Z = "Option Z"


class TemporaryPersonaEnum(str, Enum):
    JULIEN_DELANNOY = "julien_delannoy"


class Application(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Mon interface Tkinter")

        self.model_var = tk.StringVar(value=TemporaryPersonaEnum.JULIEN_DELANNOY.name)
        self.shot_type_var = tk.StringVar(value=ShotType.NONE.name)
        self.person_type_var = tk.StringVar(value=PersonType.PERSON.name)
        self.archetype_var = tk.StringVar(value=Archetype.NONE.name)
        self.art_style_var = {choix: tk.BooleanVar() for choix in ArtStyle}

        self.selected_index = None  # Ajouter une variable pour suivre l'image sélectionnée
        self.seed_var = tk.StringVar()  # Variable pour le seed
        self.denoising_step_var = tk.DoubleVar(value=0)  # Variable pour le denoising step

        self.create_widgets()

    def create_widgets(self):
        # Cadre principal
        main_frame = tk.Frame(self)
        main_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Cadre pour la liste des choix à gauche
        self.create_left_frame(main_frame)

        # Cadre pour l'image et les petites images à droite
        self.create_right_frame(main_frame)

    def create_left_frame(self, main_frame):
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Zone de choix unique
        self.create_choix_unique(left_frame, "Model", TemporaryPersonaEnum, self.model_var)
        self.create_choix_unique(left_frame, "Person type", PersonType, self.person_type_var)
        self.create_choix_unique(left_frame, "Shot type", ShotType, self.shot_type_var)
        self.create_choix_unique(left_frame, "Archetype", Archetype, self.archetype_var)

        # Zone de choix multiple (avec Listbox)
        self.create_choix_multiple_with_listbox(left_frame)

        self.create_text_zone(left_frame)

        # Ajouter la zone denoising
        self.create_denoising_slider(left_frame)

        # Ajouter la zone seed
        self.create_seed_zone(left_frame)

        self.create_button(left_frame)

    def create_choix_unique(self, parent, text: str, values: Enum, var):
        # Créer un cadre pour la ligne contenant le texte et le menu déroulant
        frame = tk.Frame(parent)
        frame.pack(fill=tk.X, pady=5)

        # Configurer les colonnes pour qu'elles aient une taille fixe
        frame.grid_columnconfigure(0, weight=1, minsize=200)  # Colonne pour le texte
        frame.grid_columnconfigure(1, weight=1, minsize=350)  # Colonne pour le menu déroulant

        # Ajouter le texte à gauche avec une colonne dédiée
        label_unique = tk.Label(frame, text=text)
        label_unique.grid(row=0, column=0, padx=5, sticky="w")

        # Ajouter le menu déroulant à droite du texte avec une colonne dédiée
        option_menu = tk.OptionMenu(frame, var, *[choix.name for choix in values])
        option_menu.grid(row=0, column=1, padx=5,
                         sticky="ew")  # Étendre le menu pour prendre toute la largeur de la colonne

    def create_choix_multiple_with_listbox(self, parent):
        label_multiple = tk.Label(parent, text="Choix multiples (avec Listbox)")
        label_multiple.pack(fill=tk.X, pady=5)

        # Créer une zone déroulante pour les choix multiples avec Scrollbar
        scrollable_frame = tk.Frame(parent)
        scrollable_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(scrollable_frame)
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(scrollable_frame, orient="vertical", command=canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill="y")

        scrollable_frame_inner = tk.Frame(canvas)
        canvas.create_window((0, 0), window=scrollable_frame_inner, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        # Ajouter une liste déroulante pour les choix multiples dans Listbox
        self.listbox = tk.Listbox(scrollable_frame_inner, selectmode=tk.MULTIPLE, height=10)
        self.listbox.pack(fill=tk.BOTH, expand=True)

        # Ajouter les éléments dans le Listbox
        for choix in ChoixMultiple:
            self.listbox.insert(tk.END, choix.value)

        # Mettre à jour la taille de la zone déroulante pour s'adapter au contenu
        scrollable_frame_inner.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def create_text_zone(self, parent):
        # Zone de texte au-dessus de l'image et des petites images
        self.text_zone = tk.Text(parent, height=4, width=40)
        self.text_zone.pack(pady=10)

    def create_denoising_slider(self, parent):
        # Créer un slider pour le denoising step
        denoising_frame = tk.Frame(parent)
        denoising_frame.pack(fill=tk.X, pady=5)

        label_denoising = tk.Label(denoising_frame, text="Denoising Step")
        label_denoising.pack(side=tk.LEFT, padx=5)

        slider_denoising = tk.Scale(denoising_frame, from_=0, to=100, orient=tk.HORIZONTAL,
                                    variable=self.denoising_step_var)
        slider_denoising.pack(fill=tk.X, padx=5)

    def create_seed_zone(self, parent):
        # Créer une zone de texte pour entrer le "seed"
        frame_seed = tk.Frame(parent)
        frame_seed.pack(fill=tk.X, pady=5)

        label_seed = tk.Label(frame_seed, text="Seed")
        label_seed.grid(row=0, column=0, padx=5, sticky="w")

        entry_seed = tk.Entry(frame_seed, textvariable=self.seed_var)
        entry_seed.grid(row=0, column=1, padx=5, sticky="ew")

        # Ajouter un bouton carré avec une icône de dé à droite de la zone de texte
        button_dice = tk.Button(frame_seed, text="🎲", width=4, height=2, command=self.roll_seed)
        button_dice.grid(row=0, column=2, padx=5)

    def roll_seed(self):
        # Ici on pourrait implémenter une fonctionnalité pour générer un seed aléatoire, par exemple
        import random
        self.seed_var.set(str(random.randint(1000, 9999)))

    def create_right_frame(self, main_frame):
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.LEFT, padx=10, pady=10, fill=tk.BOTH, expand=True)
        # Zone de texte (au-dessus de l'image)
        # Zone d'affichage d'image et petites images
        self.create_image_zone(right_frame)
        # Cadre pour les boutons (en bas)

    def create_image_zone(self, parent):
        # Créer un cadre pour l'image principale et les petites images
        image_frame = tk.Frame(parent)
        image_frame.pack(side=tk.TOP, pady=10)

        # Image principale
        self.label_image = tk.Label(image_frame)
        self.label_image.pack(side=tk.LEFT, padx=10)

        # Charger l'image principale au démarrage
        self.afficher_image()

        # Cadre pour les petites images à droite
        small_images_frame = tk.Frame(image_frame)
        small_images_frame.pack(side=tk.LEFT, padx=10)

        # Afficher les petites images alignées verticalement
        self.create_small_images(small_images_frame)

    def create_small_images(self, parent):
        # Charger et afficher les 6 petites images
        self.small_image_labels = []  # Ajouter une liste pour les labels des petites images
        for i in range(6):
            small_image_label = tk.Label(parent, bd=2, relief="solid")
            small_image_label.pack(pady=5)
            self.afficher_petite_image(small_image_label, f"1737925249_{i}_4532.png")  # Remplacer par les vrais chemins
            small_image_label.bind("<Button-1>", lambda event, index=i: self.change_large_image(event, index))
            self.small_image_labels.append(small_image_label)

    def change_large_image(self, event, index):
        # Changer la grande image selon l'image sélectionnée
        self.afficher_image(f"1737925249_{index}_4532.png")

        # Ajouter un cadre autour de l'image sélectionnée
        if self.selected_index is not None:
            self.small_image_labels[self.selected_index].config(bd=2, relief="solid")

        # Ajouter un cadre autour de l'image sélectionnée
        self.small_image_labels[index].config(bd=4, relief="groove", bg="yellow")

        # Mettre à jour l'index de l'image sélectionnée
        self.selected_index = index

    def afficher_image(self, chemin_image="1737925249_0_4532.png"):
        # Charger et redimensionner l'image principale
        img = Image.open(chemin_image)  # Remplacer par ton chemin d'image
        img = img.resize((512*3, 512*3))  # Taille de l'image principale
        img_tk = ImageTk.PhotoImage(img)
        self.label_image.config(image=img_tk)
        self.label_image.image = img_tk  # Garder une référence à l'image

    def afficher_petite_image(self, label, chemin_image):
        # Charger et redimensionner les petites images
        img = Image.open(chemin_image)  # Remplacer par ton chemin d'image
        img = img.resize((256, 256))  # Taille des petites images
        img_tk = ImageTk.PhotoImage(img)
        label.config(image=img_tk)
        label.image = img_tk  # Garder une référence à l'image

    def create_button(self, parent):
        button_valider = tk.Button(parent, text="Valider", command=self.valider)
        button_valider.pack(fill=tk.X, pady=5)

        button_image = tk.Button(parent, text="Afficher image", command=self.afficher_image)
        button_image.pack(fill=tk.X, pady=5)

    def valider(self):
        choix_unique = self.shot_type_var.get()
        choix_unique1 = self.person_type_var.get()
        seed = self.seed_var.get()  # Récupérer la valeur du seed
        denoising_step = self.denoising_step_var.get()  # Récupérer le denoising step

        choix_multiple = [self.listbox.get(i) for i in self.listbox.curselection()]

        messagebox.showinfo("Choix",
                            f"Choix unique : {choix_unique} {choix_unique1}\nSeed : {seed}\nDenoising Step : {denoising_step}\nChoix multiples : {', '.join(choix_multiple)}")


if __name__ == "__main__":
    app = Application()
    app.mainloop()
