#!/usr/bin/env python3
"""
KOI - GY521 Water Consumption Tracker Test Version

This is a test version to debug the drinking detection issue.
"""

import smbus
import time
import math

class GY521TestTracker:
    def __init__(self):
        # GY521 (MPU6050) I2C address
        self.MPU6050_ADDR = 0x68
        
        # MPU6050 register addresses
        self.ACCEL_XOUT_H = 0x3B
        self.PWR_MGMT_1 = 0x6B
        
        # Test threshold
        self.TILT_THRESHOLD = 15.0
        
        # Calibration offsets
        self.calibrated_x = 0.0
        self.calibrated_y = 0.0
        
        # Initialize I2C bus
        try:
            self.bus = smbus.SMBus(1)
            print("I2C bus initialized successfully using smbus(1)")
        except Exception as e:
            print(f"Failed to initialize I2C bus with smbus(1): {e}")
            try:
                self.bus = smbus.SMBus(0)
                print("I2C bus initialized successfully using smbus(0)")
            except Exception as e2:
                print(f"Failed to initialize I2C bus with smbus(0): {e2}")
                raise
        
        # Initialize MPU6050
        if not self.init_mpu6050():
            raise Exception("Failed to initialize MPU6050!")
        
        # Calibrate the sensor
        self.calibrate_sensor()
    
    def init_mpu6050(self):
        """Initialize the MPU6050 sensor"""
        try:
            self.bus.write_byte_data(self.MPU6050_ADDR, self.PWR_MGMT_1, 0)
            time.sleep(0.1)
            print("MPU6050 initialized successfully")
            return True
        except Exception as e:
            print(f"Failed to initialize MPU6050: {e}")
            return False
    
    def calibrate_sensor(self):
        """Calibrate the sensor"""
        print("Calibrating sensor...")
        print("Keep the bottle level and still...")
        
        sum_x = 0.0
        sum_y = 0.0
        
        for i in range(100):
            self.read_accelerometer()
            sum_x += self.accel_x
            sum_y += self.accel_y
            time.sleep(0.01)
        
        self.calibrated_x = sum_x / 100
        self.calibrated_y = sum_y / 100
        
        print("Calibration complete!")
        print(f"Calibration offsets - X: {self.calibrated_x:.3f}, Y: {self.calibrated_y:.3f}")
    
    def read_accelerometer(self):
        """Read accelerometer data"""
        try:
            accel_x_high = self.bus.read_byte_data(self.MPU6050_ADDR, self.ACCEL_XOUT_H)
            accel_x_low = self.bus.read_byte_data(self.MPU6050_ADDR, self.ACCEL_XOUT_H + 1)
            accel_y_high = self.bus.read_byte_data(self.MPU6050_ADDR, self.ACCEL_XOUT_H + 2)
            accel_y_low = self.bus.read_byte_data(self.MPU6050_ADDR, self.ACCEL_XOUT_H + 3)
            accel_z_high = self.bus.read_byte_data(self.MPU6050_ADDR, self.ACCEL_XOUT_H + 4)
            accel_z_low = self.bus.read_byte_data(self.MPU6050_ADDR, self.ACCEL_XOUT_H + 5)
            
            accel_x_raw = (accel_x_high << 8) | accel_x_low
            accel_y_raw = (accel_y_high << 8) | accel_y_low
            accel_z_raw = (accel_z_high << 8) | accel_z_low
            
            if accel_x_raw > 32767:
                accel_x_raw -= 65536
            if accel_y_raw > 32767:
                accel_y_raw -= 65536
            if accel_z_raw > 32767:
                accel_z_raw -= 65536
            
            self.accel_x = accel_x_raw / 16384.0
            self.accel_y = accel_y_raw / 16384.0
            self.accel_z = accel_z_raw / 16384.0
            
            self.accel_x -= self.calibrated_x
            self.accel_y -= self.calibrated_y
            
        except Exception as e:
            print(f"Error reading accelerometer: {e}")
    
    def calculate_tilt_angles(self):
        """Calculate tilt angles"""
        self.tilt_angle_x = math.degrees(math.atan2(self.accel_y, math.sqrt(self.accel_x**2 + self.accel_z**2)))
        self.tilt_angle_y = math.degrees(math.atan2(-self.accel_x, math.sqrt(self.accel_y**2 + self.accel_z**2)))
    
    def run_test(self):
        """Run the test with detailed debugging"""
        print("KOI - GY521 Test Tracker")
        print(f"Tilt threshold: {self.TILT_THRESHOLD}°")
        print("Starting test...")
        print()
        
        last_print_time = time.time()
        consecutive_above_threshold = 0
        consecutive_below_threshold = 0
        
        try:
            while True:
                current_time = time.time()
                
                # Read sensor data
                self.read_accelerometer()
                self.calculate_tilt_angles()
                
                # Calculate Y-axis tilt (drinking axis)
                y_tilt_abs = abs(self.tilt_angle_y)
                
                # Check threshold
                above_threshold = y_tilt_abs > self.TILT_THRESHOLD
                
                if above_threshold:
                    consecutive_above_threshold += 1
                    consecutive_below_threshold = 0
                else:
                    consecutive_below_threshold += 1
                    consecutive_above_threshold = 0
                
                # Print detailed status every 0.5 seconds
                if current_time - last_print_time >= 0.5:
                    status = f"Tilt - X: {self.tilt_angle_x:.1f}°, Y: {self.tilt_angle_y:.1f}° (Drinking: {y_tilt_abs:.1f}°)"
                    
                    if above_threshold:
                        status += f" | ABOVE THRESHOLD ({consecutive_above_threshold} consecutive)"
                        if consecutive_above_threshold == 1:
                            status += " <<< TRIGGER POINT!"
                    else:
                        status += f" | below threshold ({consecutive_below_threshold} consecutive)"
                    
                    print(status)
                    last_print_time = current_time
                
                time.sleep(0.05)  # 50ms delay
                
        except KeyboardInterrupt:
            print("\nTest stopped.")
        finally:
            self.bus.close()

if __name__ == "__main__":
    try:
        tracker = GY521TestTracker()
        tracker.run_test()
    except Exception as e:
        print(f"Error: {e}") 