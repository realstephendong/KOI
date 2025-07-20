from PIL import Image
from PIL import ImageDraw
import pygame

# ========================================
# UI CONTROLLER - CENTRAL POSITIONING SYSTEM
# Controls all UI elements positioning and appearance
# ========================================

# Screen dimensions (locked)
DEVICE_WIDTH = 600
DEVICE_HEIGHT = 1024
MARGIN_X = 6
MARGIN_Y = 6

# Scaling factors (locked)
HP_BAR_SCALE = 3
HEART_SCALE = 3
MASCOT_SCALE = 4

# Mascot positioning (locked) - UI controls this
MASCOT_CENTER_X = DEVICE_WIDTH // 2 - 40
MASCOT_CENTER_Y = DEVICE_HEIGHT // 2 + 60

# HP Bar positioning (locked)
HP_BAR_OFFSET_Y = 130  # Distance below mascot center
HP_BAR_HEALTH_WIDTH = 94  # Width of health bar area within sprite
HP_BAR_HEALTH_HEIGHT = 6  # Height of health bar area within sprite
HP_BAR_HEALTH_X_OFFSET = 12  # X offset within HP bar sprite
HP_BAR_HEALTH_Y_OFFSET = 2  # Y offset within HP bar sprite

# Heart positioning (locked)
HEART_SPACING_EXTRA = 15  # Extra spacing between hearts
HEART_OFFSET_Y = 10  # Distance above HP bar
HEART_X_ADJUSTMENT = 110  # Fine-tune horizontal positioning

