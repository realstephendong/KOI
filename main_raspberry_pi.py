import pygame
import sys
import time
import math
import random
import os
from config_raspberry_pi import *
from mascot import Mascot, MascotState
from ai_manager import AIManager
from sensor_manager import SensorManager
from brick_game import BrickGame
from ui import draw_ui
from pet import Pet

# Import GPIO for Raspberry Pi
try:
    from gpiozero import Button
    GPIO_AVAILABLE = True
    print("🔌 GPIO library found - Running on Raspberry Pi")
except ImportError:
    GPIO_AVAILABLE = False
    print("❌ GPIO library not found - Please install gpiozero on Raspberry Pi")
    sys.exit(1)

class TamagotchiWaterBottle:
    def __init__(self):
        pygame.init()
        
        # Raspberry Pi specific display setup
        os.environ['SDL_VIDEODRIVER'] = 'fbcon'
        os.environ['SDL_FBDEV'] = '/dev/fb0'
        os.environ['SDL_NOMOUSE'] = '1'
        
        # Set up display with Raspberry Pi configuration for vertical orientation
        if PI_FULLSCREEN:
            # For vertical display, we need to rotate the screen
            # This will make the 600x1024 content display sideways on the 1024x600 screen
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
            print("🔧 Raspberry Pi fullscreen mode enabled - Vertical orientation")
        else:
            self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
            print("🔧 Raspberry Pi windowed mode - Vertical orientation")
            
        pygame.display.set_caption("Tamagotchi Water Bottle - Raspberry Pi")
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.sensor_manager = SensorManager()
        self.ai_manager = AIManager()
        
        # Initialize GPIO buttons for Raspberry Pi
        self.yellow_button = Button(17)  # Left button (pet)
        self.blue_button = Button(27)    # Right button (game)
        
        # Button state tracking
        self.yellow_button_pressed = False
        self.blue_button_pressed = False
        self.yellow_button_last_state = False
        self.blue_button_last_state = False
        
        # Mascot management
        self.current_mascot = Mascot('koi')
        self.current_mascot.load_state()
        
        # Mascot interaction
        self.mascot_speaking = False
        self.speech_text = ""
        self.speech_timer = 0
        self.hearts = 3  # Hearts for mascot affection
        
        # New Pet system (partner's implementation)
        self.pet = Pet('koi', self.current_mascot.health, self.hearts)
        
        # Game state
        self.running = True
        self.paused = False
        self.playing_brick = False
        self.brick_game = None
        
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
        print(f"🎮 GPIO Button controls: Yellow (GPIO 17) for pet, Blue (GPIO 27) for game")
        
    def handle_events(self):
        """Handle GPIO button input with press counting"""
        current_time = time.time()
        
        # Check for pygame quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return
        
        # Read GPIO button states
        yellow_current = self.yellow_button.value
        blue_current = self.blue_button.value
        
        # Handle yellow button (left/pet button)
        if yellow_current and not self.yellow_button_last_state:
            # Button just pressed
            if current_time - self.last_button_press < self.button_debounce:
                return  # Debounce
            self.handle_left_button_combo(current_time)
            self.last_button_press = current_time
            
        # Handle blue button (right/game button)
        if blue_current and not self.blue_button_last_state:
            # Button just pressed
            if current_time - self.last_button_press < self.button_debounce:
                return  # Debounce
            self.handle_right_button_combo(current_time)
            self.last_button_press = current_time
        
        # Update button states
        self.yellow_button_last_state = yellow_current
        self.blue_button_last_state = blue_current
        
    def handle_left_button_combo(self, current_time):
        """Handle left button with press counting for different actions"""
        # Check if this is part of a combo
        if current_time - self.last_left_press_time < self.button_combo_timeout:
            self.left_button_press_count += 1
        else:
            self.left_button_press_count = 1
            
        self.last_left_press_time = current_time
        print(f"🔘 Yellow button (GPIO 17) pressed {self.left_button_press_count} times")
        
        # Handle different press counts
        if self.button_mode == BUTTON_MODE_MAIN:
            if self.left_button_press_count == 1:
                # Single press: Pet mascot
                self.pet_mascot()
            elif self.left_button_press_count == 2:
                # Double press: Switch mascot
                self.switch_mascot()
            elif self.left_button_press_count == 3:
                # Triple press: Special interaction
                self.special_mascot_interaction()
        elif self.button_mode == BUTTON_MODE_BRICK:
            self.exit_brick_game()
            
    def handle_right_button_combo(self, current_time):
        """Handle right button with press counting for different actions"""
        # Check if this is part of a combo
        if current_time - self.last_right_press_time < self.button_combo_timeout:
            self.right_button_press_count += 1
        else:
            self.right_button_press_count = 1
            
        self.last_right_press_time = current_time
        print(f"🔘 Blue button (GPIO 27) pressed {self.right_button_press_count} times")
        
        # Handle different press counts
        if self.button_mode == BUTTON_MODE_MAIN:
            if self.right_button_press_count == 1:
                # Single press: Start game
                self.start_brick_game()
            elif self.right_button_press_count == 2:
                # Double press: Show stats
                self.show_stats()
            elif self.right_button_press_count == 3:
                # Triple press: Settings menu
                self.show_settings()
            
    def switch_mascot(self):
        """Switch between different mascots"""
        current_type = self.current_mascot.type
        if current_type == 'koi':
            new_type = 'soy'
        else:
            new_type = 'koi'
            
        # Save current mascot state
        self.current_mascot.save_state()
        
        # Create new mascot
        self.current_mascot = Mascot(new_type)
        self.current_mascot.load_state()
        
        # Update pet to match new mascot
        self.pet = Pet(new_type, self.current_mascot.health, self.hearts)
        
        # Mascot speaks about the switch
        self.mascot_speak(f"Hi! I'm {self.current_mascot.name}! Nice to meet you!")
        
        print(f"🔄 Switched mascot from {current_type} to {new_type}")
        
    def special_mascot_interaction(self):
        """Special interaction with mascot (triple press)"""
        # Give extra health and hearts
        self.current_mascot.health = min(self.current_mascot.max_health, 
                                       self.current_mascot.health + 15)
        self.pet.hp = self.current_mascot.health
        
        self.hearts = min(5, self.hearts + 2)
        self.pet.hearts = self.hearts
        
        # Special state
        self.current_mascot.current_state = MascotState.HAPPY
        self.current_mascot.state_timer = 0
        
        # Add special particles
        self.add_particles(self.current_mascot.x, self.current_mascot.y, 'sparkle')
        
        # Special message
        self.mascot_speak("Wow! You really love me! Thank you for the special attention!")
        
        print("✨ Special mascot interaction triggered!")
        
    def show_stats(self):
        """Show drinking statistics (double press right)"""
        stats_text = f"Today's Progress:\nWater: {self.session_water}ml\nTotal: {self.total_water_drunk}ml\nGoal: {self.daily_goal}ml"
        self.mascot_speak(stats_text)
        print("📊 Showing drinking statistics")
        
    def show_settings(self):
        """Show settings menu (triple press right)"""
        settings_text = "Settings:\n- Health decay rate\n- Button sensitivity\n- Sound effects\n- Display options"
        self.mascot_speak(settings_text)
        print("⚙️ Showing settings menu")
            
    def start_brick_game(self):
        """Start the brick breaker game"""
        print("🎮 Starting Brick Breaker game...")
        try:
            self.playing_brick = True
            self.button_mode = BUTTON_MODE_BRICK
            self.brick_game = BrickGame(self.screen, self.sensor_manager)
            
            # Mascot speaks about the game
            self.mascot_speak(self.ai_manager.generate_random_feature("", "", 100))
            
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
            happiness_boost = min(20, final_score // 10)
            self.current_mascot.health = min(self.current_mascot.max_health, 
                                           self.current_mascot.health + happiness_boost)
            self.current_mascot.current_state = MascotState.HAPPY
            self.current_mascot.state_timer = 0
            
            # Update pet health to match
            self.pet.hp = self.current_mascot.health
            
            # Mascot speaks about the game result
            context = f"User just played Brick Breaker and scored {final_score} points!"
            self.mascot_speak(self.ai_manager.generate_conversation("", "", context))
            
            print(f"🎮 Brick Breaker game ended! Final score: {final_score}, Level: {final_level}")
            
    def pet_mascot(self):
        """Pet the mascot for positive interaction"""
        self.current_mascot.current_state = MascotState.HAPPY
        self.current_mascot.state_timer = 0
        self.current_mascot.health = min(self.current_mascot.max_health, 
                                       self.current_mascot.health + 5)
        
        # Update pet health to match
        self.pet.hp = self.current_mascot.health
        
        # Add hearts for affection
        self.hearts = min(5, self.hearts + 1)
        self.pet.hearts = self.hearts
        
        # Mascot speaks directly
        if not self.mascot_speaking:
            self.mascot_speak(self.ai_manager.generate_conversation("", "", "User just petted me!"))
            
    def mascot_speak(self, text):
        """Make the mascot speak with a speech bubble"""
        self.mascot_speaking = True
        self.speech_text = text
        self.speech_timer = 4.0  # Show speech for 4 seconds
        
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
            # Update the sensor manager
            self.sensor_manager.update()
            
            # Check for drinking motion using the correct methods
            if self.sensor_manager.is_currently_drinking():
                water_amount = self.sensor_manager.water_amount
                if water_amount > 0:
                    self.handle_drinking(water_amount)
                    self.sensor_manager.reset_water_amount()
                    
            # Check for bottle shaking
            if self.sensor_manager.is_shaking:
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
        self.pet.hp = self.current_mascot.health
        
        # Add particles
        self.add_particles(self.current_mascot.x, self.current_mascot.y, 'water')
        
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
        
        # Update pet animation
        animation_state = "idle"
        if self.current_mascot.current_state == MascotState.HAPPY:
            animation_state = "happy"
        elif self.current_mascot.current_state == MascotState.DRINKING:
            animation_state = "drinking"
        elif self.current_mascot.current_state == MascotState.SAD:
            animation_state = "sad"
            
        self.pet.update(dt, animation_state)
        
        # Update particles
        self.update_particles()
        
        # Update timers
        self.speech_timer -= dt
        if self.speech_timer <= 0:
            self.mascot_speaking = False
            
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
        """Draw everything to screen using partner's UI system"""
        if self.playing_brick:
            # Draw brick game
            if self.brick_game:
                self.brick_game.draw()
                pygame.display.flip()
            return
            
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw pet sprite (partner's implementation)
        self.pet.draw(self.screen, "idle")
        
        # Draw UI elements (partner's implementation)
        health_percentage = (self.current_mascot.health / self.current_mascot.max_health) * 100
        draw_ui(self.screen, self.hearts, health_percentage)
        
        # Draw particles
        self.draw_particles()
        
        # Draw mascot speech bubble
        if self.mascot_speaking:
            self.draw_speech_bubble()
            
        # Draw achievement popup
        if self.achievement_timer > 0:
            self.draw_achievement()
            
        # Update display
        pygame.display.flip()
        
    def draw_particles(self):
        """Draw particle effects"""
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
                pygame.draw.polygon(self.screen, color, points)
            else:
                # Draw simple circle
                pygame.draw.circle(self.screen, color, 
                                 (int(particle['x']), int(particle['y'])), 3)
                                 
    def draw_speech_bubble(self):
        """Draw mascot speech bubble (vertical layout)"""
        if not self.speech_text:
            return
            
        # Calculate bubble size based on text
        font = pygame.font.Font(None, 20)
        words = self.speech_text.split()
        lines = []
        current_line = ""
        max_width = 0
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            if font.size(test_line)[0] < 200:  # Smaller for vertical layout
                current_line = test_line
            else:
                lines.append(current_line)
                max_width = max(max_width, font.size(current_line)[0])
                current_line = word
        lines.append(current_line)
        max_width = max(max_width, font.size(current_line)[0])
        
        # Draw speech bubble
        bubble_width = max_width + 30
        bubble_height = len(lines) * 25 + 15
        bubble_x = self.pet.x - bubble_width // 2  # Center relative to pet
        bubble_y = self.pet.y - bubble_height - 50  # Position above pet
        
        # Keep bubble on screen
        if bubble_x < 10:
            bubble_x = 10
        elif bubble_x + bubble_width > SCREEN_WIDTH - 10:
            bubble_x = SCREEN_WIDTH - bubble_width - 10
            
        bubble_rect = pygame.Rect(bubble_x, bubble_y, bubble_width, bubble_height)
        
        # Bubble background
        pygame.draw.rect(self.screen, WHITE, bubble_rect)
        pygame.draw.rect(self.screen, BLACK, bubble_rect, 2)
        
        # Draw speech bubble tail
        tail_x = self.pet.x
        tail_y = bubble_y + bubble_height
        tail_points = [
            (tail_x, tail_y),
            (tail_x - 10, tail_y + 15),
            (tail_x + 10, tail_y + 15)
        ]
        pygame.draw.polygon(self.screen, WHITE, tail_points)
        pygame.draw.polygon(self.screen, BLACK, tail_points, 2)
        
        # Draw text
        for i, line in enumerate(lines):
            text = font.render(line, True, BLACK)
            text_x = bubble_x + 15
            text_y = bubble_y + 8 + i * 20
            self.screen.blit(text, (text_x, text_y))
        
    def draw_achievement(self):
        """Draw achievement popup with pixel-art style"""
        if not self.achievement_popup:
            return
            
        # Draw achievement box with pixel-art style
        box_width = 300  # Smaller for vertical layout
        box_height = 100
        box_x = SCREEN_WIDTH // 2 - box_width // 2
        box_y = 80
        
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        # Box background
        pygame.draw.rect(self.screen, WHITE, box_rect)
        pygame.draw.rect(self.screen, BLACK, box_rect, BORDER_THICKNESS)
        
        # Draw pixel-art border effect
        highlight_rect = pygame.Rect(box_x + 3, box_y + 3, box_width - 6, box_height - 6)
        pygame.draw.rect(self.screen, LIGHT_GRAY, highlight_rect, 1)
        
        # Draw title
        font = pygame.font.Font(None, 24)
        text = font.render("ACHIEVEMENT!", True, BLACK)
        text_rect = text.get_rect(center=(box_rect.centerx, box_rect.y + 20))
        self.screen.blit(text, text_rect)
        
        # Draw achievement text
        font = pygame.font.Font(None, 16)
        text = font.render(self.achievement_popup, True, BLACK)
        text_rect = text.get_rect(center=(box_rect.centerx, box_rect.y + 50))
        self.screen.blit(text, text_rect)
            
    def run(self):
        """Main game loop"""
        while self.running:
            dt = self.clock.tick(FPS) / 1000.0
            
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