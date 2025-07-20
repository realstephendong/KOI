#!/usr/bin/env python3
"""
Vertical Brick Breaker Game for Tamagotchi Water Bottle
Uses bottle tilt for paddle control
"""

import pygame
import random
import math
from config import *

class BrickGame:
    def __init__(self, screen, sensor_manager, app_width=600, app_height=1024):
        self.screen = screen
        self.sensor_manager = sensor_manager
        
        # Use provided dimensions or fallback to config
        self.width = app_width if app_width else SCREEN_WIDTH
        self.height = app_height if app_height else SCREEN_HEIGHT
        
        print(f"🎮 Brick game initialized with dimensions: {self.width}x{self.height}")
        
        # Game state
        self.running = True
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.paused = False
        self.level = 1
        
        # Paddle settings (horizontal in vertical game)
        self.paddle_width = 80
        self.paddle_height = 15
        self.paddle_x = self.width // 2 - self.paddle_width // 2
        self.paddle_y = self.height - 50
        self.paddle_speed = 5
        
        # Ball settings
        self.ball_size = 8
        self.ball_x = self.width // 2
        self.ball_y = self.height - 100
        self.ball_speed_x = 4
        self.ball_speed_y = -4
        self.ball_launched = False
        
        # Brick settings - More blocks for better gameplay
        self.brick_width = 50  # Smaller bricks to fit more
        self.brick_height = 18
        self.brick_rows = 12   # More rows
        self.brick_cols = 10   # More columns
        self.bricks = []
        self.setup_bricks()
        
        # Game settings
        self.lives = 3
        self.max_lives = 3
        
        # Visual effects
        self.particles = []
        self.score_flash_timer = 0
        
        # Tilt control
        self.tilt_sensitivity = 2.0
        self.last_tilt = 0
        
        # Game loop timing
        self.last_update = pygame.time.get_ticks()
        
        # Auto-launch timer (launch ball after 2 seconds if not manually launched)
        self.auto_launch_timer = 2.0
        
    def setup_bricks(self):
        """Setup brick layout"""
        self.bricks = []
        
        # Calculate spacing to fit all bricks
        total_brick_width = self.brick_cols * self.brick_width
        total_brick_height = self.brick_rows * self.brick_height
        
        # Calculate margins to center the brick layout
        margin_x = (self.width - total_brick_width) // 2
        margin_y = 50  # Top margin
        
        # Add some spacing between bricks
        brick_spacing_x = 2
        brick_spacing_y = 2
        
        for row in range(self.brick_rows):
            for col in range(self.brick_cols):
                brick = {
                    'x': margin_x + col * (self.brick_width + brick_spacing_x),
                    'y': margin_y + row * (self.brick_height + brick_spacing_y),
                    'width': self.brick_width,
                    'height': self.brick_height,
                    'color': self.get_brick_color(row),
                    'active': True
                }
                self.bricks.append(brick)
                
        print(f"🧱 Created {len(self.bricks)} bricks ({self.brick_rows} rows × {self.brick_cols} columns)")
        
    def get_brick_color(self, row):
        """Get brick color based on row"""
        colors = [WHITE, LIGHT_GRAY, GRAY, DARK_GRAY]
        return colors[row % len(colors)]
        
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == ord(BUTTON_LEFT):
                    self.running = False
                elif event.key == pygame.K_SPACE or event.key == ord(BUTTON_RIGHT):
                    if not self.ball_launched:
                        self.launch_ball()
                        
    def launch_ball(self):
        """Launch the ball from paddle"""
        if not self.ball_launched:
            self.ball_launched = True
            self.ball_speed_y = -4
            self.ball_speed_x = random.uniform(-3, 3)
            print("🎾 Ball launched!")
            
    def update(self, dt):
        """Update game state"""
        if self.paused or self.game_over:
            return
            
        # Update auto-launch timer
        if not self.ball_launched:
            self.auto_launch_timer -= dt
            if self.auto_launch_timer <= 0:
                self.launch_ball()
            
        # Update paddle position based on tilt
        self.update_paddle_from_tilt()
        
        # Update ball
        self.update_ball()
        
        # Update particles
        self.update_particles()
        
        # Update timers
        self.score_flash_timer -= dt
        
        # Check for level completion
        if self.check_level_complete():
            self.next_level()
            
    def update_paddle_from_tilt(self):
        """Update paddle position based on bottle tilt"""
        sensor_data = self.sensor_manager.get_sensor_status()
        
        # Use tilt data to move paddle
        if 'tilt_x' in sensor_data:
            tilt = sensor_data['tilt_x'] * self.tilt_sensitivity
            self.paddle_x += tilt
            
            # Keep paddle on screen
            self.paddle_x = max(0, min(self.width - self.paddle_width, self.paddle_x))
            
    def update_ball(self):
        """Update ball movement and collisions"""
        if not self.ball_launched:
            # Ball follows paddle
            self.ball_x = self.paddle_x + self.paddle_width // 2
            return
            
        # Move ball
        self.ball_x += self.ball_speed_x
        self.ball_y += self.ball_speed_y
        
        # Ball collision with left and right walls
        if self.ball_x <= 0 or self.ball_x >= self.width - self.ball_size:
            self.ball_speed_x = -self.ball_speed_x
            self.add_particles(self.ball_x, self.ball_y, 'bounce')
            
        # Ball collision with top wall
        if self.ball_y <= 0:
            self.ball_speed_y = -self.ball_speed_y
            self.add_particles(self.ball_x, self.ball_y, 'bounce')
            
        # Ball collision with paddle
        if (self.ball_y >= self.paddle_y - self.ball_size and 
            self.ball_y <= self.paddle_y + self.paddle_height and
            self.ball_x >= self.paddle_x and 
            self.ball_x <= self.paddle_x + self.paddle_width):
            
            # Calculate hit position for angle
            hit_pos = (self.ball_x - self.paddle_x) / self.paddle_width
            angle = (hit_pos - 0.5) * 2  # -1 to 1
            
            self.ball_speed_y = -abs(self.ball_speed_y)  # Always go up
            self.ball_speed_x = angle * 6  # Angle based on hit position
            
            self.add_particles(self.ball_x, self.ball_y, 'hit')
            
        # Ball collision with bricks
        self.check_brick_collisions()
        
        # Ball goes past paddle (lose life)
        if self.ball_y >= self.height:
            self.lose_life()
            
    def check_brick_collisions(self):
        """Check ball collision with bricks"""
        for brick in self.bricks:
            if not brick['active']:
                continue
                
            if (self.ball_x >= brick['x'] and 
                self.ball_x <= brick['x'] + brick['width'] and
                self.ball_y >= brick['y'] and 
                self.ball_y <= brick['y'] + brick['height']):
                
                # Destroy brick
                brick['active'] = False
                self.score += 10
                self.high_score = max(self.high_score, self.score)
                self.score_flash_timer = 0.5
                
                # Bounce ball
                if (self.ball_x < brick['x'] or self.ball_x > brick['x'] + brick['width']):
                    self.ball_speed_x = -self.ball_speed_x
                else:
                    self.ball_speed_y = -self.ball_speed_y
                    
                self.add_particles(brick['x'] + brick['width']//2, 
                                 brick['y'] + brick['height']//2, 'break')
                break
                
    def lose_life(self):
        """Lose a life and reset ball"""
        self.lives -= 1
        self.ball_launched = False
        self.ball_x = self.paddle_x + self.paddle_width // 2
        self.ball_y = self.paddle_y - self.ball_size
        
        # Reset auto-launch timer
        self.auto_launch_timer = 2.0
        
        if self.lives <= 0:
            self.game_over = True
            
    def check_level_complete(self):
        """Check if all bricks are destroyed"""
        return all(not brick['active'] for brick in self.bricks)
        
    def next_level(self):
        """Start next level"""
        self.level += 1
        self.ball_launched = False
        self.ball_x = self.paddle_x + self.paddle_width // 2
        self.ball_y = self.paddle_y - self.ball_size
        
        # Reset auto-launch timer
        self.auto_launch_timer = 2.0
        
        # Increase difficulty
        self.ball_speed_x = min(8, self.ball_speed_x + 0.5)
        self.ball_speed_y = min(8, abs(self.ball_speed_y) + 0.5)
        
        # Setup new bricks
        self.setup_bricks()
        
    def add_particles(self, x, y, particle_type):
        """Add particle effects"""
        if len(self.particles) > 20:
            return
            
        colors = {
            'bounce': WHITE,
            'hit': LIGHT_GRAY,
            'break': GRAY
        }
        
        for _ in range(5):
            particle = {
                'x': x + random.uniform(-10, 10),
                'y': y + random.uniform(-10, 10),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'life': 30,
                'color': colors.get(particle_type, WHITE)
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
                
    def draw(self):
        """Draw the game"""
        # Calculate delta time
        current_time = pygame.time.get_ticks()
        dt = (current_time - self.last_update) / 1000.0
        self.last_update = current_time
        
        # Update game state
        self.update(dt)
        
        # Handle events
        self.handle_events()
        
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw bricks
        self.draw_bricks()
        
        # Draw paddle
        self.draw_paddle()
        
        # Draw ball
        pygame.draw.rect(self.screen, WHITE, 
                        (self.ball_x, self.ball_y, self.ball_size, self.ball_size))
        
        # Draw particles
        self.draw_particles()
        
        # Draw UI
        self.draw_ui()
        
        # Draw game over screen
        if self.game_over:
            self.draw_game_over()
            
    def draw_bricks(self):
        """Draw active bricks"""
        for brick in self.bricks:
            if brick['active']:
                pygame.draw.rect(self.screen, brick['color'], 
                               (brick['x'], brick['y'], brick['width'], brick['height']))
                pygame.draw.rect(self.screen, BLACK, 
                               (brick['x'], brick['y'], brick['width'], brick['height']), 1)
                
    def draw_paddle(self):
        """Draw paddle with pixel-art style"""
        paddle_rect = pygame.Rect(self.paddle_x, self.paddle_y, 
                                 self.paddle_width, self.paddle_height)
        pygame.draw.rect(self.screen, WHITE, paddle_rect)
        pygame.draw.rect(self.screen, BLACK, paddle_rect, 2)
        
        # Pixel-art highlight
        highlight_rect = pygame.Rect(self.paddle_x + 1, self.paddle_y + 1, 
                                   self.paddle_width - 2, self.paddle_height - 2)
        pygame.draw.rect(self.screen, LIGHT_GRAY, highlight_rect, 1)
        
    def draw_particles(self):
        """Draw particle effects"""
        for particle in self.particles:
            pygame.draw.circle(self.screen, particle['color'], 
                             (int(particle['x']), int(particle['y'])), 2)
                             
    def draw_ui(self):
        """Draw UI elements"""
        font = pygame.font.Font(None, 24)
        
        # Draw score
        score_color = WHITE if self.score_flash_timer <= 0 else LIGHT_GRAY
        score_text = font.render(f"SCORE: {self.score}", True, score_color)
        self.screen.blit(score_text, (10, 10))
        
        # Draw level
        level_text = font.render(f"LEVEL: {self.level}", True, GRAY)
        self.screen.blit(level_text, (10, 35))
        
        # Draw lives
        lives_text = font.render(f"LIVES: {self.lives}", True, GRAY)
        self.screen.blit(lives_text, (10, 60))
        
        # Draw controls
        controls_font = pygame.font.Font(None, 18)
        controls_text = controls_font.render("Tilt bottle to move paddle", True, GRAY)
        self.screen.blit(controls_text, (10, self.height - 60))
        
        # Draw launch instructions
        if not self.ball_launched:
            launch_text = controls_font.render("Press SPACE or D to launch ball", True, WHITE)
            self.screen.blit(launch_text, (10, self.height - 40))
            
            # Show auto-launch countdown
            if self.auto_launch_timer > 0:
                countdown_text = controls_font.render(f"Auto-launch in {self.auto_launch_timer:.1f}s", True, LIGHT_GRAY)
                self.screen.blit(countdown_text, (10, self.height - 20))
        else:
            exit_text = controls_font.render(f"Press {BUTTON_LEFT.upper()} to exit", True, GRAY)
            self.screen.blit(exit_text, (10, self.height - 20))
        
    def draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        font = pygame.font.Font(None, 48)
        text = font.render("GAME OVER", True, WHITE)
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(text, text_rect)
        
        # Final score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Final Score: {self.score}", True, LIGHT_GRAY)
        score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(score_text, score_rect)
        
        # Instructions
        font = pygame.font.Font(None, 24)
        restart_text = font.render(f"Press {BUTTON_LEFT.upper()} to exit", True, GRAY)
        restart_rect = restart_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(restart_text, restart_rect) 