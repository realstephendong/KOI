import time
from PIL import Image
from PIL import ImageDraw
from graphics.pet import Pet
from button import Button
from graphics.ui import draw_ui
from luma.core.render import canvas

USE_EMULATOR = True
FPS = 1

select_button = Button(17)
confirm_button = Button(27)

def setup():
    if USE_EMULATOR:
        from luma.emulator.device import pygame
        def get_device():
            return pygame(width=128, height=96)
    else:
        from luma.core.interface.serial import spi
        from luma.oled.device import ssd1306
        def get_device():
            serial = spi(port=0, device=0, gpio_DC=22, gpio_RST=13)
            return ssd1306(serial)
        
    device = get_device()

    return device

def create_pet(pet_choice):
    if (pet_choice == "koi"):
        koi_image_paths = {"idle0": "./graphics/assets/koi/koi_idle0.png",
                        "idle1": "./graphics/assets/koi/koi_idle1.png"}

        koi = Pet("idle", 0, 3, koi_image_paths)
        koi.setup_images()
        return koi
    elif (pet_choice == "soy"):
        soy_image_paths = {"idle0": "./graphics/assets/soy/soy_idle0.png", 
                        "idle1": "./graphics/assets/soy/soy_idle1.png"}

        soy = Pet("idle", 0, 3, soy_image_paths)
        soy.setup_images()
        return soy
    
def draw_frame(device, pet):
        # Setup canvas
    image = Image.new("1", (device.width, device.height))
    
    # Draw components
    pet.draw(image, "idle")
    draw_ui(image, 3)

    # Render canvas
    device.display(image)

def pet_selection_loop(device):
    pet_choices = ["koi", "soy"]
    pet_index = 0
    current_pet = create_pet(pet_choices[pet_index])
        
    while True:
        # Handle button presses
        if confirm_button.is_pressed():
            global state, pet_choice
            state = "pet"
            pet_choice = pet_choices[pet_index]
            print(f"Confirmed pet choice: {pet_choice}")
            return current_pet
            
        if select_button.is_pressed():
            pet_index = (pet_index + 1) % len(pet_choices)
            current_pet = create_pet(pet_choices[pet_index])
            print(f"Selected pet: {pet_choices[pet_index]}")


        draw_frame(device, current_pet)
        time.sleep(1 / FPS) 

def run_loop(device, pet):
    """Main game loop with the selected pet"""
    
    while True:
        draw_frame(device, pet)

        time.sleep(1 / FPS) 
        

def main():
    pet_choice = "soy"
    game_state = "pet"
    
    device = setup()
    
    if game_state == "selection":
        selected_pet = pet_selection_loop(device)

        run_loop(device, selected_pet)
    
    elif game_state == "pet":
        pet = create_pet(pet_choice)

        run_loop(device, pet)

if __name__ == "__main__":
    main()