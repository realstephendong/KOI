from PIL import Image

from config import DEVICE_HEIGHT, MARGIN_X, MARGIN_Y

def draw_ui(image, hearts):
    hp_bar = Image.open("/assets/hp.png").convert("1")
    hp_width, hp_height = hp_bar.size

    heart = Image.open("/assets/heart.png").convert("1")
    heart_width, hp_height = heart.size

    # Margin: (6 pixels from the left, 6 pixels from the right)
    image.paste(hp_bar, (MARGIN_X, DEVICE_HEIGHT - MARGIN_Y - hp_height))
