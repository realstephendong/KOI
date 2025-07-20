#!/bin/bash

# Raspberry Pi Deployment Script for Tamagotchi Water Bottle
# This script sets up the environment and runs the application

echo "🔧 Setting up Tamagotchi Water Bottle for Raspberry Pi..."

# Check if we're on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo; then
    echo "❌ This script is designed for Raspberry Pi only!"
    exit 1
fi

echo "✅ Raspberry Pi detected"

# Install required packages
echo "📦 Installing required packages..."
sudo apt-get update
sudo apt-get install -y python3-pip python3-pygame python3-smbus

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip3 install gpiozero python-dotenv

# Enable I2C interface
echo "🔌 Enabling I2C interface..."
sudo raspi-config nonint do_i2c 0

# Set display rotation for vertical orientation
echo "🖥️  Setting display rotation for vertical orientation..."
sudo raspi-config nonint do_rotate 1  # 90 degrees for vertical display

# Create startup script
echo "🚀 Creating startup script..."
cat > ~/start_tamagotchi.sh << 'EOF'
#!/bin/bash
cd /home/pi/KOI
python3 main_raspberry_pi.py
EOF

chmod +x ~/start_tamagotchi.sh

# Add to autostart (optional)
echo "🤔 Would you like to add the application to autostart? (y/n)"
read -r response
if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    echo "📝 Adding to autostart..."
    cat >> ~/.bashrc << 'EOF'

# Start Tamagotchi Water Bottle on login
if [[ -z $DISPLAY ]] && [[ $(tty) = /dev/tty1 ]]; then
    cd /home/pi/KOI
    python3 main_raspberry_pi.py
fi
EOF
    echo "✅ Added to autostart"
fi

echo "🎉 Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Connect your buttons:"
echo "   - Yellow button to GPIO 17"
echo "   - Blue button to GPIO 27"
echo "2. Connect your MPU6050 sensor:"
echo "   - VCC to 3.3V"
echo "   - GND to GND"
echo "   - SCL to GPIO3 (SCL)"
echo "   - SDA to GPIO2 (SDA)"
echo "3. Run the application:"
echo "   ./start_tamagotchi.sh"
echo ""
echo "🔧 To run manually: python3 main_raspberry_pi.py" 