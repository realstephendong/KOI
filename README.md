# 🐟 Tamagotchi Water Bottle 🥤

A smart, interactive water bottle that encourages healthy hydration habits through gamification and AI-powered features. Meet Koi and Soy, your adorable digital companions who thrive on your water drinking habits!

## 🌟 Features

### 🎮 Core Gameplay
- **Two Unique Mascots**: Koi (energetic and playful) and Soy (calm and caring)
- **Real-time Health System**: Mascot health decreases over time, encouraging regular water intake
- **Emotional States**: Mascots change emotions based on health levels (happy → content → worried → sad → dying)
- **Interactive Touch Controls**: Pet, play, and interact with your mascots

### 🕹️ Mini-Games
- **Brick Breaker Game**: Play a vertical brick breaker mini-game, controlled by tilting the bottle. Paddle moves with tilt; mascots comment on your gameplay.

### 🧑‍🤝‍🧑 Mascots
- **Three Unique Mascots**: Koi (energetic and playful), Soy (calm and caring), and Joy (angry and mean)
- **Switch Mascot**: Cycle between Koi, Soy, and Joy with the pet button

### 🧠 AI-Powered Features
- **Dynamic Conversations**: Gemini AI generates personalized responses from your mascots
- **Random Activities**: AI creates unique mini-games and features every 5 minutes
- **Smart Achievements**: Personalized achievements based on drinking patterns and streaks
- **Fallback System**: Works offline with pre-programmed features
- **Personality-Driven Responses**: Each mascot has unique, personality-driven responses for petting, drinking, games, and achievements

### 📊 Health Tracking
- **Drinking Detection**: GY521 gyroscope detects tilt and duration for accurate water measurement
- **Daily Goals**: Track progress toward hydration targets
- **Streak System**: Maintain daily drinking streaks for rewards
- **Statistics Dashboard**: Visual progress tracking
- **Session-Based Drinking Detection**: Tracks each drinking session, with improved tilt/noise filtering and per-session water calculation
- **Shake Detection**: Mascots react (get dizzy) if the bottle is shaken

### 🎨 Visual Effects & UI
- **Centralized UI Controller**: Consistent mascot, health bar, and heart display
- **Speech Bubbles**: Mascots speak in custom speech bubbles with dynamic sizing and custom font
- **Custom Font Support**: Pixel-style font for UI and mini-games
- **Particle Systems**: Hearts, sparkles, and water droplets for visual feedback
- **Smooth Animations**: Bouncing, rotation, and state transitions
- **Health Bars**: Real-time visual health indicators
- **Achievement Popups**: Celebrate milestones with animated notifications

## 🛠️ Hardware Requirements

### Required Components
- **Raspberry Pi 5** with Raspberry Pi OS
- **Touchscreen LCD Display** (iPad-style monitor)
- **GY521 Gyroscope Module** (MPU6050)
- **Water Bottle** (compatible with sensor mounting)

### Optional Components
- **3D Printed Case** for electronics
- **Battery Pack** for portable operation
- **Speaker** for audio feedback

