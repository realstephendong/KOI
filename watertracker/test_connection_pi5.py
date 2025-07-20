#!/usr/bin/env python3
"""
Quick I2C Test for GY521 on Raspberry Pi 5 with Raspberry Pi OS
Run this to verify your GY521 module is properly connected.
"""

import sys
import time

# Check if we can import smbus
try:
    import smbus
    print("✅ smbus module imported successfully")
except ImportError:
    print("❌ smbus module not found")
    print("Install with: sudo apt install python3-smbus")
    print("Or: pip3 install smbus2")
    sys.exit(1)

def test_i2c_connection():
    """Test I2C connection to GY521/MPU6050"""
    print("\n🔍 Testing I2C Connection to GY521/MPU6050")
    print("=" * 50)
    
    # Test different buses and addresses
    buses = [1, 0]  # Pi 5 typically uses bus 1
    addresses = [0x68, 0x69]  # Two possible addresses
    
    device_found = False
    
    for bus_num in buses:
        print(f"\n📡 Testing I2C bus {bus_num}...")
        
        try:
            bus = smbus.SMBus(bus_num)
        except Exception as e:
            print(f"   ❌ Cannot open I2C bus {bus_num}: {e}")
            continue
        
        for addr in addresses:
            try:
                print(f"   🔍 Checking address 0x{addr:02X}...")
                
                # Try to read WHO_AM_I register (0x75)
                who_am_i = bus.read_byte_data(addr, 0x75)
                print(f"      WHO_AM_I register: 0x{who_am_i:02X}")
                
                if who_am_i == 0x68:
                    print(f"   ✅ MPU6050 found at address 0x{addr:02X}!")
                    
                    # Test basic communication
                    print("   🧪 Testing communication...")
                    
                    # Wake up the device
                    bus.write_byte_data(addr, 0x6B, 0x00)
                    time.sleep(0.1)
                    
                    # Read accelerometer data
                    accel_x_h = bus.read_byte_data(addr, 0x3B)
                    accel_x_l = bus.read_byte_data(addr, 0x3C)
                    accel_raw = (accel_x_h << 8) | accel_x_l
                    if accel_raw > 32767:
                        accel_raw -= 65536
                    accel_g = accel_raw / 16384.0
                    
                    print(f"      Sample X-axis: {accel_g:.3f}g")
                    print("   ✅ Communication test successful!")
                    
                    device_found = True
                    found_bus = bus_num
                    found_addr = addr
                    break
                else:
                    print(f"      ⚠️  Unexpected WHO_AM_I: 0x{who_am_i:02X}")
                    
            except Exception as e:
                print(f"      ❌ Error: {e}")
        
        bus.close()
        
        if device_found:
            break
    
    print("\n" + "=" * 50)
    
    if device_found:
        print("🎉 SUCCESS! GY521/MPU6050 is working correctly")
        print(f"   📍 Location: I2C bus {found_bus}, address 0x{found_addr:02X}")
        print("\n✨ You can now run the water tracker:")
        print("   python3 gy521_water_tracker.py")
    else:
        print("❌ No GY521/MPU6050 found")
        print("\n🔧 Troubleshooting steps:")
        print("1. Check wiring connections:")
        print("   VCC -> Pin 1 (3.3V) or Pin 2 (5V)")
        print("   GND -> Pin 6 (GND)")
        print("   SCL -> Pin 5 (GPIO3)")
        print("   SDA -> Pin 3 (GPIO2)")
        print("2. Enable I2C: sudo raspi-config -> Interface Options -> I2C")
        print("3. Scan manually: sudo i2cdetect -y 1")
        print("4. Reboot and try again")
        
    return device_found

def check_permissions():
    """Check I2C permissions"""
    print("\n🔐 Checking I2C Permissions")
    print("=" * 30)
    
    import os
    import grp
    
    # Check if user is in i2c group
    try:
        i2c_group = grp.getgrnam('i2c')
        user_groups = os.getgroups()
        
        if i2c_group.gr_gid in user_groups:
            print("✅ User is in i2c group")
        else:
            print("❌ User is NOT in i2c group")
            print("Fix with: sudo usermod -a -G i2c $USER")
            print("Then logout and login again")
    except KeyError:
        print("⚠️  i2c group not found")
    
    # Check device permissions
    i2c_devices = ['/dev/i2c-0', '/dev/i2c-1']
    for device in i2c_devices:
        if os.path.exists(device):
            stat = os.stat(device)
            mode = oct(stat.st_mode)[-3:]
            print(f"✅ {device} exists (permissions: {mode})")
        else:
            print(f"❌ {device} not found")

def main():
    """Main test function"""
    print("KOI Water Tracker - GY521 Connection Test")
    print("Raspberry Pi 5 with Raspberry Pi OS")
    print("=" * 50)
    
    # Check permissions first
    check_permissions()
    
    # Test I2C connection
    success = test_i2c_connection()
    
    print("\n" + "=" * 50)
    if success:
        print("🚀 All tests passed! Ready to track water consumption!")
    else:
        print("🛠️  Please fix the issues above and try again")
        
    return success

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Test cancelled by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your setup and try again")