class UIController:
    def __init__(self):
        self.mascot_images = {}
        self.hp_bar_image = None
        self.heart_image = None
        self.load_ui_assets()
    
    def load_ui_assets(self):
        """Load all UI assets including mascot sprites"""
        try:
            # Load HP bar
            self.hp_bar_image = pygame.image.load("./assets/hp.png").convert_alpha()
            
            # Load heart sprite
            self.heart_image = pygame.image.load("./assets/heart.png").convert_alpha()
            
            # Load mascot sprites for both types
            self.load_mascot_sprites('koi')
            self.load_mascot_sprites('soy')
            
        except pygame.error as e:
            print(f"Error loading UI assets: {e}")
    
    def load_mascot_sprites(self, mascot_type):
        """Load and scale mascot sprites"""
        try:
            if mascot_type == 'koi':
                idle0 = pygame.image.load("./assets/koi/koi_idle0.png").convert_alpha()
                idle1 = pygame.image.load("./assets/koi/koi_idle1.png").convert_alpha()
            elif mascot_type == 'soy':
                idle0 = pygame.image.load("./assets/soy/soy_idle0.png").convert_alpha()
                idle1 = pygame.image.load("./assets/soy/soy_idle1.png").convert_alpha()
            else:
                return

            # Scale up the sprites
            scaled_idle0 = pygame.transform.scale(idle0, 
                (idle0.get_width() * MASCOT_SCALE, idle0.get_height() * MASCOT_SCALE))
            scaled_idle1 = pygame.transform.scale(idle1, 
                (idle1.get_width() * MASCOT_SCALE, idle1.get_height() * MASCOT_SCALE))

            self.mascot_images[mascot_type] = {
                "idle": [scaled_idle0, scaled_idle1],
                "happy": [scaled_idle0, scaled_idle1],  # Use idle for now, can be expanded
                "sad": [scaled_idle0, scaled_idle1],    # Use idle for now, can be expanded
                "drinking": [scaled_idle0, scaled_idle1] # Use idle for now, can be expanded
            }
            
        except pygame.error as e:
            print(f"Error loading mascot sprites for {mascot_type}: {e}")
    
    def get_mascot_position(self):
        """Get the mascot's position (UI controls this)"""
        return MASCOT_CENTER_X, MASCOT_CENTER_Y
    
    def get_mascot_sprites(self, mascot_type):
        """Get mascot sprites for the specified type"""
        return self.mascot_images.get(mascot_type, self.mascot_images.get('koi', {}))
    
    def draw_mascot(self, offscreen, mascot_type, animation_state="idle", current_frame=0):
        """Draw the mascot sprite at the UI-controlled position"""
        sprites = self.get_mascot_sprites(mascot_type)
        if animation_state not in sprites:
            animation_state = "idle"
            
        if sprites[animation_state]:
            sprite_to_draw = sprites[animation_state][current_frame]
            # Center the sprite at UI-controlled position
            sprite_rect = sprite_to_draw.get_rect(center=(MASCOT_CENTER_X, MASCOT_CENTER_Y))
            offscreen.blit(sprite_to_draw, sprite_rect)
    
    def draw_ui(self, offscreen, num_hearts, health_percentage=100):
        """Draw the UI elements with locked positioning system"""
        try:
            if not self.hp_bar_image or not self.heart_image:
                self.draw_fallback_ui(offscreen, num_hearts, health_percentage)
                return
            
            # Scale up the HP bar (locked scale)
            hp_width, hp_height = self.hp_bar_image.get_size()
            scaled_hp_bar = pygame.transform.scale(self.hp_bar_image, 
                (hp_width * HP_BAR_SCALE, hp_height * HP_BAR_SCALE))
            scaled_hp_width, scaled_hp_height = scaled_hp_bar.get_size()

            # Scale up the heart (locked scale)
            heart_width, heart_height = self.heart_image.get_size()
            scaled_heart = pygame.transform.scale(self.heart_image, 
                (heart_width * HEART_SCALE, heart_height * HEART_SCALE))
            scaled_heart_width, scaled_heart_height = scaled_heart.get_size()

            # Calculate HP bar position (locked positioning)
            hp_x = MASCOT_CENTER_X - scaled_hp_width // 2
            hp_y = MASCOT_CENTER_Y + HP_BAR_OFFSET_Y
            
            # Draw HP bar background
            offscreen.blit(scaled_hp_bar, (hp_x, hp_y))

            # Draw health bar fill (locked positioning)
            health_bar_width = int(HP_BAR_HEALTH_WIDTH * HP_BAR_SCALE)
            health_bar_height = int(HP_BAR_HEALTH_HEIGHT * HP_BAR_SCALE)
            health_bar_x = hp_x + int(HP_BAR_HEALTH_X_OFFSET * HP_BAR_SCALE)
            health_bar_y = hp_y + int(HP_BAR_HEALTH_Y_OFFSET * HP_BAR_SCALE)
            
            # Calculate current health width based on percentage
            current_health_width = int(health_bar_width * (health_percentage / 100))
            
            # Draw the health rectangle that decreases over time
            if current_health_width > 0:
                health_rect = pygame.Rect(health_bar_x, health_bar_y, current_health_width, health_bar_height)
                pygame.draw.rect(offscreen, (255, 255, 255), health_rect)  # White fill

            # Draw hearts (locked positioning)
            heart_spacing = scaled_heart_width + HEART_SPACING_EXTRA
            heart_x_start = hp_x + (scaled_hp_width // 2) - ((heart_spacing * num_hearts) // 2) + HEART_X_ADJUSTMENT
            heart_y = hp_y - scaled_heart_height - HEART_OFFSET_Y
            
            for i in range(num_hearts):
                heart_x = heart_x_start + (i * heart_spacing)
                offscreen.blit(scaled_heart, (heart_x, heart_y))
                
        except pygame.error as e:
            print(f"Error drawing UI: {e}")
            self.draw_fallback_ui(offscreen, num_hearts, health_percentage)

    def draw_fallback_ui(self, offscreen, num_hearts, health_percentage):
        """Fallback UI drawing with locked positioning"""
        # Use same locked positioning system
        hp_bar_width = 100 * HP_BAR_SCALE
        hp_bar_height = 20 * HP_BAR_SCALE
        hp_x = MASCOT_CENTER_X - hp_bar_width // 2
        hp_y = MASCOT_CENTER_Y + HP_BAR_OFFSET_Y
        
        hp_bar_rect = pygame.Rect(hp_x, hp_y, hp_bar_width, hp_bar_height)
        pygame.draw.rect(offscreen, (128, 128, 128), hp_bar_rect)
        pygame.draw.rect(offscreen, (255, 255, 255), hp_bar_rect, 2)
        
        # Draw health fill that fits the HP bar width
        health_width = int(90 * HP_BAR_SCALE * (health_percentage / 100))
        if health_width > 0:
            health_rect = pygame.Rect(hp_x + 5 * HP_BAR_SCALE, 
                                     hp_y + 3 * HP_BAR_SCALE, 
                                     health_width, 14 * HP_BAR_SCALE)
            pygame.draw.rect(offscreen, (255, 255, 255), health_rect)
        
        # Draw simple hearts with locked positioning
        heart_size = 20 * 2
        heart_spacing = heart_size + 10
        heart_x_start = hp_x + (hp_bar_width // 2) - ((heart_spacing * num_hearts) // 2)
        heart_y = hp_y - heart_size - 20
        
        for i in range(num_hearts):
            heart_x = heart_x_start + (i * heart_spacing)
            self.draw_simple_heart(offscreen, heart_x + heart_size//2, heart_y + heart_size//2, heart_size)

    def draw_simple_heart(self, offscreen, x, y, size):
        """Draw a simple heart shape"""
        points = [
            (x, y + size//2),
            (x - size//2, y),
            (x - size//2, y - size//2),
            (x, y - size),
            (x + size//2, y - size//2),
            (x + size//2, y),
        ]
        pygame.draw.polygon(offscreen, (255, 255, 255), points)

# Legacy function for backward compatibility
def draw_ui(offscreen, num_hearts, health_percentage=100):
    """Legacy function - use UIController instead"""
    ui_controller = UIController()
    ui_controller.draw_ui(offscreen, num_hearts, health_percentage)