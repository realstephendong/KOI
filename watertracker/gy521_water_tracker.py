#!/usr/bin/env python3
"""
KOI - GY521 Water Consumption Tracker for Raspberry Pi (QNX Version with Robust Detection)

This code uses a GY521 (MPU6050) gyroscope module to detect when a water bottle
is tilted for drinking and calculates water consumption based on tilt angle and duration.

Hardware:
- GY521 (MPU6050) gyroscope module
- Raspberry Pi 4 with QNX 8.0

Connections:
- VCC to 3.3V or 5V (GY521 works with both)
- GND to GND
- SCL to GPIO3 (SCL)
- SDA to GPIO2 (SDA)
"""

import smbus
import time
import math
from datetime import datetime

class GY521WaterTrackerFixed:
    def __init__(self):
        # GY521 (MPU6050) I2C address
        self.MPU6050_ADDR = 0x68
        
        # MPU6050 register addresses
        self.ACCEL_XOUT_H = 0x3B
        self.PWR_MGMT_1 = 0x6B
        
        # Calibration and threshold values
        self.TILT_THRESHOLD = 70.0        # Increased threshold for more realistic pouring detection
        self.TILT_UPPER_BOUND = 180.0     # Allow drinking detection up to fully upside down
        self.DRINKING_TIMEOUT = 2.0       # Reduced timeout for quicker session end (seconds)
        self.MIN_DRINKING_TIME = 0.3      # Reduced minimum time for quick sips (seconds)
        self.CALIBRATION_SAMPLES = 200    # Increased samples for better calibration
        self.NOISE_THRESHOLD = 5.0        # Minimum change to consider real movement
        
        # Water consumption calculation constants (IMPROVED VALUES)
        self.BASE_FLOW_RATE = 0.5         # Base flow rate (ml per second at 45 degrees)
        self.ANGLE_MULTIPLIER = 0.3       # Flow rate multiplier per 10 degrees of tilt
        self.MAX_FLOW_RATE = 8.0          # Maximum flow rate (ml per second)
        
        # Sensor data
        self.accel_x = 0.0
        self.accel_y = 0.0
        self.accel_z = 0.0
        self.tilt_angle_x = 0.0
        self.tilt_angle_y = 0.0
        
        # Calibration offsets
        self.calibrated_x = 0.0
        self.calibrated_y = 0.0
        self.calibrated_z = 0.0
        
        # Movement detection
        self.last_tilt_y = 0.0
        self.stable_readings = 0
        self.required_stable_readings = 5   # Reduced to 5 stable readings (0.25 seconds) for quicker detection
        
        # Drinking session variables
        self.is_drinking = False
        self.drinking_start_time = 0.0
        self.last_drinking_time = 0.0
        self.total_water_consumed = 0.0
        self.session_water_consumed = 0.0
        
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
        if not self.init_mpu6050():
            raise Exception("Failed to initialize MPU6050!")
        
        # Calibrate the sensor
        self.calibrate_sensor()
    
    def init_mpu6050(self):
        """Initialize the MPU6050 sensor"""
        try:
            # Wake up the MPU6050
            self.bus.write_byte_data(self.MPU6050_ADDR, self.PWR_MGMT_1, 0)
            time.sleep(0.1)
            print("MPU6050 initialized successfully")
            return True
        except Exception as e:
            print(f"Failed to initialize MPU6050: {e}")
            return False
    
    def calibrate_sensor(self):
        """Calibrate the sensor by taking multiple readings when level"""
        print("Calibrating sensor...")
        print("Keep the bottle level and still for 4 seconds...")
        
        sum_x = 0.0
        sum_y = 0.0
        sum_z = 0.0
        readings = []
        
        for i in range(self.CALIBRATION_SAMPLES):
            self.read_accelerometer()
            readings.append((self.accel_x, self.accel_y, self.accel_z))
            sum_x += self.accel_x
            sum_y += self.accel_y
            sum_z += self.accel_z
            time.sleep(0.02)  # 50Hz sampling
        
        # Calculate mean
        self.calibrated_x = sum_x / self.CALIBRATION_SAMPLES
        self.calibrated_y = sum_y / self.CALIBRATION_SAMPLES
        self.calibrated_z = sum_z / self.CALIBRATION_SAMPLES
        # Store upright vector for orientation-independent tilt
        self.upright_vector = [self.calibrated_x, self.calibrated_y, self.calibrated_z]
        
        # Calculate standard deviation to understand noise level
        var_x = sum((x - self.calibrated_x) ** 2 for x, _, _ in readings) / self.CALIBRATION_SAMPLES
        var_y = sum((y - self.calibrated_y) ** 2 for _, y, _ in readings) / self.CALIBRATION_SAMPLES
        std_x = math.sqrt(var_x)
        std_y = math.sqrt(var_y)
        
        print("Calibration complete!")
        print(f"Calibration offsets - X: {self.calibrated_x:.3f}, Y: {self.calibrated_y:.3f}, Z: {self.calibrated_z:.3f}")
        print(f"Noise levels - X: ±{std_x:.3f}g, Y: ±{std_y:.3f}g")
        
        # Adjust noise threshold based on actual sensor noise
        self.NOISE_THRESHOLD = max(5.0, std_y * 100)  # Convert to degrees, minimum 5°
        print(f"Adjusted noise threshold: {self.NOISE_THRESHOLD:.1f}°")
    
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
            
            # Apply calibration offsets
            self.accel_x -= self.calibrated_x
            self.accel_y -= self.calibrated_y
            self.accel_z -= self.calibrated_z
            
        except Exception as e:
            print(f"Error reading accelerometer: {e}")
    
    def calculate_tilt_angles(self):
        """Calculate tilt angles from accelerometer data"""
        # Calculate tilt angles from accelerometer data
        self.tilt_angle_x = math.degrees(math.atan2(self.accel_y, math.sqrt(self.accel_x**2 + self.accel_z**2)))
        self.tilt_angle_y = math.degrees(math.atan2(-self.accel_x, math.sqrt(self.accel_y**2 + self.accel_z**2)))
    
    def detect_drinking(self, current_time):
        """Detect drinking based on orientation-independent tilt angle and duration with noise filtering"""
        # Calculate current acceleration vector (raw, not offset)
        current_vector = [self.accel_x + self.calibrated_x, self.accel_y + self.calibrated_y, self.accel_z + self.calibrated_z]
        upright_vector = self.upright_vector
        # Calculate angle between current vector and upright vector
        dot = sum(a*b for a, b in zip(current_vector, upright_vector))
        mag1 = math.sqrt(sum(a*a for a in current_vector))
        mag2 = math.sqrt(sum(b*b for b in upright_vector))
        # Clamp value to avoid math domain errors
        cos_angle = max(-1.0, min(1.0, dot / (mag1 * mag2))) if mag1 > 0 and mag2 > 0 else 1.0
        total_tilt = math.degrees(math.acos(cos_angle))

        # Check for significant movement (not just noise)
        tilt_change = abs(total_tilt - self.last_tilt_y)

        if tilt_change > self.NOISE_THRESHOLD:
            # Significant movement detected
            self.stable_readings = 0
        else:
            # Movement is stable
            self.stable_readings += 1

        # Only trigger if we have stable readings above threshold and within upper bound
        if (self.TILT_THRESHOLD < total_tilt < self.TILT_UPPER_BOUND) and self.stable_readings >= self.required_stable_readings:
            # DEBUG: Print threshold comparison
            if not self.is_drinking:  # Only print when first crossing threshold
                print(f"DEBUG: Orientation-independent tilt {total_tilt:.1f}° vs threshold {self.TILT_THRESHOLD}° (stable: {self.stable_readings})")

            # Bottle is tilted enough to be drinking
            if not self.is_drinking:
                # Start a new drinking session
                self.is_drinking = True
                self.drinking_start_time = current_time
                self.session_water_consumed = 0.0
                print(f"Drinking detected! Starting session... (Tilt: {total_tilt:.1f}°)")

            # Calculate water consumption for this time interval
            time_elapsed = current_time - self.last_drinking_time
            if time_elapsed > 0:
                water_consumed = self.calculate_water_consumption(total_tilt, time_elapsed)
                self.session_water_consumed += water_consumed
                self.total_water_consumed += water_consumed

            self.last_drinking_time = current_time
        elif self.is_drinking and (total_tilt <= self.TILT_THRESHOLD or total_tilt >= self.TILT_UPPER_BOUND):
            # Bottle is no longer tilted enough or is too far upside down - end session immediately
            self.end_drinking_session(current_time)
        else:
            # Bottle is not tilted enough or movement is not stable
            if self.is_drinking:
                # Check if drinking session should end due to timeout
                if current_time - self.last_drinking_time > self.DRINKING_TIMEOUT:
                    self.end_drinking_session(current_time)

        # Update last tilt for next comparison
        self.last_tilt_y = total_tilt
    
    def calculate_water_consumption(self, tilt_angle, time_elapsed):
        """Calculate water consumption based on tilt angle and time (IMPROVED VERSION)"""
        # Calculate flow rate based on tilt angle with more realistic values
        # More aggressive flow rate calculation
        angle_factor = max(0, (tilt_angle - self.TILT_THRESHOLD) / 10.0)
        flow_rate = self.BASE_FLOW_RATE * (1 + angle_factor * self.ANGLE_MULTIPLIER)
        
        # Ensure flow rate is within reasonable bounds
        flow_rate = max(0, min(flow_rate, self.MAX_FLOW_RATE))
        
        # Calculate water consumed in this time interval
        water_consumed = flow_rate * time_elapsed
        
        # More reasonable safety check - limit to 5ml per update
        if water_consumed > 5.0:
            water_consumed = 5.0
        
        return water_consumed
    
    def end_drinking_session(self, current_time):
        """End the current drinking session and log results"""
        session_duration = current_time - self.drinking_start_time
        
        if session_duration >= self.MIN_DRINKING_TIME:
            print("Drinking session ended!")
            print(f"Session duration: {session_duration:.1f} seconds")
            print(f"Water consumed this session: {self.session_water_consumed:.1f} ml")
            print(f"Total water consumed: {self.total_water_consumed:.1f} ml")
            print()
        
        self.is_drinking = False
        self.session_water_consumed = 0.0
    
    def print_status(self):
        """Print current status information"""
        y_tilt_abs = abs(self.tilt_angle_y)
        
        status = f"Tilt - X: {self.tilt_angle_x:.1f}°, Y: {self.tilt_angle_y:.1f}° (Drinking: {y_tilt_abs:.1f}°) | "
        
        if self.is_drinking:
            status += f"DRINKING | Session: {self.session_water_consumed:.1f} ml | "
        else:
            status += "IDLE | "
        
        status += f"Total: {self.total_water_consumed:.1f} ml"
        print(status)
    
    def reset_water_consumption(self):
        """Reset water consumption counter"""
        self.total_water_consumed = 0.0
        self.session_water_consumed = 0.0
        print("Water consumption counter reset!")
    
    def get_total_water_consumed(self):
        """Get current total water consumption"""
        return self.total_water_consumed
    
    def get_session_water_consumed(self):
        """Get current session water consumption"""
        return self.session_water_consumed
    
    def is_currently_drinking(self):
        """Check if currently drinking"""
        return self.is_drinking
    
    def detect_shake(self, shake_threshold=1.2, window_size=5):
        """
        Detect if the bottle is being shaken based on rapid changes in acceleration.
        shake_threshold: minimum change in acceleration (g) to consider as shaking
        window_size: number of samples to consider for shake detection
        """
        if not hasattr(self, 'accel_history'):
            self.accel_history = []
        # Store the current acceleration vector magnitude
        accel_mag = math.sqrt(self.accel_x**2 + self.accel_y**2 + self.accel_z**2)
        self.accel_history.append(accel_mag)
        if len(self.accel_history) > window_size:
            self.accel_history.pop(0)
        # Only check for shake if we have enough samples
        if len(self.accel_history) == window_size:
            # Calculate the max difference in the window
            max_diff = max(self.accel_history) - min(self.accel_history)
            if max_diff > shake_threshold:
                if not hasattr(self, '_shake_printed') or not self._shake_printed:
                    print("Shake detected! (max accel diff: {:.2f}g)".format(max_diff))
                    self._shake_printed = True
            else:
                self._shake_printed = False
    
    def run(self):
        """Main loop for water tracking"""
        print("KOI - GY521 Water Consumption Tracker (QNX Version with Robust Detection)")
        print("Initialization complete!")
        print(f"Tilt threshold: {self.TILT_THRESHOLD}°")
        print(f"Noise threshold: {self.NOISE_THRESHOLD:.1f}°")
        print("Tilt the bottle to start tracking water consumption...")
        print()
        
        last_update_time = time.time()
        last_print_time = time.time()
        update_interval = 0.05  # Update every 50ms
        
        try:
            while True:
                current_time = time.time()
                
                # Update sensor readings at regular intervals
                if current_time - last_update_time >= update_interval:
                    self.read_accelerometer()
                    self.calculate_tilt_angles()
                    self.detect_drinking(current_time)
                    self.detect_shake()  # Call shake detection
                    last_update_time = current_time
                
                # Print status every second
                if current_time - last_print_time >= 1.0:
                    self.print_status()
                    last_print_time = current_time
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print("\nStopping water tracker...")
            print(f"Final total water consumed: {self.total_water_consumed:.1f} ml")
        finally:
            self.bus.close()

if __name__ == "__main__":
    try:
        tracker = GY521WaterTrackerFixed()
        tracker.run()
    except Exception as e:
        print(f"Error: {e}")
        print("Make sure the GY521 module is properly connected to the Raspberry Pi.")
        print("On QNX, ensure I2C is enabled and the device files exist.") 