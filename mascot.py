import pygame
import json
import time
import random
import math
from enum import Enum
from config import *

class MascotState(Enum):
    IDLE = "idle"
    DRINKING = "drinking"
    HAPPY = "happy"
    SAD = "sad"
    SLEEPING = "sleeping"
    PLAYING = "playing"
    DIZZY = "dizzy"
    EATING = "eating"

class Mascot:
    def __init__(self, mascot_type='koi'):
        self.type = mascot_type
        self.config = MASCOTS[mascot_type]
        self.name = self.config['name']
        
        # Health and stats
        self.health = self.config['base_health']
        self.max_health = self.config['base_health']
        self.hydration_level = 100
        self.last_drink_time = time.time()
        self.last_health_update = time.time()
        
        # State management
        self.current_state = MascotState.IDLE
        self.state_timer = 0
        self.animation_frame = 0
        self.animation_speed = 0.1
        
        # Emotions and reactions
        self.emotion = 'happy'
        self.reaction_timer = 0
        self.is_dizzy = False
        self.dizzy_timer = 0
        
        # AI-generated features
        self.ai_features = []
        self.last_ai_update = 0
        
        # Animation properties
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT // 2
        self.size = 100
        self.bounce_offset = 0
        self.bounce_speed = 0.05
        
    def update(self, dt, water_drunk=0, is_shaking=False):
        """Update mascot state and animations"""
        current_time = time.time()
        
        # Update health based on time
        if current_time - self.last_health_update >= 60:  # Every minute
            self.health -= self.config['health_decay_rate']
            self.health = max(0, self.health)
            self.last_health_update = current_time
        
        # Handle water drinking
        if water_drunk > 0:
            self.drink_water(water_drunk)
        
        # Handle shaking
        if is_shaking:
            self.make_dizzy()
        
        # Update state timers
        self.state_timer += dt
        self.reaction_timer -= dt
        self.dizzy_timer -= dt
        
        # Update animations
        self.update_animation(dt)
        
        # Auto-transition states
        self.update_state_transitions()
        
        # Update emotion based on health
        self.update_emotion()
        
    def drink_water(self, amount):
        """Handle water drinking event"""
        self.health = min(self.max_health, self.health + amount)
        self.hydration_level = min(100, self.hydration_level + amount)
        self.last_drink_time = time.time()
        
        # Trigger happy reaction
        self.current_state = MascotState.DRINKING
        self.state_timer = 0
        self.reaction_timer = 3.0  # Show reaction for 3 seconds
        
    def make_dizzy(self):
        """Handle bottle shaking"""
        self.is_dizzy = True
        self.dizzy_timer = 5.0  # Dizzy for 5 seconds
        self.current_state = MascotState.DIZZY
        self.state_timer = 0
        
    def update_animation(self, dt):
        """Update animation frames and effects"""
        self.animation_frame += self.animation_speed
        
        # Bouncing effect
        self.bounce_offset = math.sin(time.time() * self.bounce_speed) * 5
        
        # Dizzy rotation effect
        if self.is_dizzy and self.dizzy_timer > 0:
            self.rotation = (time.time() * 360) % 360
        else:
            self.rotation = 0
            self.is_dizzy = False
            
    def update_state_transitions(self):
        """Handle automatic state transitions"""
        if self.current_state == MascotState.DRINKING and self.state_timer > 2:
            self.current_state = MascotState.HAPPY
            
        if self.current_state == MascotState.HAPPY and self.state_timer > 3:
            self.current_state = MascotState.IDLE
            
        if self.current_state == MascotState.DIZZY and self.dizzy_timer <= 0:
            self.current_state = MascotState.IDLE
            
    def update_emotion(self):
        """Update emotion based on health level"""
        health_percentage = (self.health / self.max_health) * 100
        
        for state, data in HEALTH_STATES.items():
            if health_percentage >= data['min']:
                self.emotion = data['emotion']
                break
                
    def get_health_color(self):
        """Get color based on current health"""
        health_percentage = (self.health / self.max_health) * 100
        for state, data in HEALTH_STATES.items():
            if health_percentage >= data['min']:
                return data['color']
        return RED
        
    def draw(self, screen):
        """Draw the mascot with pixel-art style"""
        # Draw mascot body with pixel-art style
        body_rect = pygame.Rect(self.x - self.size // 2, self.y - self.size // 2, 
                               self.size, self.size)
        
        # Draw body with border
        pygame.draw.rect(screen, self.config['color'], body_rect)
        pygame.draw.rect(screen, BLACK, body_rect, 2)
        
        # Draw pixel-art details based on state
        if self.current_state == MascotState.HAPPY:
            self.draw_happy_face(screen)
        elif self.current_state == MascotState.SAD:
            self.draw_sad_face(screen)
        elif self.current_state == MascotState.PLAYING:
            self.draw_playing_face(screen)
        elif self.current_state == MascotState.DIZZY:
            self.draw_dizzy_face(screen)
        else:
            self.draw_normal_face(screen)
            
        # Draw health bar with pixel-art style
        self.draw_health_bar(screen)
        
    def draw_normal_face(self, screen):
        """Draw normal face with pixel-art style"""
        # Eyes
        eye_size = 4
        left_eye_x = self.x - 8
        right_eye_x = self.x + 8
        eye_y = self.y - 5
        
        pygame.draw.rect(screen, BLACK, (left_eye_x, eye_y, eye_size, eye_size))
        pygame.draw.rect(screen, BLACK, (right_eye_x, eye_y, eye_size, eye_size))
        
        # Mouth (small line)
        mouth_y = self.y + 8
        pygame.draw.line(screen, BLACK, (self.x - 6, mouth_y), (self.x + 6, mouth_y), 2)
        
    def draw_happy_face(self, screen):
        """Draw happy face with pixel-art style"""
        # Eyes
        eye_size = 4
        left_eye_x = self.x - 8
        right_eye_x = self.x + 8
        eye_y = self.y - 5
        
        pygame.draw.rect(screen, BLACK, (left_eye_x, eye_y, eye_size, eye_size))
        pygame.draw.rect(screen, BLACK, (right_eye_x, eye_y, eye_size, eye_size))
        
        # Happy mouth (curve)
        mouth_points = [
            (self.x - 8, self.y + 8),
            (self.x - 4, self.y + 12),
            (self.x, self.y + 10),
            (self.x + 4, self.y + 12),
            (self.x + 8, self.y + 8)
        ]
        pygame.draw.lines(screen, BLACK, False, mouth_points, 2)
        
    def draw_sad_face(self, screen):
        """Draw sad face with pixel-art style"""
        # Eyes
        eye_size = 4
        left_eye_x = self.x - 8
        right_eye_x = self.x + 8
        eye_y = self.y - 5
        
        pygame.draw.rect(screen, BLACK, (left_eye_x, eye_y, eye_size, eye_size))
        pygame.draw.rect(screen, BLACK, (right_eye_x, eye_y, eye_size, eye_size))
        
        # Sad mouth (inverted curve)
        mouth_points = [
            (self.x - 8, self.y + 12),
            (self.x - 4, self.y + 8),
            (self.x, self.y + 10),
            (self.x + 4, self.y + 8),
            (self.x + 8, self.y + 12)
        ]
        pygame.draw.lines(screen, BLACK, False, mouth_points, 2)
        
    def draw_playing_face(self, screen):
        """Draw playing face with pixel-art style"""
        # Eyes (squinted)
        eye_size = 2
        left_eye_x = self.x - 8
        right_eye_x = self.x + 8
        eye_y = self.y - 4
        
        pygame.draw.rect(screen, BLACK, (left_eye_x, eye_y, eye_size, eye_size))
        pygame.draw.rect(screen, BLACK, (right_eye_x, eye_y, eye_size, eye_size))
        
        # Excited mouth (wide)
        mouth_y = self.y + 8
        pygame.draw.line(screen, BLACK, (self.x - 10, mouth_y), (self.x + 10, mouth_y), 3)
        
    def draw_dizzy_face(self, screen):
        """Draw dizzy face with pixel-art style"""
        # Swirling eyes
        eye_size = 3
        left_eye_x = self.x - 8
        right_eye_x = self.x + 8
        eye_y = self.y - 5
        
        # Draw X eyes
        pygame.draw.line(screen, BLACK, (left_eye_x, eye_y), (left_eye_x + eye_size, eye_y + eye_size), 2)
        pygame.draw.line(screen, BLACK, (left_eye_x + eye_size, eye_y), (left_eye_x, eye_y + eye_size), 2)
        
        pygame.draw.line(screen, BLACK, (right_eye_x, eye_y), (right_eye_x + eye_size, eye_y + eye_size), 2)
        pygame.draw.line(screen, BLACK, (right_eye_x + eye_size, eye_y), (right_eye_x, eye_y + eye_size), 2)
        
        # Confused mouth
        mouth_y = self.y + 8
        pygame.draw.line(screen, BLACK, (self.x - 4, mouth_y), (self.x + 4, mouth_y), 2)
        
    def draw_health_bar(self, screen):
        """Draw health bar with pixel-art style"""
        bar_width = 200
        bar_height = 20
        bar_x = self.x - bar_width // 2
        bar_y = self.y + self.size // 2 + 20
        
        # Background
        pygame.draw.rect(screen, DARK_GRAY, (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(screen, BLACK, (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Health fill
        health_width = int((self.health / self.max_health) * bar_width)
        health_color = self.get_health_color()
        if health_width > 0:
            pygame.draw.rect(screen, health_color, (bar_x + 2, bar_y + 2, health_width - 4, bar_height - 4))
        
        # Pixel-art border effect
        pygame.draw.rect(screen, LIGHT_GRAY, (bar_x + 1, bar_y + 1, bar_width - 2, bar_height - 2), 1)
        
    def save_state(self):
        """Save mascot state to file"""
        state = {
            'type': self.type,
            'health': self.health,
            'hydration_level': self.hydration_level,
            'last_drink_time': self.last_drink_time,
            'ai_features': self.ai_features
        }
        
        with open(SAVE_FILE, 'w') as f:
            json.dump(state, f)
            
    def load_state(self):
        """Load mascot state from file"""
        try:
            with open(SAVE_FILE, 'r') as f:
                state = json.load(f)
                
            self.health = state.get('health', self.max_health)
            self.hydration_level = state.get('hydration_level', 100)
            self.last_drink_time = state.get('last_drink_time', time.time())
            self.ai_features = state.get('ai_features', [])
            
        except FileNotFoundError:
            pass  # Use default values if no save file exists 