## 📦 Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd KOI
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up Environment Variables
Create a `.env` file in the project root:
```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

### 4. Configure Sensor
Connect the GY521 module to your Raspberry Pi:
- VCC → 3.3V
- GND → GND
- SCL → GPIO 3 (SCL)
- SDA → GPIO 2 (SDA)

### 5. Run the Application
```bash
python main_vertical_test.py
```

## 🎯 Usage Guide

### Basic Controls
- **Touch Screen**: Interact with mascots and UI elements
- **Escape Key**: Exit the application
- **Space Bar**: Pause/unpause the game
- **A Key**: Pet/switch mascot (desktop mode)
- **D Key**: Start mini-game/confirm (desktop mode)

### Mascot Interactions
- **Pet Button**: Give your mascot affection (+5 health)
- **Play Button**: Start AI-generated activities or mini-game
- **Switch Mascot**: Cycle between Koi, Soy, and Joy

### Mini-Game: Brick Breaker
- **Start Game**: Press the play button (or 'D' key)
- **Control Paddle**: Tilt the bottle left/right (or use keyboard in test mode)
- **Lives & Levels**: Progress through levels, avoid losing all lives
- **Mascot Commentary**: Mascots react to your gameplay

### Drinking Detection
1. **Tilt Detection**: Bottle must be tilted >45° for drinking detection
2. **Duration Tracking**: Must maintain tilt for 2+ seconds
3. **Water Calculation**: Amount based on tilt angle and duration
4. **Health Boost**: Drinking restores mascot health
- **Session Tracking**: Each drinking session is measured and reported
- **Shake Detection**: Shaking the bottle makes mascots dizzy

### AI Features
- **Automatic Updates**: New features generated every 5 minutes
- **Contextual Responses**: AI considers mascot personality and current state
- **Offline Mode**: Fallback features when AI is unavailable
- **Personality-Driven Responses**: Each mascot has unique responses for petting, drinking (small/large sips), game start/end, and achievements

## 🔧 Configuration

### Sensor Settings (`config.py`)
```python
DRINKING_THRESHOLD = 45  # degrees
DRINKING_DURATION = 2.0  # seconds
WATER_PER_DRINK = 10     # ml
```

### Mascot Personalities
```python
MASCOTS = {
    'koi': {
        'name': 'Koi',
        'personality': 'energetic and playful',
        'health_decay_rate': 0.5  # per minute
    },
    'soy': {
        'name': 'Soy', 
        'personality': 'calm and caring',
        'health_decay_rate': 0.3  # per minute
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
```

### Health States
```python
HEALTH_STATES = {
    'excellent': {'min': 80, 'emotion': 'happy'},
    'good': {'min': 60, 'emotion': 'content'},
    'okay': {'min': 40, 'emotion': 'worried'},
    'poor': {'min': 20, 'emotion': 'sad'},
    'critical': {'min': 0, 'emotion': 'dying'}
}
```

# Game Configuration
BRICK_GAME_LIVES = 3
BRICK_GAME_BALL_SPEED = 5
BRICK_GAME_PADDLE_SPEED = 8
BRICK_GAME_TILT_SENSITIVITY = 0.5

# Particle Effects
MAX_PARTICLES = 20
PARTICLE_LIFETIME = 60  # frames
PARTICLE_SPEED = 3

# Achievement System
ACHIEVEMENT_COOLDOWN = 300  # seconds between achievements
MIN_WATER_FOR_ACHIEVEMENT = 50  # ml

## 🎨 Customization

### Adding New Mascots
1. Add mascot configuration to `config.py`
2. Create custom sprites/animations
3. Update `mascot.py` with new behaviors

### Custom AI Prompts
Modify `ai_manager.py` to change:
- Feature generation prompts
- Conversation styles
- Achievement descriptions

### Visual Themes
- Modify colors in `config.py`
- Add custom particle effects
- Create new background patterns
- Add new mascots by updating `config.py`, creating sprites, and adding behaviors in `mascot.py` and responses in `ai_manager.py`
- Customize mini-game settings in `config.py`

## 🐛 Troubleshooting

### Sensor Issues
- **No Connection**: Check wiring and port settings
- **Inaccurate Readings**: Recalibrate sensor
- **False Positives**: Adjust thresholds in config

### Display Issues
- **Fullscreen Problems**: Modify display settings in `main.py`
- **Touch Not Working**: Check touchscreen drivers
- **Performance Issues**: Reduce FPS or particle count

### AI Features Not Working
- **API Key Missing**: Check `.env` file
- **Network Issues**: Features fall back to offline mode
- **Rate Limiting**: AI features have cooldown periods

## 🚀 Advanced Features

### Planned Enhancements
- **Multiplayer Mode**: Connect multiple bottles
- **Cloud Sync**: Save progress across devices
- **Custom Mascots**: User-created characters
- **Advanced Analytics**: Detailed health insights
- **Social Features**: Share achievements

### Development & Simulation Mode
```bash
# Run with sensor simulation (for desktop testing)
python main_vertical_test.py

# Debug mode with console output
python main_vertical_test.py --debug

# Custom config file
python main_vertical_test.py --config custom_config.py
```
- **Keyboard Controls**: Use 'A' (pet/switch mascot) and 'D' (play/confirm) for testing on desktop

## 📝 API Documentation

### Mascot Class
```python
mascot = Mascot('koi')
mascot.update(dt, water_drunk=10, is_shaking=False)
mascot.draw(screen)
mascot.save_state()
```

### Sensor Manager
```python
sensor = SensorManager()
sensor.connect()
data = sensor.update()
status = sensor.get_sensor_status()
```

### AI Manager
```python
ai = AIManager()
feature = ai.generate_random_feature(name, personality, health)
conversation = ai.generate_conversation(name, personality, context)
achievement = ai.generate_achievement(water_amount, streak_days)
```

### BrickGame Class
```python
brick_game = BrickGame(screen, sensor_manager)
brick_game.launch_ball()
brick_game.update(dt)
brick_game.draw()
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Gemini AI** for intelligent conversation and feature generation
- **Pygame** for the game engine
- **Raspberry Pi Foundation** for the hardware platform
- **Open Source Community** for various libraries and tools

## 📞 Support

For questions, issues, or feature requests:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the configuration options

---

**Stay hydrated and have fun with your digital companions! 💧🐟** 