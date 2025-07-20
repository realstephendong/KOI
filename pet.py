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
            elif self.mascot_type == 'soy':
                idle0 = pygame.image.load("./assets/soy/soy_idle0.png").convert_alpha()
                idle1 = pygame.image.load("./assets/soy/soy_idle1.png").convert_alpha()
            else:
                # Fallback to koi if unknown type
                idle0 = pygame.image.load("./assets/koi/koi_idle0.png").convert_alpha()
                idle1 = pygame.image.load("./assets/koi/koi_idle1.png").convert_alpha()

            # Scale up the sprites
            scaled_idle0 = pygame.transform.scale(idle0, 
                (idle0.get_width() * self.scale_factor, idle0.get_height() * self.scale_factor))
            scaled_idle1 = pygame.transform.scale(idle1, 
                (idle1.get_width() * self.scale_factor, idle1.get_height() * self.scale_factor))

            self.images = {
                "idle": [scaled_idle0, scaled_idle1],
                "happy": [scaled_idle0, scaled_idle1],  # Use idle for now, can be expanded
                "sad": [scaled_idle0, scaled_idle1],    # Use idle for now, can be expanded
                "drinking": [scaled_idle0, scaled_idle1] # Use idle for now, can be expanded
            }
            
        except pygame.error as e:
            print(f"Error loading mascot sprites: {e}")
            # Create fallback sprites
            self.create_fallback_sprites()

    def create_fallback_sprites(self):
        """Create simple fallback sprites if image loading fails"""
        # Create simple colored rectangles as fallback (scaled up)
        fallback_sprite = pygame.Surface((50 * self.scale_factor, 50 * self.scale_factor))
        if self.mascot_type == 'koi':
            fallback_sprite.fill((255, 255, 255))  # White for koi
        else:
            fallback_sprite.fill((200, 200, 200))  # Gray for soy
        
        # Add simple face (scaled)
        face_scale = self.scale_factor
        pygame.draw.rect(fallback_sprite, (0, 0, 0), (15 * face_scale, 15 * face_scale, 5 * face_scale, 5 * face_scale))  # Left eye
        pygame.draw.rect(fallback_sprite, (0, 0, 0), (30 * face_scale, 15 * face_scale, 5 * face_scale, 5 * face_scale))  # Right eye
        pygame.draw.rect(fallback_sprite, (0, 0, 0), (20 * face_scale, 30 * face_scale, 10 * face_scale, 3 * face_scale))  # Mouth
        
        self.images = {
            "idle": [fallback_sprite, fallback_sprite],
            "happy": [fallback_sprite, fallback_sprite],
            "sad": [fallback_sprite, fallback_sprite],
            "drinking": [fallback_sprite, fallback_sprite]
        }

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





            
        