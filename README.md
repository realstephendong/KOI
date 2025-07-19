# KOI - GY521 Water Consumption Tracker

A smart water consumption tracking system using a GY521 (MPU6050) gyroscope module on Raspberry Pi with QNX 8.0.

## Overview

This project uses a GY521 accelerometer module to detect when a water bottle is tilted for drinking and calculates water consumption based on tilt angle and duration. The system is specifically designed to work with QNX 8.0 on Raspberry Pi.

## Files

- **`gy521_water_tracker.py`** - Main water consumption tracker (QNX compatible)
- **`gy521_test.py`** - Test script to verify sensor functionality (QNX compatible)
- **`SETUP.md`** - Detailed setup instructions
- **`install.sh`** - Automated installation script
- **`transfer_to_pi.sh`** - Script to transfer files to Raspberry Pi
- **`requirements.txt`** - Python dependencies

## Quick Start

1. **Setup**: Follow instructions in `SETUP.md`
2. **Test**: Run `python3 gy521_test.py` to verify sensor
3. **Track**: Run `python3 gy521_water_tracker.py` to start tracking

## Features

- Real-time tilt detection and water consumption calculation
- Automatic calibration for accurate readings
- Session-based tracking with start/stop detection
- QNX 8.0 compatibility with basic smbus library
- Configurable thresholds and flow rates

## Hardware Requirements

- Raspberry Pi 4 with QNX 8.0
- GY521 (MPU6050) gyroscope module
- Standard I2C connections (VCC, GND, SCL, SDA) 