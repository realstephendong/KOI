import time
from PIL import Image
from PIL import ImageDraw
from graphics.pet import Pet
from luma.core.render import canvas

USE_EMULATOR = False
FPS = 1

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

def pet_selection_loop():
    pet_choice = "koi"
        
    while True:
        return pet_choice
    
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

def run_loop(device):
    pet_choice = pet_selection_loop()

    koi = create_pet(pet_choice)

    while True:
        image = Image.new("1", (device.width, device.height))

        koi.draw(image, "idle")

        # for drawing shapes
        # draw = ImageDraw.Draw(image)
        device.display(image)
        time.sleep(1 / FPS) 
        

def main():
    device = setup()
    run_loop(device)

if __name__ == "__main__":
    main()