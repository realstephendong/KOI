import pygame
import sys
import time
import math
import random
from config import *
from mascot import Mascot, MascotState
from ai_manager import AIManager
from sensor_manager import SensorManager
from brick_game import BrickGame

class TamagotchiWaterBottle:
    def __init__(self):
        pygame.init()
        
        # Set up display
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Tamagotchi Water Bottle")
        self.clock = pygame.time.Clock()
        
        # Initialize components
        self.sensor_manager = SensorManager()
        self.ai_manager = AIManager()
        
        # Mascot management
        self.current_mascot = Mascot('koi')
        self.current_mascot.load_state()
        
        # Game state
        self.running = True
        self.paused = False
        self.playing_brick = False
        self.brick_game = None
        
        # Button system
        self.button_mode = BUTTON_MODE_MAIN
        self.last_button_press = 0
        self.button_debounce = 0.3  # Slightly longer debounce for cleaner interaction
        
        # Mascot interaction
        self.mascot_speaking = False
        self.speech_text = ""
        self.speech_timer = 0
        self.hearts = 3  # Hearts for mascot affection
        
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
        print(f"🎮 Button controls: {BUTTON_LEFT} (pet) and {BUTTON_RIGHT} (game)")
        
    def handle_events(self):
        """Handle pygame events for button input"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                current_time = time.time()
                
                # Only process button presses if enough time has passed
                if current_time - self.last_button_press < self.button_debounce:
                    continue
                    
                if event.key == pygame.K_ESCAPE:
                    if self.playing_brick:
                        self.exit_brick_game()
                    else:
                        self.running = False
                        
                elif event.key == ord(BUTTON_LEFT):
                    self.handle_left_button()
                    self.last_button_press = current_time
                    
                elif event.key == ord(BUTTON_RIGHT):
                    self.handle_right_button()
                    self.last_button_press = current_time
                    
    def handle_left_button(self):
        """Handle left button press (pet mascot or exit game)"""
        print("🔘 Left button pressed")
        
        if self.button_mode == BUTTON_MODE_MAIN:
            self.pet_mascot()
        elif self.button_mode == BUTTON_MODE_BRICK:
            self.exit_brick_game()
            
    def handle_right_button(self):
        """Handle right button press (start game)"""
        print("🔘 Right button pressed - Starting game")
        
        if self.button_mode == BUTTON_MODE_MAIN:
            self.start_brick_game()
            
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
        
        # Add hearts for affection
        self.hearts = min(5, self.hearts + 1)
        
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
        """Update sensor data and handle drinking/shaking events"""
        # Get sensor data using your sophisticated detection system
        sensor_data = self.sensor_manager.update()
        
        # Handle drinking detection with precise water amount calculation
        if sensor_data['drinking_detected']:
            water_amount = sensor_data['water_amount']
            if water_amount > 0:
                self.handle_drinking(water_amount)
                print(f"🍶 Drinking detected! Water consumed: {water_amount}ml")
            
        # Handle shaking detection
        if sensor_data['shaking_detected']:
            self.current_mascot.make_dizzy()
            print("🔄 Shake detected! Mascot is dizzy!")
            
        # Update statistics display
        self.update_drinking_statistics()
        
    def update_drinking_statistics(self):
        """Update drinking statistics from sensor data"""
        sensor_status = self.sensor_manager.get_sensor_status()
        self.session_water = sensor_status['total_water_consumed']
        
    def handle_drinking(self, water_amount):
        """Handle water drinking event"""
        self.current_mascot.drink_water(water_amount)
        self.total_water_drunk += water_amount
        
        # Update streak
        current_date = time.strftime('%Y-%m-%d')
        if self.last_drink_date != current_date:
            if self.last_drink_date:
                # Check if it's consecutive
                yesterday = time.strftime('%Y-%m-%d', 
                                        time.localtime(time.time() - 86400))
                if self.last_drink_date == yesterday:
                    self.streak_days += 1
                else:
                    self.streak_days = 1
            else:
                self.streak_days = 1
            self.last_drink_date = current_date
            
        # Generate achievement
        if self.achievement_timer <= 0:
            achievement = self.ai_manager.generate_achievement(water_amount, self.streak_days)
            self.show_achievement(achievement)
            
        # Add water particles
        self.add_particles(self.current_mascot.x, self.current_mascot.y, 'water')
        
        # Mascot speaks about drinking
        if not self.mascot_speaking:
            context = f"User just drank {water_amount}ml of water!"
            self.mascot_speak(self.ai_manager.generate_conversation("", "", context))
            
    def show_achievement(self, achievement_text):
        """Show achievement popup"""
        self.achievement_popup = achievement_text
        self.achievement_timer = 5.0
        
    def update(self, dt):
        """Update game state"""
        if self.playing_brick:
            # Update brick game
            if self.brick_game:
                self.brick_game.handle_events()
                self.brick_game.update(dt)
                if not self.brick_game.running:
                    self.exit_brick_game()
            return
            
        if self.paused:
            return
            
        # Update mascot
        self.current_mascot.update(dt)
        
        # Update sensor data (less frequently for performance)
        if int(time.time() * 10) % 2 == 0:  # Update every 0.2 seconds instead of every frame
            self.update_sensor_data()
        
        # Update particles
        self.update_particles()
        
        # Update timers
        self.speech_timer -= dt
        if self.speech_timer <= 0:
            self.mascot_speaking = False
            
        self.achievement_timer -= dt
        
        # Auto-save every 30 seconds
        if int(time.time()) % 30 == 0:
            self.current_mascot.save_state()
            
    def draw(self):
        """Draw everything to screen"""
        if self.playing_brick:
            # Draw brick game
            if self.brick_game:
                self.brick_game.draw()
                pygame.display.flip()
            return
            
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw mascot
        self.current_mascot.draw(self.screen)
        
        # Draw hearts
        self.draw_hearts()
        
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
        
    def draw_hearts(self):
        """Draw hearts for mascot affection (vertical layout)"""
        heart_size = 20
        heart_spacing = 25
        heart_x = SCREEN_WIDTH - 30
        start_y = 20
        
        for i in range(self.hearts):
            heart_y = start_y + (i * heart_spacing)
            self.draw_heart(heart_x, heart_y, heart_size)
            
    def draw_heart(self, x, y, size):
        """Draw a single heart"""
        points = [
            (x, y + size//2),
            (x - size//2, y),
            (x - size//2, y - size//2),
            (x, y - size),
            (x + size//2, y - size//2),
            (x + size//2, y),
        ]
        pygame.draw.polygon(self.screen, WHITE, points)
        
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
        bubble_x = self.current_mascot.x - bubble_width // 2
        bubble_y = self.current_mascot.y - self.current_mascot.size // 2 - bubble_height - 20
        
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
        tail_x = self.current_mascot.x
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