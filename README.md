# FACEBOOTH

#### Factory for Artistic Creation and Expression, Building Original Outputs from Trained Human models

## Description

**FACEBOOTH** is a product designed for generating personalized images using DreamBooth-style models. This project includes a graphical user interface and a prompt management system, enabling advanced customization of the generated images.

---

## Project Structure

### Main Files

- **`main.py`**: Entry point of the project. This script orchestrates various functionalities by combining the main components.
- **`README.md`**: This documentation file.
- **`requirements.txt`**: List of required Python dependencies to run the project.
- **`.gitignore`**: Specifies files and folders to exclude from Git version control.

### `photo_generator_lib` Folder

This directory contains the core modules of the library:

#### Core Modules

- **`seed_generator.py`**: Handles seed generation to ensure reproducibility in image generation processes.
- **`dreambooth.py`**: Contains functionalities for training and using DreamBooth models.
- **`gui/`**:
  - **`tkinter_gui.py`**: Implements the graphical user interface using Tkinter.
  - **`app_state.json`**: Configuration file to save the application's GUI state.

- **`model/`**: This folder is expected to contain the trained (or pre-trained) models required for the project.
- **`output/`**: Folder to store generated outputs.
- **`output_last/`**: Contains the most recently generated outputs, enabling quick access.

---

## Installation

### Prerequisites

- Python 3.12 or higher

### Installation Steps

1. Clone the repository:
   ```bash
   git clone <REPOSITORY_URL>
   cd facebooth
   ```
2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Ensure the missing folders are created:
   ```bash
   mkdir model output output_last
   ```

---

## Usage

### Running the Application

1. Launch the main script:
   ```bash
   python main.py
   ```
2. The graphical user interface will open, allowing you to generate images based on specified prompts.

## User Interface Description

The graphical user interface (GUI) of the **FACEBOOTH** application is designed for intuitive image generation and customization. 
![gui](doc/screenshot.png)
Below is a breakdown of its key components:

### Model Selection
- A dropdown menu allows the user to choose from pre-trained models (e.g., `JULIEN_DELANNOY`).

### Prompt Parameters
- **Person Type**: Specify the type of subject (e.g., `MAN`).
- **Shot Type**: Define the framing of the generated image (e.g., `CLOSEUP`).
- **Archetype**: Choose an archetype for the subject (e.g., `CYBORG`).
- **Art Style**: A list box lets the user select from predefined art styles, such as `EasternFantasy`, `GeometricAbstract`, `Surrealism`, etc.

### Prompt Editor
- A text area displays the generated prompt, which can be manually edited for fine-tuning the description used during image generation.

### DreamBooth Parameters
- **Denoising Step**: A slider to adjust the number of denoising steps applied, affecting the output quality and generation time.
- **Seed**: A numeric field to input or randomize a seed value for reproducibility.

### Preview Section
- A main panel displays the generated image.
- A side panel shows thumbnails of other generated images, you can click on it to display in large.

### Generate Button
- A single button to start the image generation process based on the current settings and prompt.


### Customization

- **Prompts**: Modify or add new prompts in the `prompt/prompt_generator.py` module.
- **Models**: Add your own trained models to the `model/` folder.

---

## Contribution

1. Fork the project.
2. Create a branch:
   ```bash
   git checkout -b feature-new-functionality
   ```
3. Submit a Pull Request.

