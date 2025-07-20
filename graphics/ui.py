from PIL import Image
from PIL import ImageDraw
import pygame

from config import DEVICE_HEIGHT, DEVICE_WIDTH, MARGIN_X, MARGIN_Y

def draw_ui(offscreen, num_hearts):
    hp_bar = pygame.image.load("./graphics/assets/hp.png").convert_alpha()
    hp_width, hp_height = hp_bar.get_size()

    heart = pygame.image.load("./graphics/assets/heart.png").convert_alpha()
    heart_width, heart_height = heart.get_size()

    # Margin: (6 pixels from the left, 6 pixels from the right)
    offscreen.blit(hp_bar, (MARGIN_X, DEVICE_HEIGHT - MARGIN_Y - hp_height))

    # Calculate and display health

    hp_start = (22, 78)
    hp_end = ((22 + (93 * (1 * 1))), (83))
    
    # draw.rectangle(
    #     [hp_start, hp_end],
    #     fill=225  # fill=0 means black on 1-bit display
    # )

    for i in range (num_hearts):
        offscreen.blit(heart, (DEVICE_WIDTH - MARGIN_X - (heart_width * (i + 1)) - (i * 3), DEVICE_HEIGHT - MARGIN_Y - hp_height - heart_height - 2))