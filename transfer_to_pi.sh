#!/bin/bash
# Script to transfer files to Raspberry Pi with QNX

# Configuration - Update these with your Pi's details
PI_USER="qnxuser"
PI_IP="YOUR_PI_IP_HERE"  # Replace with your Pi's IP address
PI_PATH="~/KOI-water-tracker-feature"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Transferring files to Raspberry Pi...${NC}"

# Transfer the main files
echo -e "${YELLOW}Transferring water tracker files...${NC}"
scp gy521_water_tracker.py $PI_USER@$PI_IP:$PI_PATH/
scp gy521_test.py $PI_USER@$PI_IP:$PI_PATH/

# Transfer other important files
echo -e "${YELLOW}Transferring setup files...${NC}"
scp requirements.txt $PI_USER@$PI_IP:$PI_PATH/
scp SETUP.md $PI_USER@$PI_IP:$PI_PATH/
scp README.md $PI_USER@$PI_IP:$PI_PATH/

echo -e "${GREEN}Transfer complete!${NC}"
echo -e "${YELLOW}You can now run on the Pi:${NC}"
echo -e "  python3 gy521_test.py"
echo -e "  python3 gy521_water_tracker.py" 