#!/bin/bash

echo "KOI - GY521 Water Tracking Setup Script"
echo "======================================"
echo

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "Warning: This script is designed for Raspberry Pi"
    echo "You may need to modify it for your system"
    echo
fi

# Update package list
echo "Updating package list..."
sudo apt update

# Install required packages
echo "Installing required packages..."
sudo apt install -y python3-pip i2c-tools

# Enable I2C interface
echo "Enabling I2C interface..."
if ! grep -q "i2c_arm=on" /boot/config.txt; then
    echo "i2c_arm=on" | sudo tee -a /boot/config.txt
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
    echo "I2C enabled in config.txt"
else
    echo "I2C already enabled in config.txt"
fi

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install smbus2

# Check I2C devices
echo
echo "Checking I2C devices..."
if ls /dev/i2c* >/dev/null 2>&1; then
    echo "I2C devices found:"
    ls /dev/i2c*
    echo
    echo "Scanning I2C bus for devices..."
    sudo i2cdetect -y 1
else
    echo "No I2C devices found. You may need to reboot."
fi

echo
echo "Setup complete!"
echo
echo "Next steps:"
echo "1. Reboot your Raspberry Pi: sudo reboot"
echo "2. Test the sensor: python3 gy521_test.py"
echo "3. Run the water tracker: python3 gy521_water_tracker.py"
echo
echo "Make sure your GY521 module is connected:"
echo "  VCC -> 3.3V or 5V"
echo "  GND -> GND"
echo "  SDA -> GPIO2"
echo "  SCL -> GPIO3" 