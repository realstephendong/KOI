#!/bin/bash
"""
KOI Water Tracker Setup Script for Raspberry Pi 5 with Raspberry Pi OS
This script automates the setup process for the GY521 water tracker.
"""

echo "=================================================="
echo "KOI Water Tracker Setup for Raspberry Pi 5"
echo "=================================================="
echo

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This doesn't appear to be a Raspberry Pi"
    echo "   This setup is designed for Raspberry Pi OS"
    echo
fi

# Function to check if a command was successful
check_success() {
    if [ $? -eq 0 ]; then
        echo "✅ $1"
    else
        echo "❌ $1 failed"
        exit 1
    fi
}

echo "Step 1: Updating system packages..."
sudo apt update && sudo apt upgrade -y
check_success "System update"

echo
echo "Step 2: Installing I2C tools and Python dependencies..."
sudo apt install -y i2c-tools python3-smbus python3-pip python3-dev
check_success "Package installation"

echo
echo "Step 3: Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0  # 0 = enable, 1 = disable
check_success "I2C enable"

echo
echo "Step 4: Adding user to i2c group..."
sudo usermod -a -G i2c $USER
check_success "User group addition"

echo
echo "Step 5: Installing Python dependencies..."
pip3 install --user smbus2
check_success "Python dependencies"

echo
echo "Step 6: Checking I2C interface..."
if [ -e /dev/i2c-1 ]; then
    echo "✅ I2C interface /dev/i2c-1 exists"
else
    echo "⚠️  I2C interface /dev/i2c-1 not found"
    echo "   You may need to reboot for I2C to be enabled"
fi

echo
echo "Step 7: Testing I2C detection (if GY521 is connected)..."
echo "Scanning I2C bus 1 for devices..."
if command -v i2cdetect &> /dev/null; then
    sudo i2cdetect -y 1
    echo
    echo "Look for '68' or '69' in the grid above"
    echo "If you see either, your GY521 is detected!"
else
    echo "⚠️  i2cdetect not available, skipping scan"
fi

echo
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo
echo "Next steps:"
echo "1. 🔌 Connect your GY521 module:"
echo "   VCC -> Pin 1 (3.3V) or Pin 2 (5V)"
echo "   GND -> Pin 6 (GND)"
echo "   SCL -> Pin 5 (GPIO3/SCL)"
echo "   SDA -> Pin 3 (GPIO2/SDA)"
echo
echo "2. 🔄 Reboot to ensure I2C is fully enabled:"
echo "   sudo reboot"
echo
echo "3. 🧪 After reboot, test the connection:"
echo "   sudo i2cdetect -y 1"
echo
echo "4. 🚀 Run the water tracker:"
echo "   python3 gy521_water_tracker.py"
echo
echo "Troubleshooting:"
echo "- If no device found: Check wiring connections"
echo "- If permission denied: Logout and login after reboot"
echo "- If import errors: pip3 install --user smbus2"
echo
echo "Happy tracking! 🐟💧"
