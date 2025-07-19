import time
from PIL import Image
from PIL import ImageDraw
from graphics.pet import Pet
from button import Button
from graphics.ui import draw_ui
# from luma.emulator.device import pygame

USE_EMULATOR = False
FPS = 1

yellow_button = Button(17)
blue_button = Button(22)

def setup():
    if USE_EMULATOR:
        # Emulator mode (same as before)
        def get_device():
            return pygame(width=128, height=96)
    else:
        # SPI-based display for Raspberry Pi 5 using Adafruit library
        import board
        import digitalio
        import adafruit_ssd1306

        def get_device():
            spi = board.SPI()
            dc_pin = digitalio.DigitalInOut(board.D22)     # GPIO 22
            reset_pin = digitalio.DigitalInOut(board.D13)   # GPIO 13
            cs_pin = digitalio.DigitalInOut(board.CE0)      # GPIO 8 (CE0)
            display = adafruit_ssd1306.SSD1306_SPI(128, 96, spi, dc_pin, reset_pin, cs_pin)
            display.fill(0)
            display.show()
            return display

    return get_device()

def create_pet(pet_choice):
    if (pet_choice == "koi"):
        koi_image_paths = {"idle0": "./graphics/assets/koi/koi_idle0.png",
                        "idle1": "./graphics/assets/koi/koi_idle1.png"}

        koi = Pet("idle", 3, koi_image_paths)
        koi.setup_images()
        return koi
    elif (pet_choice == "soy"):
        soy_image_paths = {"idle0": "./graphics/assets/soy/soy_idle0.png", 
                        "idle1": "./graphics/assets/soy/soy_idle1.png"}

        soy = Pet("idle", 3, soy_image_paths)
        soy.setup_images()
        return soy

def increase_friendship(device):
    pass

def pet_selection_loop(device):
    pet_choices = ["koi", "soy"]
    pet_index = 0
    current_pet = create_pet(pet_choices[pet_index])
        
    while True:
        # Handle button presses
        if blue_button.is_pressed():
            global state, pet_choice
            state = "pet"
            pet_choice = pet_choices[pet_index]
            print(f"Confirmed pet choice: {pet_choice}")
            return current_pet
            
        if yellow_button.is_pressed():
            pet_index = (pet_index + 1) % len(pet_choices)
            current_pet = create_pet(pet_choices[pet_index])
            print(f"Selected pet: {pet_choices[pet_index]}")

        image = Image.new("1", (device.width, device.height))
        
        # Draw components
        current_pet.draw(image, "idle")

        # Render canvas
        if USE_EMULATOR:
            device.display(image)
        else:
            device.image(image)
            device.show()

        time.sleep(1 / FPS) 

def run_loop(device, pet):
    """Main game loop with the selected pet"""
    
    while True:
        # Setup canvas
        image = Image.new("1", (device.width, device.height))
        
        # Draw components
        pet.draw(image, "idle")
        draw_ui(image, 3)

        # Render canvas
        if USE_EMULATOR:
            device.display(image)
        else:
            device.image(image)
            device.show()

        time.sleep(1 / FPS) 
        

def main():
    pet_choice = "soy"
    game_state = "selection"
    
    device = setup()
    
    if game_state == "selection":
        selected_pet = pet_selection_loop(device)

        run_loop(device, selected_pet)
    
    elif game_state == "pet":
        pet = create_pet(pet_choice)

        run_loop(device, pet)

if __name__ == "__main__":
    main()