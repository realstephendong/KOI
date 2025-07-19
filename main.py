import time
from PIL import Image
from PIL import ImageDraw
# from graphics.pet import Pet
# from button import Button
# from graphics.ui import draw_ui
# from luma.emulator.device import pygame
# from gpiozero import Button

FPS = 1

def setup():
    # SPI-based display for Raspberry Pi 5 using Adafruit library
    import board
    import digitalio
    import adafruit_ssd1327

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
            print("Creating SSD1327 display object...")
            display = adafruit_ssd1327.SSD1327_SPI(128, 96, spi, dc_pin, reset_pin, cs_pin)
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
                print("Creating SSD1327 display object...")
                display = adafruit_ssd1327.SSD1327_SPI(128, 96, spi, dc_pin, reset_pin, cs_pin)
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
                    print("Creating SSD1327 display object...")
                    display = adafruit_ssd1327.SSD1327_SPI(128, 96, spi, dc_pin, reset_pin, cs_pin)
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

def main():
    display = setup()
    image = Image.new("1", (128, 96), 0)
    draw = ImageDraw.Draw(image)
    rect_width, rect_height = 40, 20
    rect_x0 = (128 - rect_width) // 2
    rect_y0 = (96 - rect_height) // 2
    rect_x1 = rect_x0 + rect_width
    rect_y1 = rect_y0 + rect_height
    draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill=1)
    display.image(image)
    display.show()
    time.sleep(2)

if __name__ == "__main__":
    main()