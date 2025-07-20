#!/usr/bin/env python3
"""
Pong Game for Tamagotchi Water Bottle
Pixel-art style Pong game with simple controls
"""

import pygame
import random
import math
from config import *

class PongGame:
    def __init__(self, screen):
        self.screen = screen
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        
        # Game state
        self.running = True
        self.score = 0
        self.high_score = 0
        self.game_over = False
        self.paused = False
        
        # Paddle settings
        self.paddle_width = 15
        self.paddle_height = 80
        self.paddle_speed = 8
        self.paddle_y = self.height // 2 - self.paddle_height // 2
        self.paddle_x = 50
        
        # Ball settings
        self.ball_size = 8
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_speed_x = 5
        self.ball_speed_y = 3
        self.ball_direction = random.choice([-1, 1])
        
        # AI opponent
        self.ai_paddle_x = self.width - 50 - self.paddle_width
        self.ai_paddle_y = self.height // 2 - self.paddle_height // 2
        self.ai_speed = 4
        
        # Game settings
        self.difficulty = 1.0
        self.max_difficulty = 3.0
        self.difficulty_increase = 0.1
        
        # Visual effects
        self.particles = []
        self.score_flash_timer = 0
        
        # Button controls (will be handled by main game)
        self.paddle_moving_up = False
        self.paddle_moving_down = False
        
    def handle_events(self):
        """Handle pygame events (now handled by main game)"""
        # Events are now handled by the main game
        pass
        
    def update(self, dt):
        """Update game state"""
        if self.paused or self.game_over:
            return
            
        # Update paddle movement (now controlled by main game buttons)
        # The main game will call move_paddle_up() and move_paddle_down()
        
        # Update AI opponent
        self.update_ai()
        
        # Update ball
        self.update_ball()
        
        # Update particles
        self.update_particles()
        
        # Update timers
        self.score_flash_timer -= dt
        
    def move_paddle_up(self):
        """Move paddle up (called by main game)"""
        self.paddle_y -= self.paddle_speed
        self.paddle_y = max(0, self.paddle_y)
        
    def move_paddle_down(self):
        """Move paddle down (called by main game)"""
        self.paddle_y += self.paddle_speed
        self.paddle_y = min(self.height - self.paddle_height, self.paddle_y)
        
    def update_ai(self):
        """Update AI opponent movement"""
        # Simple AI: follow the ball
        target_y = self.ball_y - self.paddle_height // 2
        
        if self.ai_paddle_y < target_y:
            self.ai_paddle_y += self.ai_speed * self.difficulty
        elif self.ai_paddle_y > target_y:
            self.ai_paddle_y -= self.ai_speed * self.difficulty
            
        # Keep AI paddle on screen
        self.ai_paddle_y = max(0, min(self.height - self.paddle_height, self.ai_paddle_y))
        
    def update_ball(self):
        """Update ball movement and collisions (optimized)"""
        # Move ball
        self.ball_x += self.ball_speed_x * self.ball_direction
        self.ball_y += self.ball_speed_y
        
        # Ball collision with top and bottom
        if self.ball_y <= 0 or self.ball_y >= self.height - self.ball_size:
            self.ball_speed_y = -self.ball_speed_y
            # Only add particles occasionally for performance
            if random.random() < 0.3:
                self.add_particles(self.ball_x, self.ball_y, 'bounce')
            
        # Ball collision with player paddle (optimized collision detection)
        if (self.ball_x <= self.paddle_x + self.paddle_width and 
            self.ball_x >= self.paddle_x and
            self.ball_y >= self.paddle_y and 
            self.ball_y <= self.paddle_y + self.paddle_height):
            
            self.ball_direction = 1
            self.ball_speed_x = min(8, self.ball_speed_x + 0.5)
            self.add_particles(self.ball_x, self.ball_y, 'hit')
            
        # Ball collision with AI paddle (optimized collision detection)
        if (self.ball_x >= self.ai_paddle_x and 
            self.ball_x <= self.ai_paddle_x + self.paddle_width and
            self.ball_y >= self.ai_paddle_y and 
            self.ball_y <= self.ai_paddle_y + self.paddle_height):
            
            self.ball_direction = -1
            self.ball_speed_x = min(8, self.ball_speed_x + 0.5)
            self.add_particles(self.ball_x, self.ball_y, 'hit')
            
        # Ball goes past AI paddle (player scores)
        if self.ball_x >= self.width:
            self.score += 1
            self.high_score = max(self.high_score, self.score)
            self.score_flash_timer = 0.5
            self.reset_ball()
            self.increase_difficulty()
            
        # Ball goes past player paddle (game over)
        if self.ball_x <= 0:
            self.game_over = True
            
    def reset_ball(self):
        """Reset ball to center"""
        self.ball_x = self.width // 2
        self.ball_y = self.height // 2
        self.ball_direction = random.choice([-1, 1])
        self.ball_speed_x = 5
        self.ball_speed_y = random.uniform(-3, 3)
        
    def increase_difficulty(self):
        """Increase game difficulty"""
        self.difficulty = min(self.max_difficulty, self.difficulty + self.difficulty_increase)
        
    def reset_game(self):
        """Reset game state"""
        self.score = 0
        self.game_over = False
        self.paused = False
        self.difficulty = 1.0
        self.reset_ball()
        self.paddle_y = self.height // 2 - self.paddle_height // 2
        self.ai_paddle_y = self.height // 2 - self.paddle_height // 2
        self.particles.clear()
        
    def add_particles(self, x, y, particle_type):
        """Add particle effects (optimized for performance)"""
        # Limit particles for better performance
        if len(self.particles) > 15:
            return
            
        colors = {
            'bounce': WHITE,
            'hit': LIGHT_GRAY
        }
        
        for _ in range(3):  # Reduced from 5 to 3
            particle = {
                'x': x + random.uniform(-10, 10),
                'y': y + random.uniform(-10, 10),
                'vx': random.uniform(-3, 3),
                'vy': random.uniform(-3, 3),
                'life': 20,  # Reduced from 30 to 20
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
        # Clear screen
        self.screen.fill(BLACK)
        
        # Draw center line
        center_x = self.width // 2
        for y in range(0, self.height, 20):
            pygame.draw.rect(self.screen, GRAY, (center_x - 2, y, 4, 10))
            
        # Draw paddles
        self.draw_paddle(self.paddle_x, self.paddle_y, WHITE)
        self.draw_paddle(self.ai_paddle_x, self.ai_paddle_y, LIGHT_GRAY)
        
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
            
        # Draw pause screen
        if self.paused:
            self.draw_pause_screen()
            
    def draw_paddle(self, x, y, color):
        """Draw a paddle with pixel-art style"""
        paddle_rect = pygame.Rect(x, y, self.paddle_width, self.paddle_height)
        pygame.draw.rect(self.screen, color, paddle_rect)
        pygame.draw.rect(self.screen, BLACK, paddle_rect, 2)
        
        # Pixel-art highlight
        highlight_rect = pygame.Rect(x + 1, y + 1, self.paddle_width - 2, self.paddle_height - 2)
        pygame.draw.rect(self.screen, LIGHT_GRAY, highlight_rect, 1)
        
    def draw_particles(self):
        """Draw particle effects"""
        for particle in self.particles:
            alpha = particle['life'] / 30.0
            color = particle['color']
            pygame.draw.circle(self.screen, color, 
                             (int(particle['x']), int(particle['y'])), 2)
                             
    def draw_ui(self):
        """Draw UI elements"""
        font = pygame.font.Font(None, 36)
        
        # Draw score
        score_color = WHITE if self.score_flash_timer <= 0 else LIGHT_GRAY
        score_text = font.render(f"SCORE: {self.score}", True, score_color)
        self.screen.blit(score_text, (20, 20))
        
        # Draw high score
        high_score_text = font.render(f"HIGH: {self.high_score}", True, GRAY)
        self.screen.blit(high_score_text, (20, 60))
        
        # Draw difficulty
        diff_text = font.render(f"LEVEL: {int(self.difficulty)}", True, GRAY)
        self.screen.blit(diff_text, (20, 100))
        
        # Draw controls
        controls_font = pygame.font.Font(None, 24)
        controls_text = controls_font.render("WASD or ARROWS to move", True, GRAY)
        self.screen.blit(controls_text, (20, self.height - 60))
        
        pause_text = controls_font.render("SPACE to pause, R to reset", True, GRAY)
        self.screen.blit(pause_text, (20, self.height - 40))
        
    def draw_game_over(self):
        """Draw game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game over text
        font = pygame.font.Font(None, 72)
        text = font.render("GAME OVER", True, WHITE)
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2 - 50))
        self.screen.blit(text, text_rect)
        
        # Final score
        font = pygame.font.Font(None, 48)
        score_text = font.render(f"Final Score: {self.score}", True, LIGHT_GRAY)
        score_rect = score_text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(score_text, score_rect)
        
        # Instructions
        font = pygame.font.Font(None, 32)
        restart_text = font.render("Press SPACE to restart", True, GRAY)
        restart_rect = restart_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
        self.screen.blit(restart_text, restart_rect)
        
    def draw_pause_screen(self):
        """Draw pause screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.width, self.height))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Pause text
        font = pygame.font.Font(None, 72)
        text = font.render("PAUSED", True, WHITE)
        text_rect = text.get_rect(center=(self.width // 2, self.height // 2))
        self.screen.blit(text, text_rect)
        
    def run(self):
        """Main game loop"""
        clock = pygame.time.Clock()
        
        while self.running:
            dt = clock.tick(FPS) / 1000.0
            
            self.handle_events()
            self.update(dt)
            self.draw()
            
            pygame.display.flip()
            
        return self.score  # Return final score 