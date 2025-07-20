#!/bin/bash
"""
I2C Troubleshooting Script for "Resource temporarily unavailable" error
This script helps fix I2C bus locking issues on Raspberry Pi
"""

echo "=================================================="
echo "I2C Troubleshooting - Resource Busy Fix"
echo "=================================================="
echo

# Check what processes are using I2C
echo "Step 1: Checking processes using I2C..."
if command -v lsof &> /dev/null; then
    echo "Processes using /dev/i2c-1:"
    sudo lsof /dev/i2c-1 2>/dev/null || echo "No processes found using /dev/i2c-1"
else
    echo "lsof not available, checking with ps..."
    ps aux | grep -i i2c | grep -v grep || echo "No I2C processes found"
fi

echo
echo "Step 2: Checking I2C kernel modules..."
lsmod | grep i2c

echo
echo "Step 3: Checking I2C device permissions..."
ls -la /dev/i2c-*

echo
echo "Step 4: Testing I2C scan..."
echo "Running: sudo i2cdetect -y 1"
sudo i2cdetect -y 1

echo
echo "Step 5: Attempting I2C reset..."
echo "This will reload the I2C kernel modules..."

# Stop any services that might be using I2C
echo "Stopping potential I2C services..."
sudo systemctl stop bluetooth 2>/dev/null || true
sudo systemctl stop hciuart 2>/dev/null || true

# Reload I2C modules
echo "Reloading I2C modules..."
sudo modprobe -r i2c_dev 2>/dev/null || true
sudo modprobe -r i2c_bcm2835 2>/dev/null || true
sleep 1
sudo modprobe i2c_bcm2835
sudo modprobe i2c_dev

echo "Waiting for I2C to stabilize..."
sleep 2

echo
echo "Step 6: Testing I2C after reset..."
sudo i2cdetect -y 1

echo
echo "=================================================="
echo "I2C Reset Complete!"
echo "=================================================="
echo
echo "Try running your water tracker again:"
echo "python3 gy521_water_tracker.py"
echo
echo "If the issue persists:"
echo "1. Reboot the system: sudo reboot"
echo "2. Check for hardware conflicts"
echo "3. Try a different GY521 module"
echo "4. Check wiring connections"
