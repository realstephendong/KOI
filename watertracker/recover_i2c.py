#!/usr/bin/env python3
"""
Simple I2C Recovery Tool for GY521/MPU6050
This script attempts to recover from "Resource temporarily unavailable" errors
"""

import smbus
import time
import sys
import subprocess

def run_command(cmd):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip(), result.stderr.strip(), result.returncode
    except Exception as e:
        return "", str(e), -1

def check_i2c_processes():
    """Check what processes are using I2C"""
    print("🔍 Checking for processes using I2C...")
    
    stdout, stderr, code = run_command("sudo lsof /dev/i2c-1 2>/dev/null")
    if stdout:
        print("⚠️  Processes using /dev/i2c-1:")
        print(stdout)
        return True
    else:
        print("✅ No processes found using /dev/i2c-1")
        return False

def reset_i2c():
    """Reset I2C modules"""
    print("\n🔄 Resetting I2C modules...")
    
    commands = [
        "sudo modprobe -r i2c_dev",
        "sudo modprobe -r i2c_bcm2835",
        "sleep 1",
        "sudo modprobe i2c_bcm2835", 
        "sudo modprobe i2c_dev"
    ]
    
    for cmd in commands:
        print(f"   Running: {cmd}")
        stdout, stderr, code = run_command(cmd)
        if code != 0 and "sleep" not in cmd:
            print(f"   Warning: {stderr}")
        time.sleep(0.5)
    
    print("✅ I2C modules reset complete")

def test_i2c_simple():
    """Simple I2C test without complex logic"""
    print("\n🧪 Testing I2C connection...")
    
    max_attempts = 5
    for attempt in range(max_attempts):
        try:
            print(f"   Attempt {attempt + 1}/{max_attempts}...")
            
            # Try to open I2C bus
            bus = smbus.SMBus(1)
            time.sleep(0.2)  # Wait after opening
            
            # Try to read from MPU6050
            who_am_i = bus.read_byte_data(0x68, 0x75)
            print(f"   ✅ WHO_AM_I: 0x{who_am_i:02X}")
            
            if who_am_i == 0x68:
                print("   ✅ MPU6050 communication successful!")
                bus.close()
                return True
            else:
                print(f"   ⚠️  Unexpected WHO_AM_I value: 0x{who_am_i:02X}")
            
            bus.close()
            
        except OSError as e:
            if e.errno == 11:
                print(f"   ❌ Resource busy (attempt {attempt + 1})")
                if attempt < max_attempts - 1:
                    print("   ⏳ Waiting 2 seconds before retry...")
                    time.sleep(2)
            else:
                print(f"   ❌ Error: {e}")
        except Exception as e:
            print(f"   ❌ Error: {e}")
            
        # Close bus if it's still open
        try:
            bus.close()
        except:
            pass
    
    return False

def main():
    """Main recovery function"""
    print("KOI Water Tracker - I2C Recovery Tool")
    print("=" * 50)
    
    # Check for conflicting processes
    has_conflicts = check_i2c_processes()
    
    # Test I2C first
    if test_i2c_simple():
        print("\n🎉 I2C is working! You can run the water tracker now.")
        return True
    
    # If failed, try reset
    print("\n💊 I2C test failed. Attempting recovery...")
    reset_i2c()
    
    # Wait a bit after reset
    print("\n⏳ Waiting for I2C to stabilize...")
    time.sleep(3)
    
    # Test again
    if test_i2c_simple():
        print("\n🎉 I2C recovery successful! You can run the water tracker now.")
        return True
    else:
        print("\n❌ I2C recovery failed.")
        print("\n🔧 Additional troubleshooting:")
        print("1. Reboot the system: sudo reboot")
        print("2. Check wiring connections")
        print("3. Try running: sudo i2cdetect -y 1")
        print("4. Disable conflicting services")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Recovery cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
