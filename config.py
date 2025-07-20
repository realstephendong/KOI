import os
from dotenv import load_dotenv

load_dotenv()

# Screen Configuration - Vertical Mounting
SCREEN_WIDTH = 480   # Rotated from 800
SCREEN_HEIGHT = 800  # Rotated from 600
FPS = 60

# Colors - Black and White Theme
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (128, 128, 128)
LIGHT_GRAY = (200, 200, 200)
DARK_GRAY = (64, 64, 64)

# Legacy color mappings for compatibility
BLUE = GRAY
LIGHT_BLUE = LIGHT_GRAY
GREEN = WHITE
RED = BLACK
YELLOW = WHITE
PINK = LIGHT_GRAY
PURPLE = DARK_GRAY

# Pixel Art Style
PIXEL_SIZE = 2
BORDER_THICKNESS = 3
CORNER_RADIUS = 0  # Sharp corners for pixel art

# Physical Button Configuration
# For testing on computer: 'a' and 'd' keys
# For Raspberry Pi: GPIO pins or other input methods
BUTTON_LEFT = 'a'    # Pet/Exit button
BUTTON_RIGHT = 'd'   # Start game button

BUTTON_LEFT_PI = 'yellow button'
BUTTON_RIGHT_PI = 'blue button' 

# Button Function Modes
BUTTON_MODE_MAIN = 'main'      # Main screen
BUTTON_MODE_BRICK = 'brick'    # Brick breaker game controls
BUTTON_MODE_MENU = 'menu'      # Menu navigation
BUTTON_MODE_DIALOG = 'dialog'  # Dialog/confirmation

# Mascot Configuration
MASCOTS = {
    'koi': {
        'name': 'Koi',
        'color': WHITE,
        'personality': 'energetic and playful',
        'favorite_food': 'water drops',
        'base_health': 100,
        'health_decay_rate': 10  # per minute
    },
    'soy': {
        'name': 'Soy',
        'color': LIGHT_GRAY,
        'personality': 'calm and caring',
        'favorite_food': 'water bubbles',
        'base_health': 100,
        'health_decay_rate': 10  # per minute
    },
    'joy': {
        'name': 'Joy',
        'color': WHITE,
        'personality': 'angry and mean',
        'favorite_food': 'rain',
        'base_health': 100,
        'health_decay_rate': 10  # per minute
    }
}

# Health States
HEALTH_STATES = {
    'excellent': {'min': 80, 'emotion': 'happy', 'color': WHITE},
    'good': {'min': 60, 'emotion': 'content', 'color': LIGHT_GRAY},
    'okay': {'min': 40, 'emotion': 'worried', 'color': GRAY},
    'poor': {'min': 20, 'emotion': 'sad', 'color': DARK_GRAY},
    'critical': {'min': 0, 'emotion': 'dying', 'color': BLACK}
}

# Drinking Detection
DRINKING_THRESHOLD = 45  # degrees
DRINKING_DURATION = 2.0  # seconds
WATER_PER_DRINK = 10  # ml

# Local AI Response Configuration
AI_UPDATE_INTERVAL = 300  # 5 minutes
SPEECH_DURATION = 4.0  # seconds to show speech bubble

# Game Configuration
BRICK_GAME_LIVES = 3
BRICK_GAME_BALL_SPEED = 5
BRICK_GAME_PADDLE_SPEED = 8
BRICK_GAME_TILT_SENSITIVITY = 0.5

# File Paths
ASSETS_DIR = 'assets'
SAVE_FILE = 'mascot_save.json'
CALIBRATION_FILE = 'sensor_calibration.json'

# Sensor Configuration
SENSOR_UPDATE_RATE = 60  # Hz
SENSOR_SIMULATION_MODE = True  # Set to False on Raspberry Pi
MPU6050_ADDRESS = 0x68
SMBUS_BUS = 1

# Particle Effects
MAX_PARTICLES = 20
PARTICLE_LIFETIME = 60  # frames
PARTICLE_SPEED = 3

# Achievement System
ACHIEVEMENT_COOLDOWN = 300  # seconds between achievements
MIN_WATER_FOR_ACHIEVEMENT = 50  # ml 