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
    import displayio
    import fourwire
    import adafruit_ssd1327
    import busio

    def get_device():
        print("Starting display setup...")
        try:
            print("Initializing SPI...")
            spi = busio.SPI(board.D11, board.D10)  # SCLK, MOSI
            print("Setting up display bus...")
            display_bus = fourwire.FourWire(
                spi, 
                command=board.D25,    # DC pin
                chip_select=board.D18, # CS pin
                reset=board.D13,      # Reset pin
                baudrate=1000000
            )
            print("Creating SSD1327 display object...")
            display = adafruit_ssd1327.SSD1327(display_bus, width=128, height=96)
            print("Display setup complete!")
            return display
        except Exception as e:
            print(f"Error setting up display with GPIO 18: {e}")
            print("Trying GPIO 16...")
            try:
                # Try GPIO 16
                print("Initializing SPI for GPIO 16...")
                spi = busio.SPI(board.D11, board.D10)  # SCLK, MOSI
                print("Setting up display bus with GPIO 16...")
                display_bus = fourwire.FourWire(
                    spi, 
                    command=board.D25,    # DC pin
                    chip_select=board.D16, # CS pin
                    reset=board.D13,      # Reset pin
                    baudrate=1000000
                )
                print("Creating SSD1327 display object...")
                display = adafruit_ssd1327.SSD1327(display_bus, width=128, height=96)
                print("Display setup complete with GPIO 16!")
                return display
            except Exception as e2:
                print(f"Error with GPIO 16: {e2}")
                print("Trying GPIO 20...")
                try:
                    # Try GPIO 20
                    print("Initializing SPI for GPIO 20...")
                    spi = busio.SPI(board.D11, board.D10)  # SCLK, MOSI
                    print("Setting up display bus with GPIO 20...")
                    display_bus = fourwire.FourWire(
                        spi, 
                        command=board.D25,    # DC pin
                        chip_select=board.D20, # CS pin
                        reset=board.D13,      # Reset pin
                        baudrate=1000000
                    )
                    print("Creating SSD1327 display object...")
                    display = adafruit_ssd1327.SSD1327(display_bus, width=128, height=96)
                    print("Display setup complete with GPIO 20!")
                    return display
                except Exception as e3:
                    print(f"Error with GPIO 20: {e3}")
                    print("All GPIO attempts failed. Please check your wiring.")
                    raise

    print("Calling get_device()...")
    return get_device()

def convert_pil_to_displayio(image, device):
    """Convert PIL image to displayio format for Adafruit library"""
    import displayio
    
    # Create a displayio group and add the image
    group = displayio.Group()
    bitmap = displayio.Bitmap(image.width, image.height, 2)
    
    # Convert PIL image to bitmap
    for y in range(image.height):
        for x in range(image.width):
            pixel = image.getpixel((x, y))
            bitmap[x, y] = 0 if pixel == 0 else 1
    
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=displayio.ColorConverter())
    group.append(tile_grid)
    
    return group

def main():
    
    try:
        display = setup()
        print("Display setup successful!")
        
        while True:
            image = Image.new("1", (128, 96), 0)
            draw = ImageDraw.Draw(image)
            rect_width, rect_height = 40, 20
            rect_x0 = (128 - rect_width) // 2
            rect_y0 = (96 - rect_height) // 2
            rect_x1 = rect_x0 + rect_width
            rect_y1 = rect_y0 + rect_height
            draw.rectangle([rect_x0, rect_y0, rect_x1, rect_y1], fill=1)
            
            print("Drawing rectangle...")
            # Convert PIL image to displayio format
            group = convert_pil_to_displayio(image, display)
            display.root_group = group
            print("Rectangle drawn and displayed!")
            display.show()
            display.refresh()
            
            time.sleep(2)

    except Exception as e:
        print(f"Error in main: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()