import pygame
import sys
import time
import math
import random
import os
from config import *  # Use the vertical dimensions
from graphics.mascot import Mascot, MascotState
from ai_manager import AIManager
from sensor_manager import SensorManager
from graphics.brick_game import BrickGame
from graphics.ui import UIController
from graphics.pet import Pet

# GPIO fallback for testing
GPIO_AVAILABLE = True
print("⌨️  Testing vertical orientation on MacBook")
print("   Press 'A' for yellow button (pet), 'D' for blue button (game)")

class TamagotchiWaterBottle:
    def __init__(self):
        pygame.init()
        
        # Detect if running on Raspberry Pi
        import platform
        is_raspberry_pi = platform.system() == "Linux" and os.path.exists("/proc/cpuinfo")
        
        # Set up display with vertical orientation for testing or fullscreen for Pi
        self.DEVICE_WIDTH = 1024   # Physical screen width
        self.DEVICE_HEIGHT = 600   # Physical screen height
        self.APP_WIDTH = 600       # App width (will be rotated)
        self.APP_HEIGHT = 1024     # App height (will be rotated)
        
        if is_raspberry_pi:
            os.environ['SDL_VIDEODRIVER'] = 'fbcon'
            os.environ['SDL_FBDEV'] = '/dev/fb0'
            os.environ['SDL_NOMOUSE'] = '1'
            self.screen = pygame.display.set_mode((self.DEVICE_WIDTH, self.DEVICE_HEIGHT), pygame.FULLSCREEN)
            print("🔧 Raspberry Pi detected - Using fullscreen mode")
        else:
            self.screen = pygame.display.set_mode((self.DEVICE_WIDTH, self.DEVICE_HEIGHT))
            print("💻 Desktop mode detected")
        
        # Create the offscreen canvas for drawing
        self.offscreen = pygame.Surface((self.APP_WIDTH, self.APP_HEIGHT))
        
        print(f"🔧 Testing vertical orientation: {self.APP_WIDTH}x{self.APP_HEIGHT} canvas on {self.DEVICE_WIDTH}x{self.DEVICE_HEIGHT} screen")
            
        pygame.display.set_caption("Tamagotchi Water Bottle - Vertical Test")
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.sensor_manager = SensorManager()
        self.sensor_manager.shake_threshold = 0.5  # Lower threshold for more sensitive shake detection
        self.ai_manager = AIManager()
        self.ui_controller = UIController()  # New UI controller
        
        # Fallback to keyboard for testing
        if (GPIO_AVAILABLE):
            from gpiozero import Button
            self.yellow_button = Button(17)
            self.blue_button = Button(27)
        else:
            self.yellow_button = None
            self.blue_button = None
        self.yellow_button_up = False # set to true and then false immediately
        self.blue_button_up = False # set to true and then false immediately
        self.yellow_button_last_state = False
        self.blue_button_last_state = False
        print("⌨️  Using keyboard controls: 'A' (pet), 'D' (game)")
        
        # Mascot management
        self.current_mascot = Mascot('koi')
        self.ai_manager.current_pet = 'koi'
        self.current_mascot.load_state()
        
        # Mascot interaction
        self.current_mascot.hearts = 0  # Hearts for mascot affection
        if self.current_mascot.health == 0:
            self.current_mascot.health = 100
        
        # Pet system (now only handles speech bubbles)
        self.pet = Pet()
        
        # Game state
        self.running = True
        self.paused = False
        self.playing_brick = False
        self.brick_game = None
        self.state = "selection"
        
        # Button system
        self.button_mode = BUTTON_MODE_MAIN
        self.last_button_press = 0
        self.button_debounce = 0.3  # Slightly longer debounce for cleaner interaction
        
        # Button press counting system
        self.left_button_press_count = 0
        self.right_button_press_count = 0
        self.button_combo_timer = 0
        self.button_combo_timeout = 1.0  # Time window for button combinations
        self.last_left_press_time = 0
        self.last_right_press_time = 0
        
        # Statistics
        self.total_water_drunk = 0
        self.daily_goal = 2000  # ml
        self.streak_days = 0
        self.last_drink_date = None
        self.session_water = 0  # Water consumed in current session
        
        # Effects
        self.particles = []
        self.achievement_popup = None
        self.achievement_timer = 0
        
        # Sensor status
        self.sensor_status = self.sensor_manager.get_sensor_status()
        print(f"🎯 Sensor initialized: {'Connected' if self.sensor_status['connected'] else 'Simulation Mode'}")
        print(f"🎮 Testing vertical orientation with keyboard controls")
        
        # Get mascot position from UI controller
        mascot_x, mascot_y = self.ui_controller.get_mascot_position()
        print(f"📍 Mascot positioned at ({mascot_x}, {mascot_y})")

        self.load_custom_font()

    def load_custom_font(self):
        """Load the custom TTF font from assets/fonts"""
        try:
            font_path = os.path.join("assets", "fonts", "Delicatus-e9OLl.ttf")
            if os.path.exists(font_path):
                self.custom_font = pygame.font.Font(font_path, 24)
                self.custom_font_small = pygame.font.Font(font_path, 18)
                print(f"✅ Loaded custom font for brick game: {font_path}")
            else:
                print(f"⚠️  Custom font not found: {font_path}")
                self.custom_font = pygame.font.Font(None, 24)  # Fallback to default
                self.custom_font_small = pygame.font.Font(None, 18)  # Fallback to default
        except Exception as e:
            print(f"❌ Error loading custom font: {e}")
            self.custom_font = pygame.font.Font(None, 24)  # Fallback to default
            self.custom_font_small = pygame.font.Font(None, 18)  # Fallback to default
        
    def handle_events(self):
        # Check for pygame quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
            if (GPIO_AVAILABLE):
                self.yellow_button.when_released = lambda: setattr(self, 'yellow_button_up', True)
                self.blue_button.when_released = lambda: setattr(self, 'blue_button_up', True)
            else:
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_a:
                        self.yellow_button_up = True
                    if event.key == pygame.K_d:
                        self.blue_button_up = True
                
    def switch_mascot(self):
        """Switch between different mascots"""
        current_type = self.current_mascot.type
        if current_type == 'koi':
            new_type = 'soy'
        elif current_type == 'soy':
            new_type = 'joy'
        else:
            new_type = 'koi'
            
        # Save current mascot state
        self.current_mascot.save_state()
        
        # Create new mascot
        self.current_mascot = Mascot(new_type)
        self.ai_manager.current_pet = new_type
        self.current_mascot.load_state()
        
        # Mascot speaks about the switch
        self.pet.start_speaking(f"Hi! I'm {self.current_mascot.name}! Nice to meet you!")
        
        print(f"🔄 Switched mascot from {current_type} to {new_type}")
        
    def pet_selection_loop(self):
        if self.yellow_button_up: # select
            print("switch")
            self.switch_mascot()
            self.yellow_button_up = False
        elif self.blue_button_up: # confirm
            print("confirm")
            self.state = "pet"
            self.blue_button_up = False

    def main_loop(self):
        if self.yellow_button_up and self.blue_button_up:
            print("restart")
            self.state = "selection"
        if self.yellow_button_up: # pet
            print("pet")
            self.pet_mascot()
            self.yellow_button_up = False
        elif self.blue_button_up: # game
            print("game")
            self.state = "brick_game"
            self.start_brick_game()
            self.blue_button_up = False

    def game_loop(self):
        if self.yellow_button_up: # quit
            print("quit")
            self.state = "pet"
            self.exit_brick_game()
            self.yellow_button_up = False
        elif self.blue_button_up: # launch ball
            self.brick_game.launch_ball()
            self.blue_button_up = False
            
    def start_brick_game(self):
        """Start the brick breaker game"""
        print("🎮 Starting Brick Breaker game...")
        try:
            self.playing_brick = True
            self.button_mode = BUTTON_MODE_BRICK
            # Pass the offscreen canvas and correct dimensions for vertical orientation
            # Set test_mode=True for keyboard controls
            self.brick_game = BrickGame(self.offscreen, self.sensor_manager, self.APP_WIDTH, self.APP_HEIGHT, test_mode=True)
            
            # Mascot speaks about the game
            self.pet.start_speaking(self.ai_manager.generate_random_feature("", "", 100))
            
            print("🎮 Brick Breaker game started successfully!")
        except Exception as e:
            print(f"❌ Error starting Brick Breaker game: {e}")
            self.playing_brick = False
            self.button_mode = BUTTON_MODE_MAIN
            self.brick_game = None
        
    def exit_brick_game(self):
        """Exit the brick game and return to main screen"""
        if self.brick_game:
            final_score = self.brick_game.score
            final_level = self.brick_game.level
            self.playing_brick = False
            self.button_mode = BUTTON_MODE_MAIN
            self.brick_game = None
            
            # Give mascot happiness boost based on score
            self.current_mascot.hearts = min(3, self.current_mascot.hearts + 1)
            self.current_mascot.current_state = MascotState.IDLE
            self.current_mascot.state_timer = 0
            
            # Mascot speaks about the game result
            context = f"User just played Brick Breaker and scored {final_score} points!"
            self.pet.start_speaking(self.ai_manager.generate_conversation("", "", context))
            
            print(f"🎮 Brick Breaker game ended! Final score: {final_score}, Level: {final_level}")
            
    def pet_mascot(self):
        """Pet the mascot for positive interaction"""
        self.current_mascot.state_timer = 0
        
        # Add hearts for affection
        self.current_mascot.hearts = min(3, self.current_mascot.hearts + 1)

        # Add special particles
        mascot_x, mascot_y = self.ui_controller.get_mascot_position()
        self.add_particles(mascot_x, mascot_y, 'sparkle')
        
        # Mascot speaks directly
        if not self.pet.speaking:
            self.pet.start_speaking(self.ai_manager.generate_conversation("", "", "User just petted me!"))
            
    def add_particles(self, x, y, particle_type):
        """Add particle effects (limited for performance)"""
        # Limit particles for better performance
        if len(self.particles) > 20:
            return
            
        colors = {
            'heart': WHITE,
            'sparkle': WHITE,
            'water': LIGHT_GRAY
        }
        
        for _ in range(5):
            particle = {
                'x': x + random.uniform(-20, 20),
                'y': y + random.uniform(-20, 20),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-3, -1),
                'life': 60,
                'color': colors.get(particle_type, WHITE),
                'type': particle_type
            }
            self.particles.append(particle)
            
    def update_particles(self):
        """Update particle effects"""
        for particle in self.particles[:]:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
            
            if particle['life'] <= 0:
                self.particles.remove(particle)
                
    def update_sensor_data(self):
        """Update sensor data and handle drinking detection"""
        try:
            # Update the sensor manager and get result dict
            sensor_data = self.sensor_manager.update()

            # Check for end of drinking session using just_ended_drinking flag
            if sensor_data.get('just_ended_drinking', False):
                water_amount = sensor_data.get('last_session_amount', 0)
                if water_amount > 0:
                    self.handle_drinking(water_amount)
                self.sensor_manager.just_ended_drinking = False  # Reset flag

            # Check for bottle shaking
            if sensor_data.get('shaking_detected', False):
                self.current_mascot.make_dizzy()

        except Exception as e:
            print(f"❌ Error updating sensor data: {e}")
            
    def update_drinking_statistics(self):
        """Update drinking statistics and achievements"""
        # This would be called when water is consumed
        pass
        
    def handle_drinking(self, water_amount):
        """Handle water drinking event"""
        self.session_water += water_amount
        self.total_water_drunk += water_amount
        
        # Update mascot health
        self.current_mascot.drink_water(water_amount)
        
        # Add particles
        mascot_x, mascot_y = self.ui_controller.get_mascot_position()
        self.add_particles(mascot_x, mascot_y, 'water')
        
        # Check for achievements
        if self.session_water >= MIN_WATER_FOR_ACHIEVEMENT and self.achievement_timer <= 0:
            self.show_achievement(f"Great job! You drank {self.session_water}ml today!")
            
        print(f"💧 Water consumed: {water_amount}ml (Total: {self.total_water_drunk}ml)")
        
    def show_achievement(self, achievement_text):
        """Show achievement popup"""
        self.achievement_popup = achievement_text
        self.achievement_timer = 3.0  # Show for 3 seconds
        
    def update(self, dt):
        """Update game state"""
        # Update sensor data
        self.update_sensor_data()
        
        # Update mascot
        self.current_mascot.update(dt)
        
        # Update pet (speech bubble)
        self.pet.update(dt)
        
        # Update particles
        self.update_particles()
        
        # Update timers
        self.achievement_timer -= dt
        
        # Reset button press counts after timeout
        current_time = time.time()
        if current_time - self.last_left_press_time > self.button_combo_timeout:
            self.left_button_press_count = 0
        if current_time - self.last_right_press_time > self.button_combo_timeout:
            self.right_button_press_count = 0
        
        # Auto-save every 30 seconds
        if int(time.time()) % 30 == 0:
            self.current_mascot.save_state()
            
    def draw(self):
        """Draw everything to offscreen canvas, rotate, then display"""
        if self.playing_brick:
            # Draw brick game on offscreen canvas
            if self.brick_game:
                self.brick_game.draw()
                
                # Rotate the offscreen canvas 180 degrees
                rotated = pygame.transform.rotate(self.offscreen, 270)
                
                # Clear the visible screen
                self.screen.fill(BLACK)
                
                # Center the rotated canvas on the screen
                rotated_rect = rotated.get_rect()
                rotated_rect.center = (self.DEVICE_WIDTH // 2, self.DEVICE_HEIGHT // 2)
                
                # Blit the rotated canvas to the visible screen
                self.screen.blit(rotated, rotated_rect)
                
                pygame.display.flip()
            return
            
        # Clear offscreen canvas
        self.offscreen.fill(BLACK)
        
        # Get mascot position and animation info
        mascot_x, mascot_y = self.ui_controller.get_mascot_position()
        animation_state = self.current_mascot.get_animation_state()
        animation_frame = self.current_mascot.get_animation_frame()
        
        # Draw mascot using UI controller
        self.ui_controller.draw_mascot(self.offscreen, self.current_mascot.type, animation_state, animation_frame)

        if self.state == "selection":
            # Draw selection instructions at the top of the screen
            font = self.custom_font if self.custom_font else pygame.font.Font(None, 24)
            instruction_text_1 = "Press YELLOW (A) to change mascot"
            instruction_text_2 = "Press BLUE (D) to confirm"
            text_surface_1 = font.render(instruction_text_1, True, WHITE)
            text_surface_2 = font.render(instruction_text_2, True, WHITE)
            text_rect_1 = text_surface_1.get_rect(center=(self.APP_WIDTH // 2, 100))
            text_rect_2 = text_surface_2.get_rect(center=(self.APP_WIDTH // 2, 130))
            self.offscreen.blit(text_surface_1, text_rect_1)
            self.offscreen.blit(text_surface_2, text_rect_2)
        
        if self.state != "selection":
            # Draw UI elements using UI controller
            health_percentage = (self.current_mascot.health / self.current_mascot.max_health) * 100
            self.ui_controller.draw_ui(self.offscreen, self.current_mascot.hearts, health_percentage)
        
            # Draw particles on offscreen canvas
            self.draw_particles_offscreen()
            
            # Draw mascot speech bubble on offscreen canvas
            if self.pet.speaking:
                self.pet.draw_speech_bubble(self.offscreen, mascot_x, mascot_y)
            
            # Draw particles on offscreen canvas
            self.draw_particles_offscreen()
            
            # Draw mascot speech bubble on offscreen canvas
            if self.pet.speaking:
                self.pet.draw_speech_bubble(self.offscreen, mascot_x, mascot_y)
                
            # Draw achievement popup on offscreen canvas
            if self.achievement_timer > 0:
                self.draw_achievement_offscreen()
        
        # Rotate the entire offscreen canvas 90 degrees counter-clockwise
        rotated = pygame.transform.rotate(self.offscreen, 180)
        
        # Clear the visible screen
        self.screen.fill(BLACK)
        
        # Center the rotated canvas on the screen
        rotated_rect = rotated.get_rect()
        rotated_rect.center = (self.DEVICE_WIDTH // 2, self.DEVICE_HEIGHT // 2)
        
        # Blit the rotated canvas to the visible screen
        self.screen.blit(rotated, rotated_rect)
        
        # Update display
        pygame.display.flip()
        
    def draw_particles_offscreen(self):
        """Draw particle effects on offscreen canvas"""
        for particle in self.particles:
            alpha = particle['life'] / 60.0
            color = particle['color']
            
            if particle['type'] == 'heart':
                # Draw heart shape
                points = [
                    (particle['x'], particle['y'] - 5),
                    (particle['x'] - 3, particle['y'] - 8),
                    (particle['x'] - 5, particle['y'] - 3),
                    (particle['x'] - 5, particle['y'] + 2),
                    (particle['x'], particle['y'] + 5),
                    (particle['x'] + 5, particle['y'] + 2),
                    (particle['x'] + 5, particle['y'] - 3),
                ]
                pygame.draw.polygon(self.offscreen, color, points)
            else:
                # Draw simple circle
                pygame.draw.circle(self.offscreen, color, 
                                 (int(particle['x']), int(particle['y'])), 3)
                                 
    def draw_achievement_offscreen(self):
        """Draw achievement popup on offscreen canvas with pixel-art style"""
        if not self.achievement_popup:
            return
        
        # Draw achievement box with pixel-art style
        box_width = 300  # Smaller for vertical layout
        box_height = 100
        box_x = self.APP_WIDTH // 2 - box_width // 2
        box_y = 80
        
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        # Box background
        pygame.draw.rect(self.offscreen, WHITE, box_rect)
        pygame.draw.rect(self.offscreen, BLACK, box_rect, BORDER_THICKNESS)
        
        # Draw pixel-art border effect
        highlight_rect = pygame.Rect(box_x + 3, box_y + 3, box_width - 6, box_height - 6)
        pygame.draw.rect(self.offscreen, LIGHT_GRAY, highlight_rect, 1)
        
        # Draw title with custom font
        font_path = os.path.join("assets", "fonts", "Delicatus-e9OLl.ttf")
        try:
            title_font = pygame.font.Font(font_path, 28)
        except Exception as e:
            print(f"Error loading custom font: {e}")
            title_font = pygame.font.Font(None, 28)
        text = title_font.render("ACHIEVEMENT!", True, BLACK)
        text_rect = text.get_rect(center=(box_rect.centerx, box_rect.y + 20))
        self.offscreen.blit(text, text_rect)
        
        # Draw achievement text with custom font
        try:
            body_font = pygame.font.Font(font_path, 20)
        except Exception as e:
            print(f"Error loading custom font: {e}")
            body_font = pygame.font.Font(None, 20)
        text = body_font.render(self.achievement_popup, True, BLACK)
        text_rect = text.get_rect(center=(box_rect.centerx, box_rect.y + 50))
        self.offscreen.blit(text, text_rect)
            
    def run(self):
        """Main game loop"""
        while self.running:
            if self.state == "brick_game":
                dt = self.clock.tick(BRICK_GAME_FPS) / 1000.0
            else:
                dt = self.clock.tick(MASCOT_FPS) / 1000.0
            if (self.state == "selection"):
                self.pet_selection_loop()
            elif (self.state == "pet"):
                self.main_loop()
            elif (self.state == "brick_game"):
                self.game_loop()
            self.handle_events()
            self.update(dt)
            self.draw()
            
        # Cleanup
        self.current_mascot.save_state()
        self.sensor_manager.disconnect()
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = TamagotchiWaterBottle()
    game.run() 