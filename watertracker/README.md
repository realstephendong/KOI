# KOI Water Tracker - Raspberry Pi 5 Edition

A water consumption tracker using a GY521 (MPU6050) gyroscope module to detect when you're drinking from a water bottle.

## Hardware Requirements

- **Raspberry Pi 5** with Raspberry Pi OS (Bookworm or later)
- **GY521 (MPU6050)** gyroscope/accelerometer module
- Jumper wires for connections
- Water bottle to track

## Wiring Connections

| GY521 Pin | Raspberry Pi 5 | Physical Pin |
|-----------|----------------|--------------|
| VCC       | 3.3V or 5V     | 1 or 2       |
| GND       | GND            | 6            |
| SCL       | GPIO3 (SCL)    | 5            |
| SDA       | GPIO2 (SDA)    | 3            |

## Quick Setup

### 1. Automated Setup (Recommended)
```bash
chmod +x setup_pi5.sh
./setup_pi5.sh
```

### 2. Manual Setup
```bash
# Enable I2C
sudo raspi-config
# -> Interface Options -> I2C -> Enable

# Install dependencies
sudo apt update
sudo apt install i2c-tools python3-smbus python3-pip

# Add user to i2c group
sudo usermod -a -G i2c $USER

# Reboot
sudo reboot
```

### 3. Test Connection
```bash
# After reboot, test I2C connection
python3 test_connection_pi5.py

# Or manually scan
sudo i2cdetect -y 1
```

### 4. Run Water Tracker
```bash
python3 gy521_water_tracker.py
```

## Features

- **Automatic I2C Detection**: Tries both bus 0 and 1, addresses 0x68 and 0x69
- **Smart Calibration**: Automatically calibrates when level
- **Drinking Detection**: Detects tilting motion for drinking
- **Water Volume Calculation**: Estimates water consumption based on tilt angle and duration
- **Shake Detection**: Detects when bottle is being shaken
- **Real-time Monitoring**: Live status updates

## Configuration

You can adjust these parameters in the code:

```python
self.TILT_THRESHOLD = 70.0        # Minimum tilt angle to detect drinking (degrees)
self.DRINKING_TIMEOUT = 2.0       # Time before ending drinking session (seconds)
self.MIN_DRINKING_TIME = 0.3      # Minimum time for valid drinking session (seconds)
self.BASE_FLOW_RATE = 0.5         # Base water flow rate (ml/second)
```

## Troubleshooting

### Common Issues

**"Remote I/O error" or device not found:**
1. Check wiring connections
2. Enable I2C: `sudo raspi-config`
3. Scan for devices: `sudo i2cdetect -y 1`
4. Try different address (some modules use 0x69)

**Permission denied:**
1. Add to i2c group: `sudo usermod -a -G i2c $USER`
2. Logout and login again

**Import errors:**
```bash
sudo apt install python3-smbus
# or
pip3 install smbus2
```

### Diagnostic Commands

```bash
# Check I2C is enabled
lsmod | grep i2c

# List I2C devices
ls /dev/i2c-*

# Scan for I2C devices
sudo i2cdetect -y 1

# Check user groups
groups $USER

# Test GY521 connection
python3 test_connection_pi5.py
```

## How It Works

1. **Calibration**: When started, keep the bottle level for 4 seconds
2. **Detection**: Tilt the bottle past the threshold angle to start drinking detection
3. **Calculation**: Water consumption is calculated based on:
   - Tilt angle (steeper = faster flow)
   - Duration of tilting
   - Flow rate model

## Output Example

```
KOI Water Tracker - Raspberry Pi 5 Edition
==================================================

✅ MPU6050 found on I2C bus 1 at address 0x68
✅ MPU6050 initialized successfully for Raspberry Pi OS
Calibrating sensor...
Keep the bottle level and still for 4 seconds...
Calibration complete!

Tilt threshold: 70.0°
Noise threshold: 8.2°
Tilt the bottle to start tracking water consumption...

Tilt - X: -2.1°, Y: 1.4° (Drinking: 1.4°) | IDLE | Total: 0.0 ml
Drinking detected! Starting session... (Tilt: 75.3°)
Tilt - X: -15.2°, Y: 75.3° (Drinking: 75.3°) | DRINKING | Session: 2.3 ml | Total: 2.3 ml
Drinking session ended!
Session duration: 1.8 seconds
Water consumed this session: 4.1 ml
Total water consumed: 4.1 ml
```

## Integration with KOI Project

This water tracker can be integrated with the main KOI pet project:

```python
from watertracker.gy521_water_tracker import GY521WaterTracker

# Initialize tracker
tracker = GY521WaterTracker()

# Check water consumption
total_water = tracker.get_total_water_consumed()
is_drinking = tracker.is_currently_drinking()

# Reset counter
tracker.reset_water_consumption()
```

## Raspberry Pi 5 Specific Notes

- Uses I2C bus 1 by default (same as Pi 4)
- GPIO pins are the same as previous models
- Raspberry Pi OS Bookworm recommended
- Hardware I2C is more reliable than software I2C

## License

Part of the KOI virtual pet project. 