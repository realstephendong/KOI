from PIL import Image
from PIL import ImageOps
import pygame
import os

class Pet:
    def __init__(self, mascot_type='koi', hp=100, hearts=3):
        self.mascot_type = mascot_type
        self.hp = hp
        self.hearts = hearts
        self.images = {}
        self.curr_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.5  # seconds per frame
        
        # Center position and scale for larger display
        self.x = 480 // 2  # Center horizontally
        self.y = 800 // 2  # Center vertically
        self.scale_factor = 4  # Scale up the sprites
        
        self.setup_images()

    def setup_images(self):
        """Load and setup sprite images for the mascot"""
        try:
            # Load idle animation frames
            if self.mascot_type == 'koi':
                idle0 = pygame.image.load("./assets/koi/koi_idle0.png").convert_alpha()
                idle1 = pygame.image.load("./assets/koi/koi_idle1.png").convert_alpha()
                sad0 = pygame.image.load("./assets/koi/koi_sad0.png").convert_alpha()
                sad1 = pygame.image.load("./assets/koi/koi_sad1.png").convert_alpha()
                dizzy = pygame.image.load("./assets/koi/koi_confused.png").convert_alpha()
                death = pygame.image.load("./assets/koi/koi_death.png").convert_alpha()
            elif self.mascot_type == 'soy':
                idle0 = pygame.image.load("./assets/soy/soy_idle0.png").convert_alpha()
                idle1 = pygame.image.load("./assets/soy/soy_idle1.png").convert_alpha()
                sad0 = pygame.image.load("./assets/soy/soy_sad0.png").convert_alpha()
                sad1 = pygame.image.load("./assets/soy/soy_sad1.png").convert_alpha()
                dizzy = pygame.image.load("./assets/soy/soy_confused.png").convert_alpha()
                death = pygame.image.load("./assets/soy/soy_death.png").convert_alpha()
            elif self.mascot_type == 'joy':
                idle0 = pygame.image.load("./assets/joy/joy_idle0.png").convert_alpha()
                idle1 = pygame.image.load("./assets/joy/joy_idle1.png").convert_alpha()
                sad0 = pygame.image.load("./assets/joy/joy_sad0.png").convert_alpha()
                sad1 = pygame.image.load("./assets/joy/joy_sad1.png").convert_alpha()
                dizzy = pygame.image.load("./assets/joy/joy_confused.png").convert_alpha()
                death = pygame.image.load("./assets/joy/joy_death.png").convert_alpha()
            else:
                # Fallback to koi if unknown type
                idle0 = pygame.image.load("./assets/koi/koi_idle0.png").convert_alpha()
                idle1 = pygame.image.load("./assets/koi/koi_idle1.png").convert_alpha()
                sad0 = pygame.image.load("./assets/koi/koi_sad0.png").convert_alpha()
                sad1 = pygame.image.load("./assets/koi/koi_sad1.png").convert_alpha()
                dizzy = pygame.image.load("./assets/koi/koi_confused.png").convert_alpha()
                death = pygame.image.load("./assets/koi/koi_death.png").convert_alpha()

            # Scale up the sprites
            scaled_idle0 = pygame.transform.scale(idle0, 
                (idle0.get_width() * self.scale_factor, idle0.get_height() * self.scale_factor))
            scaled_idle1 = pygame.transform.scale(idle1, 
                (idle1.get_width() * self.scale_factor, idle1.get_height() * self.scale_factor))
            scaled_sad0 = pygame.transform.scale(sad0, 
                (idle1.get_width() * self.scale_factor, sad0.get_height() * self.scale_factor))
            scaled_sad1 = pygame.transform.scale(sad1, 
                (idle1.get_width() * self.scale_factor, sad1.get_height() * self.scale_factor))
            scaled_dizzy = pygame.transform.scale(dizzy, 
                (idle1.get_width() * self.scale_factor, dizzy.get_height() * self.scale_factor))
            scaled_death = pygame.transform.scale(death, 
                (idle1.get_width() * self.scale_factor, death.get_height() * self.scale_factor))

            self.images = {
                "idle": [scaled_idle0, scaled_idle1],
                "sad": [scaled_sad0, scaled_sad1],
                "dizzy": [scaled_dizzy],
                "death": [scaled_death]
            }
            
        except pygame.error as e:
            print(f"Error loading mascot sprites: {e}")

    def update(self, dt, animation_state="idle"):
        """Update pet animation"""
        self.animation_timer += dt
        
        # Change frame every animation_speed seconds
        if self.animation_timer >= self.animation_speed:
            self.curr_frame = (self.curr_frame + 1) % len(self.images[animation_state])
            self.animation_timer = 0

    def draw(self, offscreen, animation_state="idle"):
        """Draw the pet sprite with current animation frame, centered"""
        if animation_state not in self.images:
            animation_state = "idle"
            
        if self.images[animation_state]:
            curr_to_draw = self.images[animation_state][self.curr_frame]
            # Center the sprite on screen
            sprite_rect = curr_to_draw.get_rect(center=(self.x, self.y))
            offscreen.blit(curr_to_draw, sprite_rect)

    def set_position(self, x, y):
        """Set the pet's position"""
        self.x = x
        self.y = y

    def get_size(self):
        """Get the size of the pet sprite"""
        if self.images and "idle" in self.images and self.images["idle"]:
            return self.images["idle"][0].get_size()
        return (50 * self.scale_factor, 50 * self.scale_factor)  # Default scaled size





            
        