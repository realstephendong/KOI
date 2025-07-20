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
        
        # Animation properties (for UI to use)
        self.bounce_offset = 0
        self.bounce_speed = 0.05
        self.rotation = 0
        
    def update(self, dt, water_drunk=0, is_shaking=False):
        """Update mascot state and animations"""
        current_time = time.time()
        
        # Update health based on time
        if current_time - self.last_health_update >= 5:  # Every 5 seconds
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
        
    def get_animation_state(self):
        """Get current animation state for UI to use"""
        if self.current_state == MascotState.HAPPY:
            return "happy"
        elif self.current_state == MascotState.DRINKING:
            return "drinking"
        elif self.current_state == MascotState.SAD:
            return "sad"
        elif self.current_state == MascotState.DIZZY:
            return "dizzy"
        else:
            return "idle"
            
    def get_animation_frame(self):
        """Get current animation frame for UI to use"""
        return int(self.animation_frame) % 2  # Assuming 2-frame animations
        
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