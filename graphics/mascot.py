import pygame
import json
import time
import random
import math
from enum import Enum
from config import *

class MascotState(Enum):
    IDLE = "idle"
    SAD = "sad"
    DIZZY = "dizzy"
    DEATH = "death"

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
        self.emotion = 'idle'
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
        if current_time - self.last_health_update >= 5:  # Every minute
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
        
        self.state_timer = 0
        
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