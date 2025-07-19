from PIL import Image
from PIL import ImageDraw

from config import DEVICE_HEIGHT, DEVICE_WIDTH, MARGIN_X, MARGIN_Y

def draw_ui(image, num_hearts):
    draw = ImageDraw.Draw(image)

    hp_bar = Image.open("./graphics/assets/hp.png").convert("1")
    hp_width, hp_height = hp_bar.size

    heart = Image.open("./graphics/assets/heart.png").convert("1")
    heart_width, heart_height = heart.size

    # Margin: (6 pixels from the left, 6 pixels from the right)
    image.paste(hp_bar, (MARGIN_X, DEVICE_HEIGHT - MARGIN_Y - hp_height))

    # Calculate and display health

    hp_start = (22, 78)
    hp_end = ((22 + (93 * (1 * 1))), (83))
    
    draw.rectangle(
        [hp_start, hp_end],
        fill=225  # fill=0 means black on 1-bit display
    )

    for i in range (num_hearts):
        image.paste(heart, (DEVICE_WIDTH - MARGIN_X - (heart_width * (i + 1)) - (i * 3), DEVICE_HEIGHT - MARGIN_Y - hp_height - heart_height - 2))

