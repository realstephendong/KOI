#!/usr/bin/env python3
"""
GY521 Test Script for Raspberry Pi (QNX Version with Basic smbus)

Simple test to verify GY521 (MPU6050) module is working correctly
using only basic smbus methods available on QNX.
"""

import smbus
import time
import math

class GY521TestBasic:
    def __init__(self):
        # GY521 (MPU6050) I2C address
        self.MPU6050_ADDR = 0x68
        
        # MPU6050 register addresses
        self.ACCEL_XOUT_H = 0x3B
        self.PWR_MGMT_1 = 0x6B
        
        # Sensor data
        self.accel_x = 0.0
        self.accel_y = 0.0
        self.accel_z = 0.0
        self.tilt_angle_x = 0.0
        self.tilt_angle_y = 0.0
        
        # Initialize I2C bus for QNX using standard smbus
        try:
            # Try bus 1 first (standard Raspberry Pi I2C)
            self.bus = smbus.SMBus(1)
            print("I2C bus initialized successfully using smbus(1)")
        except Exception as e:
            print(f"Failed to initialize I2C bus with smbus(1): {e}")
            print("Trying alternative I2C bus...")
            try:
                # Try bus 0 as fallback
                self.bus = smbus.SMBus(0)
                print("I2C bus initialized successfully using smbus(0)")
            except Exception as e2:
                print(f"Failed to initialize I2C bus with smbus(0): {e2}")
                raise
        
        # Initialize MPU6050
        self.init_mpu6050()
    
    def init_mpu6050(self):
        """Initialize the MPU6050 sensor"""
        try:
            # Wake up the MPU6050
            self.bus.write_byte_data(self.MPU6050_ADDR, self.PWR_MGMT_1, 0)
            time.sleep(0.1)
            print("MPU6050 initialized successfully")
        except Exception as e:
            print(f"Failed to initialize MPU6050: {e}")
            raise
    
    def read_accelerometer(self):
        """Read accelerometer data from MPU6050 using basic smbus methods"""
        try:
            # Read accelerometer data byte by byte using basic smbus methods
            # Read X-axis (high and low bytes)
            accel_x_high = self.bus.read_byte_data(self.MPU6050_ADDR, self.ACCEL_XOUT_H)
            accel_x_low = self.bus.read_byte_data(self.MPU6050_ADDR, self.ACCEL_XOUT_H + 1)
            
            # Read Y-axis (high and low bytes)
            accel_y_high = self.bus.read_byte_data(self.MPU6050_ADDR, self.ACCEL_XOUT_H + 2)
            accel_y_low = self.bus.read_byte_data(self.MPU6050_ADDR, self.ACCEL_XOUT_H + 3)
            
            # Read Z-axis (high and low bytes)
            accel_z_high = self.bus.read_byte_data(self.MPU6050_ADDR, self.ACCEL_XOUT_H + 4)
            accel_z_low = self.bus.read_byte_data(self.MPU6050_ADDR, self.ACCEL_XOUT_H + 5)
            
            # Convert to 16-bit signed integers
            accel_x_raw = (accel_x_high << 8) | accel_x_low
            accel_y_raw = (accel_y_high << 8) | accel_y_low
            accel_z_raw = (accel_z_high << 8) | accel_z_low
            
            # Handle negative values (two's complement)
            if accel_x_raw > 32767:
                accel_x_raw -= 65536
            if accel_y_raw > 32767:
                accel_y_raw -= 65536
            if accel_z_raw > 32767:
                accel_z_raw -= 65536
            
            # Convert to g-force (assuming ±2g range)
            self.accel_x = accel_x_raw / 16384.0
            self.accel_y = accel_y_raw / 16384.0
            self.accel_z = accel_z_raw / 16384.0
            
        except Exception as e:
            print(f"Error reading accelerometer: {e}")
    
    def calculate_tilt_angles(self):
        """Calculate tilt angles from accelerometer data"""
        self.tilt_angle_x = math.degrees(math.atan2(self.accel_y, math.sqrt(self.accel_x**2 + self.accel_z**2)))
        self.tilt_angle_y = math.degrees(math.atan2(-self.accel_x, math.sqrt(self.accel_y**2 + self.accel_z**2)))
    
    def run_test(self):
        """Run the test loop"""
        print("GY521 Test Script (QNX Version with Basic smbus)")
        print("================================================")
        print("MPU6050 initialized!")
        print("Keep the sensor level and still for testing...")
        print()
        
        try:
            while True:
                self.read_accelerometer()
                self.calculate_tilt_angles()
                
                tilt_magnitude = math.sqrt(self.tilt_angle_x**2 + self.tilt_angle_y**2)
                
                print(f"Raw Accel - X: {self.accel_x:.3f}g, Y: {self.accel_y:.3f}g, Z: {self.accel_z:.3f}g | "
                      f"Tilt - X: {self.tilt_angle_x:.1f}°, Y: {self.tilt_angle_y:.1f}°, Magnitude: {tilt_magnitude:.1f}°")
                
                time.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\nTest stopped by user")
        finally:
            self.bus.close()

if __name__ == "__main__":
    try:
        test = GY521TestBasic()
        test.run_test()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the GY521 module is properly connected to the Raspberry Pi.")
        print("On QNX, ensure I2C is enabled and the device files exist.") 