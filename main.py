import time
from PIL import Image
from PIL import ImageDraw
from graphics.pet import Pet
from button import Button
from graphics.ui import draw_ui
# from luma.emulator.device import pygame

USE_EMULATOR = False
FPS = 1

# Use GPIO 17 (Select) and GPIO 27 (Confirm) for buttons, per GPIO_SETUP.md
# yellow_button = Button(17)
# blue_button = Button(27)

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
            print("Starting display setup...")
            try:
                print("Initializing SPI...")
                spi = board.SPI()
                print("Setting up DC pin (GPIO 25)...")
                dc_pin = digitalio.DigitalInOut(board.D25)     # GPIO 25
                print("Setting up reset pin (GPIO 13)...")
                reset_pin = digitalio.DigitalInOut(board.D13)   # GPIO 13
                print("Setting up CS pin (GPIO 18)...")
                # Use GPIO 18 instead of SPI CS pins to avoid conflicts
                cs_pin = digitalio.DigitalInOut(board.D18)      # GPIO 18 (not SPI)
                print("Creating SSD1306 display object...")
                display = adafruit_ssd1306.SSD1306_SPI(128, 96, spi, dc_pin, reset_pin, cs_pin)
                print("Setting contrast to maximum...")
                display.contrast(255)  # Set to maximum brightness
                print("Clearing display...")
                display.fill(0)
                print("Showing display...")
                display.show()
                print("Display setup complete!")
                return display
            except Exception as e:
                print(f"Error setting up display with GPIO 18: {e}")
                print("Trying GPIO 16...")
                try:
                    # Try GPIO 16
                    print("Initializing SPI for GPIO 16...")
                    spi = board.SPI()
                    print("Setting up DC pin (GPIO 25)...")
                    dc_pin = digitalio.DigitalInOut(board.D25)     # GPIO 25
                    print("Setting up reset pin (GPIO 13)...")
                    reset_pin = digitalio.DigitalInOut(board.D13)   # GPIO 13
                    print("Setting up CS pin (GPIO 16)...")
                    cs_pin = digitalio.DigitalInOut(board.D16)      # GPIO 16
                    print("Creating SSD1306 display object...")
                    display = adafruit_ssd1306.SSD1306_SPI(128, 96, spi, dc_pin, reset_pin, cs_pin)
                    print("Clearing display...")
                    display.fill(0)
                    print("Showing display...")
                    display.show()
                    print("Display setup complete with GPIO 16!")
                    return display
                except Exception as e2:
                    print(f"Error with GPIO 16: {e2}")
                    print("Trying GPIO 20...")
                    try:
                        # Try GPIO 20
                        print("Initializing SPI for GPIO 20...")
                        spi = board.SPI()
                        print("Setting up DC pin (GPIO 25)...")
                        dc_pin = digitalio.DigitalInOut(board.D25)     # GPIO 25
                        print("Setting up reset pin (GPIO 13)...")
                        reset_pin = digitalio.DigitalInOut(board.D13)   # GPIO 13
                        print("Setting up CS pin (GPIO 20)...")
                        cs_pin = digitalio.DigitalInOut(board.D20)      # GPIO 20
                        print("Creating SSD1306 display object...")
                        display = adafruit_ssd1306.SSD1306_SPI(128, 96, spi, dc_pin, reset_pin, cs_pin)
                        print("Clearing display...")
                        display.fill(0)
                        print("Showing display...")
                        display.show()
                        print("Display setup complete with GPIO 20!")
                        return display
                    except Exception as e3:
                        print(f"Error with GPIO 20: {e3}")
                        print("All GPIO attempts failed. Please check your wiring.")
                        raise

    print("Calling get_device()...")
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
        # # Handle button presses
        # if blue_button.is_pressed():
        #     global state, pet_choice
        #     state = "pet"
        #     pet_choice = pet_choices[pet_index]
        #     print(f"Confirmed pet choice: {pet_choice}")
        #     return current_pet
            
        # if yellow_button.is_pressed():
        #     pet_index = (pet_index + 1) % len(pet_choices)
        #     current_pet = create_pet(pet_choices[pet_index])
        #     print(f"Selected pet: {pet_choices[pet_index]}")

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
    
    print("Starting main game loop...")
    frame_count = 0
    
    while True:
        frame_count += 1
        print(f"Frame {frame_count}: Drawing test pattern...")
        
        # Setup canvas
        image = Image.new("1", (device.width, device.height))
        
        # Draw a simple test pattern instead of complex graphics
        draw = ImageDraw.Draw(image)
        
        # Draw a simple rectangle to test if display works
        draw.rectangle([10, 10, 118, 86], outline=1, fill=0)
        draw.text((20, 20), "TEST", fill=1)
        draw.text((20, 40), f"Frame: {frame_count}", fill=1)
        
        # Draw some pixels to make sure display is working
        for i in range(0, 128, 4):
            image.putpixel((i, 60), 1)
        
        # Render canvas
        if USE_EMULATOR:
            device.display(image)
        else:
            device.image(image)
            device.show()

        print(f"Frame {frame_count}: Display updated")
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