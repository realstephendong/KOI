# 🍓 Raspberry Pi Deployment Guide

## Overview
This guide will help you deploy the Tamagotchi Water Bottle application on your Raspberry Pi with proper display orientation and GPIO button support.

## 🎯 Issues Fixed

### 1. Display Orientation Issue
- **Problem**: Window appeared vertical but stretched horizontally
- **Solution**: Created `config_raspberry_pi.py` with vertical dimensions (600x1024) and 90° rotation
- **Result**: Proper vertical/portrait display on Raspberry Pi (appears sideways on screen)

### 2. Sensor Manager Errors
- **Problem**: Constant "❌ Error updating sensor data" spam
- **Solution**: Fixed `update_sensor_data()` method to use correct sensor manager methods
- **Result**: Clean operation with proper sensor integration

## 📋 Prerequisites

### Hardware Requirements
- Raspberry Pi (3, 4, or 5 recommended)
- Touchscreen LCD display (optional but recommended)
- 2x Push buttons (Yellow and Blue)
- MPU6050 (GY521) gyroscope sensor
- Breadboard and jumper wires

### Software Requirements
- Raspberry Pi OS (latest version)
- Python 3.7+
- Internet connection for package installation

## 🔧 Installation

### Option 1: Automated Setup (Recommended)
```bash
# Copy your project files to Raspberry Pi
scp -r /path/to/KOI pi@your-pi-ip:/home/pi/

# SSH into your Raspberry Pi
ssh pi@your-pi-ip

# Navigate to project directory
cd /home/pi/KOI

# Run the deployment script
./deploy_raspberry_pi.sh
```

### Option 2: Manual Setup
```bash
# Update system
sudo apt-get update
sudo apt-get upgrade

# Install required packages
sudo apt-get install -y python3-pip python3-pygame python3-smbus

# Install Python dependencies
pip3 install gpiozero python-dotenv

# Enable I2C interface
sudo raspi-config nonint do_i2c 0

# Reboot to apply changes
sudo reboot
```

## 🔌 Hardware Connections

### Button Connections
| Button | GPIO Pin | Function |
|--------|----------|----------|
| Yellow | GPIO 17  | Pet/Switch Mascot |
| Blue   | GPIO 27  | Start Game/Stats |

### MPU6050 Sensor Connections
| Sensor Pin | Raspberry Pi Pin | Function |
|------------|------------------|----------|
| VCC        | 3.3V            | Power    |
| GND        | GND             | Ground   |
| SCL        | GPIO3 (SCL)     | I2C Clock|
| SDA        | GPIO2 (SDA)     | I2C Data |

## 🚀 Running the Application

### Quick Start
```bash
cd /home/pi/KOI
python3 main_raspberry_pi.py
```

### Using the Startup Script
```bash
./start_tamagotchi.sh
```

### Auto-start on Boot
The deployment script can configure the application to start automatically when the Raspberry Pi boots.

## 🎮 Button Controls

### Yellow Button (GPIO 17)
- **Single Press**: Pet the mascot
- **Double Press**: Switch between Koi and Soy mascots
- **Triple Press**: Special interaction with health boost

### Blue Button (GPIO 27)
- **Single Press**: Start Brick Breaker game
- **Double Press**: Show drinking statistics
- **Triple Press**: Show settings menu

## 🖥️ Display Configuration

### Current Settings
- **Resolution**: 600x1024 (vertical/portrait orientation)
- **Display Rotation**: 90 degrees (appears sideways on 1024x600 screen)
- **Fullscreen**: Enabled
- **Orientation**: Vertical (tall display)

### Customizing Display
Edit `config_raspberry_pi.py` to change:
```python
# Display settings
SCREEN_WIDTH = 600   # Vertical width
SCREEN_HEIGHT = 1024 # Vertical height
PI_FULLSCREEN = True # Set to False for windowed mode
PI_DISPLAY_ROTATION = 1  # 1 = 90°, 2 = 180°, 3 = 270°
```

### Rotating Display
To rotate the display, uncomment and modify in `deploy_raspberry_pi.sh`:
```bash
# 90 degrees
sudo raspi-config nonint do_rotate 1

# 180 degrees  
sudo raspi-config nonint do_rotate 2

# 270 degrees
sudo raspi-config nonint do_rotate 3
```

## 🔍 Troubleshooting

### Display Issues
```bash
# Check display configuration
sudo raspi-config

# Test display orientation
vcgencmd get_mem gpu
```

### GPIO Button Issues
```bash
# Check GPIO permissions
sudo usermod -a -G gpio pi

# Test GPIO buttons
python3 -c "from gpiozero import Button; b = Button(17); print('Button 17:', b.value)"
```

### Sensor Issues
```bash
# Check I2C devices
i2cdetect -y 1

# Test sensor communication
python3 -c "import smbus; bus = smbus.SMBus(1); print('I2C bus available')"
```

### Performance Issues
```bash
# Check system resources
htop

# Monitor temperature
vcgencmd measure_temp
```

## 📁 File Structure
```
KOI/
├── main_raspberry_pi.py      # Pi-specific main file
├── config_raspberry_pi.py    # Pi-specific configuration
├── deploy_raspberry_pi.sh    # Deployment script
├── start_tamagotchi.sh       # Startup script
├── main.py                   # Development version
├── config.py                 # Development configuration
└── [other project files]
```

## 🔄 Updates

### Updating the Application
```bash
cd /home/pi/KOI
git pull origin main  # If using git
# Or copy new files manually
```

### Updating Dependencies
```bash
pip3 install --upgrade gpiozero python-dotenv pygame
```

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all hardware connections
3. Ensure all dependencies are installed
4. Check system logs: `journalctl -xe`

## 🎉 Success Indicators

When everything is working correctly, you should see:
- ✅ "🔌 GPIO library found - Running on Raspberry Pi"
- ✅ "🔧 Raspberry Pi fullscreen mode enabled"
- ✅ "🎮 GPIO Button controls: Yellow (GPIO 17) for pet, Blue (GPIO 27) for game"
- ✅ No sensor error spam
- ✅ Proper button response with press counting
- ✅ Fullscreen display without stretching

Happy coding! 🐟💧 