# GY521 Water Tracking Setup Guide for Raspberry Pi

## Hardware Requirements

- **Raspberry Pi 4**: (or Pi 3, Pi Zero W)
- **GY521 Module**: MPU6050 gyroscope/accelerometer
- **Breadboard**: For prototyping
- **Jumper Wires**: For connections
- **Power Supply**: For Raspberry Pi

## Wiring Diagram

```
Raspberry Pi 4    GY521 Module
---------------    -----------
3.3V or 5V    -->  VCC
GND           -->  GND
GPIO2 (SDA)   -->  SDA
GPIO3 (SCL)   -->  SCL
```

## Pin Connections

| Raspberry Pi Pin | GY521 Pin | Description |
|------------------|-----------|-------------|
| 3.3V or 5V      | VCC       | Power supply |
| GND             | GND       | Ground |
| GPIO2 (SDA)     | SDA       | I2C Data line |
| GPIO3 (SCL)     | SCL       | I2C Clock line |

## Setup Instructions

### 1. Hardware Setup
1. Connect the GY521 module to Raspberry Pi according to the wiring diagram above
2. Ensure all connections are secure
3. Power on your Raspberry Pi

### 2. Enable I2C Interface
1. Open terminal on Raspberry Pi
2. Run: `sudo raspi-config`
3. Navigate to "Interface Options" → "I2C"
4. Enable I2C and reboot if prompted
5. Verify I2C is enabled: `ls /dev/i2c*`

### 3. Install Dependencies
1. Update package list: `sudo apt update`
2. Install Python dependencies:
   ```bash
   pip3 install -r requirements.txt
   ```
   Or install manually:
   ```bash
   pip3 install smbus2
   ```

### 4. Test I2C Connection
1. Check if GY521 is detected:
   ```bash
   sudo i2cdetect -y 1
   ```
2. You should see device `68` in the output

### 5. Testing the Sensor
1. Run the test script:
   ```bash
   python3 gy521_test.py
   ```
2. Keep the sensor level and still
3. Observe the readings - they should be stable when level
4. Tilt the sensor in different directions to see angle changes
5. Press Ctrl+C to stop the test

### 6. Water Tracking Setup
1. Once the test script works correctly, run the main tracker:
   ```bash
   python3 gy521_water_tracker.py
   ```
2. The system will automatically calibrate on startup
3. Keep the bottle level during calibration
4. After calibration, tilt the bottle to test drinking detection
5. Press Ctrl+C to stop the tracker

## Calibration

The system automatically calibrates on startup. During calibration:
- Keep the water bottle level and completely still
- Wait for the "Calibration complete!" message
- The system will store offset values to compensate for sensor bias

## Configuration

You can adjust these parameters in `gy521_water_tracker.py`:

```python
self.TILT_THRESHOLD = 15.0        # Minimum tilt angle to trigger drinking (degrees)
self.DRINKING_TIMEOUT = 5.0       # Max time for drinking session (seconds)
self.MIN_DRINKING_TIME = 0.5      # Min time to be considered drinking (seconds)
self.BASE_FLOW_RATE = 0.5         # Base flow rate (ml/sec at 45 degrees)
self.ANGLE_MULTIPLIER = 1.5       # Flow rate multiplier per 10 degrees
```

## Troubleshooting

### Common Issues:

1. **No readings from sensor**
   - Check wiring connections
   - Verify I2C address (should be 0x68)
   - Ensure I2C is enabled: `sudo i2cdetect -y 1`
   - Check if device appears as "68" in the scan

2. **"Failed to initialize I2C bus"**
   - Enable I2C interface: `sudo raspi-config` → Interface Options → I2C
   - Reboot after enabling I2C
   - Install i2c-tools: `sudo apt install i2c-tools`

3. **"Failed to initialize MPU6050"**
   - Check power connections (VCC to 3.3V or 5V)
   - Verify I2C connections (SDA to GPIO2, SCL to GPIO3)
   - Check if device is detected: `sudo i2cdetect -y 1`

4. **Unstable readings**
   - Ensure sensor is mounted securely
   - Check for vibration or movement
   - Recalibrate the sensor by restarting the program

5. **Incorrect tilt angles**
   - Verify sensor orientation
   - Check calibration values in output
   - Ensure bottle is level during calibration

6. **False drinking detection**
   - Increase `TILT_THRESHOLD` value in the code
   - Adjust `DRINKING_TIMEOUT` value
   - Check for environmental vibration

## Expected Output

### Test Script Output (`gy521_test.py`):
```
GY521 Test Script
================
I2C bus initialized successfully
MPU6050 initialized successfully
MPU6050 initialized!
Keep the sensor level and still for testing...

Raw Accel - X: 0.012g, Y: -0.008g, Z: 1.001g | Tilt - X: 2.1°, Y: 1.8°, Magnitude: 2.8°
```

### Water Tracker Output (`gy521_water_tracker.py`):
```
KOI - GY521 Water Consumption Tracker
I2C bus initialized successfully
MPU6050 initialized successfully
Calibrating sensor...
Keep the bottle level and still...
Calibration complete!
Calibration offsets - X: 0.012, Y: -0.008
Initialization complete!
Tilt the bottle to start tracking water consumption...

Tilt - X: 2.1°, Y: 1.8°, Magnitude: 2.8° | IDLE | Total: 0.0 ml
Drinking detected! Starting session...
Tilt - X: 25.3°, Y: 18.7°, Magnitude: 31.2° | DRINKING | Session: 12.5 ml | Total: 12.5 ml
Drinking session ended!
Session duration: 3.2 seconds
Water consumed this session: 15.8 ml
Total water consumed: 15.8 ml
```

## Next Steps

Once the GY521 water tracking is working:
1. Mount the sensor securely to your water bottle
2. Test with actual drinking sessions
3. Fine-tune the calibration and threshold values
4. Integrate with LCD display for the koi fish mascot
5. Add data logging and daily tracking features
6. Consider running as a service: `nohup python3 gy521_water_tracker.py &`

## Quick Start Commands

```bash
# Run automated setup
./install.sh

# Test basic sensor functionality
python3 gy521_test.py

# Run water tracking system
python3 gy521_water_tracker.py

# Check I2C devices
sudo i2cdetect -y 1
``` 