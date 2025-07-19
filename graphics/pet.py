from PIL import Image
from PIL import ImageOps

class Pet:
    def __init__(self, animation_state, hearts, images):
        self.animation_state = animation_state
        self.hp = 50
        self.hearts = hearts
        self.images = images

        self.curr_frame = 0

    def setup_images(self):
        idle0 = Image.open(self.images["idle0"]).convert("1")
        idle1 = Image.open(self.images["idle1"]).convert("1")
        # TODO: Add sad and death

        self.images = {
            "idle": [idle0, idle1]
            # "sad":
            # "death":
        }

    def draw(self, image, animation_state):
        curr_to_draw = self.images[animation_state][self.curr_frame]
        image.paste(curr_to_draw, (29, 5))

        self.curr_frame += 1
        if (self.curr_frame >= len(self.images[animation_state])):
            self.curr_frame = 0





            
        