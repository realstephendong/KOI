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
    DRINKING = "drinking"  # Added drinking state

class Mascot:
    def __init__(self, mascot_type='koi'):
        self.type = mascot_type
        self.config = MASCOTS[mascot_type]
        self.name = self.config['name']
        
        # Health and stats
        self.hearts = 0
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

        # Drinking state
        self.is_drinking = False
        self.drinking_amount_left = 0
        self.drinking_rate = 20  # units per second (adjust as needed)
        self.drinking_total = 0
        
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

        # Handle shaking (prioritize dizzy state)
        if is_shaking and not self.is_dizzy:
            self.make_dizzy()

        # Handle drinking (prioritize drinking state)
        if self.is_drinking:
            drink_step = self.drinking_rate * dt
            if self.drinking_amount_left > 0:
                actual_drink = min(drink_step, self.drinking_amount_left)
                self.health = min(self.max_health, self.health + actual_drink)
                self.hydration_level = min(100, self.hydration_level + actual_drink)
                self.drinking_amount_left -= actual_drink
                self.last_drink_time = current_time
                self.current_state = MascotState.DRINKING
            else:
                self.is_drinking = False
                self.current_state = MascotState.IDLE

        # Only allow state transitions if not dizzy or drinking
        if not self.is_dizzy and not self.is_drinking:
            # Update health based on time
            if current_time - self.last_health_update >= 2:  # Every 2 seconds
                self.health -= self.config['health_decay_rate']
                self.health = max(0, self.health)
                self.last_health_update = current_time

            if self.health == 0:
                self.kill()
            elif self.health <= 40:
                self.make_sad()
            else:
                self.make_idle()

        # Handle water drinking event (start drinking if water_drunk > 0 and not already drinking)
        if water_drunk > 0 and not self.is_drinking:
            self.drink_water(water_drunk)

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
        """Handle water drinking event (smoothly)"""
        self.is_drinking = True
        self.drinking_amount_left = amount
        self.drinking_total = amount
        self.state_timer = 0
        self.current_state = MascotState.DRINKING
        
    def make_dizzy(self):
        """Handle bottle shaking"""
        self.is_dizzy = True
        self.dizzy_timer = 0  # Dizzy for 0 seconds
        self.current_state = MascotState.DIZZY
        self.state_timer = 0

    def kill(self):
        """Kill pet"""
        self.current_state = MascotState.DEATH
    
    def make_sad(self):
        """Make sad"""
        self.current_state = MascotState.SAD

        if self.health == 40:
            self.hearts = max(0, self.hearts - 1)
    
    def make_idle(self):
        """Make idel"""
        self.current_state = MascotState.IDLE
        
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
            self.is_dizzy = False
        if self.current_state == MascotState.DRINKING and not self.is_drinking:
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
        if self.current_state == MascotState.DEATH:
            return "death"
        elif self.current_state == MascotState.SAD:
            return "sad"
        elif self.current_state == MascotState.DIZZY:
            return "dizzy"
        elif self.current_state == MascotState.DRINKING:
            return "drinking"
        else:
            return "idle"
            
    def get_animation_frame(self):
        """Get current animation frame for UI to use"""
        if self.current_state == MascotState.DEATH or self.current_state == MascotState.DIZZY:
            return 0
        else:
            return int(self.animation_frame) % 2  # Assuming 2-frame animations
        
    def save_state(self):
        """Save mascot state to file"""
        state = {
            'type': self.type,
            'health': self.health,
            'hearts': self.hearts,
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
            self.hearts = state.get('hearts', 0)
            self.last_drink_time = state.get('last_drink_time', time.time())
            self.ai_features = state.get('ai_features', [])
            
        except FileNotFoundError:
            pass  # Use default values if no save file exists 