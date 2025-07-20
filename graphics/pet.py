from PIL import Image
from PIL import ImageOps
import pygame

class Pet:
    def __init__(self, hp, hearts, images):
        self.hp = hp
        self.hearts = hearts
        self.images = images

        self.curr_frame = 0

    def setup_images(self):
        idle0 = pygame.image.load(self.images["idle0"]).convert_alpha()
        idle1 = pygame.image.load(self.images["idle1"]).convert_alpha()

        # sad0 = Image.open("../assets/soy/soy0.png").convert("1")
        # sad1 = Image.open("../assets/soy/soy0.png").convert("1")
        # death = Image.open("../assets/soy/soy0.png").convert("1")

        self.images = {
            "idle": [idle0, idle1]
            # "sad":
            # "death":
        }

    def draw(self, offscreen, animation_state):
        curr_to_draw = self.images[animation_state][self.curr_frame]
        offscreen.blit(curr_to_draw, (29, 5))

        self.curr_frame += 1
        if (self.curr_frame >= len(self.images[animation_state])):
            self.curr_frame = 0





            
        