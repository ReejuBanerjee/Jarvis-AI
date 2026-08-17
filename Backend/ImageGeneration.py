import asyncio
from random import randint
from PIL import Image
from dotenv import get_key
import os
from time import sleep
from huggingface_hub import InferenceClient

# Initialize the Hugging Face Inference Client using a free-tier model
client = InferenceClient(
    model="black-forest-labs/FLUX.1-schnell",  # Free-tier friendly model
    token=get_key('.env', 'HuggingFaceAPIKey')
)

# Function to open and display images based on a given prompt
def open_images(prompt):
    folder_path = r"Data"  # Folder where the images are stored
    prompt = prompt.replace(" ", "_")  # Replace spaces in prompt with underscores

    # Generate the filenames for the images
    Files = [f"{prompt}{i}.jpg" for i in range(1, 5)]

    for jpg_file in Files:
        image_path = os.path.join(folder_path, jpg_file)
        try:
            # Try to open and display the image
            img = Image.open(image_path)
            print(f"Opening image: {image_path}")
            img.show()
            sleep(1)  # Pause for 1 second before showing the next image
        except IOError:
            print(f"Unable to open {image_path}")

# Function to generate images using the client
def generate_images(prompt: str):
    # Create 4 images sequentially
    for i in range(1, 5):
        enhanced_prompt = f"{prompt}, high quality, detailed, seed = {randint(0, 1000000)}"
        
        try:
            print(f"Generating image {i}/4...")
            # Generate image using client text_to_image
            image = client.text_to_image(enhanced_prompt)
            
            # Save the generated image
            file_path = fr"Data\{prompt.replace(' ', '_')}{i}.jpg"
            image.save(file_path)
        except Exception as e:
            print(f"Generation error on image {i}: {e}")

# Wrapper function to generate and open images
def GenerateImages(prompt: str):
    generate_images(prompt)  
    open_images(prompt)  

# Main loop to monitor for image generation requests
while True:
    try:
        # Read the status and prompt from the data file
        with open(r"Frontend\Files\ImageGeneration.data", "r") as f:
            Data: str = f.read()

        if "," in Data:
            Prompt, Status = Data.split(",")
            Prompt = Prompt.strip()
            Status = Status.strip()

            # If the status indicates an image generation request
            if Status == "True":
                print(f"Generating Images for: {Prompt} ...")

                # Reset the status file to False FIRST so it never loops again
                with open(r"Frontend\Files\ImageGeneration.data", "w") as f:
                    f.write("False,False")

                # Now generate and open the images safely
                GenerateImages(prompt=Prompt)
                
                break  # Exit the loop safely after processing once
        
        sleep(1)  # Wait for 1 second before checking again

    except Exception as e:
        print(f"Loop Exception: {e}")
        sleep(1)