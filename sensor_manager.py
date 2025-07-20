#!/usr/bin/env python3
"""
KOI - GY521 Water Consumption Tracker for Tamagotchi Water Bottle Project

This code uses a GY521 (MPU6050) gyroscope module to detect when a water bottle
is tilted for drinking and calculates water consumption based on tilt angle and duration.
Adapted to work with the Tamagotchi game system.

Hardware:
- GY521 (MPU6050) gyroscope module
- Raspberry Pi 5 with touchscreen LCD

Connections:
- VCC to 3.3V or 5V (GY521 works with both)
- GND to GND
- SCL to GPIO3 (SCL)
- SDA to GPIO2 (SDA)
"""

import time
import math
from datetime import datetime
from collections import deque

# Try to import smbus, fall back gracefully if not available
try:
    import smbus
    SMBUS_AVAILABLE = True
except ImportError:
    SMBUS_AVAILABLE = False
    print("smbus not available - using simulation mode")

class SensorManager:
    def __init__(self, port='/dev/ttyUSB0', baudrate=9600):
        """Initialize sensor manager for GY521 gyroscope"""
        self.port = port
        self.baudrate = baudrate
        self.serial_connection = None
        
        # GY521 (MPU6050) I2C address
        self.MPU6050_ADDR = 0x68
        
        # MPU6050 register addresses
        self.ACCEL_XOUT_H = 0x3B
        self.PWR_MGMT_1 = 0x6B
        
        # Calibration and threshold values (from your working code)
        self.TILT_THRESHOLD = 70.0        # Increased threshold for more realistic pouring detection
        self.TILT_UPPER_BOUND = 180.0     # Allow drinking detection up to fully upside down
        self.DRINKING_TIMEOUT = 2.0       # Reduced timeout for quicker session end (seconds)
        self.MIN_DRINKING_TIME = 0.3      # Reduced minimum time for quick sips (seconds)
        self.CALIBRATION_SAMPLES = 200    # Increased samples for better calibration
        self.NOISE_THRESHOLD = 5.0        # Minimum change to consider real movement
        
        # Water consumption calculation constants (IMPROVED VALUES)
        self.BASE_FLOW_RATE = 6.0         # Base flow rate (ml per second at 45 degrees) - increased for bigger measurement
        self.ANGLE_MULTIPLIER = 0.5       # Flow rate multiplier per 10 degrees of tilt - slightly more aggressive
        self.MAX_FLOW_RATE = 40.0         # Maximum flow rate (ml per second) - increased for bigger measurement
        
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
        
        # Game integration variables
        self.water_amount = 0
        self.is_shaking = False
        self.shake_timer = 0
        self.shake_samples = deque(maxlen=10)
        self.calibrated = False
        # --- Add session end flag ---
        self.just_ended_drinking = False
        self.last_session_amount = 0.0
        
        # Shake detection
        self.shake_threshold = 1.5
        self.shake_window_size = 5
        self.accel_history = []
        self._shake_printed = False
        
        # Initialize I2C bus
        self.bus = None
        self.init_i2c()
        
        # Initialize MPU6050
        if not self.init_mpu6050():
            print("Failed to initialize MPU6050, using simulation mode")
            self.simulation_mode = True
        else:
            self.simulation_mode = False
            # Calibrate the sensor
            self.calibrate_sensor()
    
    def init_i2c(self):
        """Initialize I2C bus for Raspberry Pi"""
        if not SMBUS_AVAILABLE:
            print("smbus not available - using simulation mode")
            return False
            
        try:
            # Try bus 1 first (standard Raspberry Pi I2C)
            self.bus = smbus.SMBus(1)
            print("I2C bus initialized successfully using smbus(1)")
            return True
        except Exception as e:
            print(f"Failed to initialize I2C bus with smbus(1): {e}")
            print("Trying alternative I2C bus...")
            try:
                # Try bus 0 as fallback
                self.bus = smbus.SMBus(0)
                print("I2C bus initialized successfully using smbus(0)")
                return True
            except Exception as e2:
                print(f"Failed to initialize I2C bus with smbus(0): {e2}")
                print("Using simulation mode")
                return False
    
    def init_mpu6050(self):
        """Initialize the MPU6050 sensor"""
        if not self.bus:
            return False
            
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
        if self.simulation_mode:
            self.calibrated = True
            # Initialize upright vector for simulation mode
            self.upright_vector = [0.0, 0.0, 1.0]
            return
            
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
        
        self.calibrated = True
    
    def read_accelerometer(self):
        """Read accelerometer data from MPU6050 using basic smbus methods"""
        if self.simulation_mode:
            # Simulate sensor data for testing
            self.generate_simulated_data()
            return
            
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
        if not self.calibrated:
            return False
            
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
                # Update game water amount
                self.water_amount = int(water_consumed)

            self.last_drinking_time = current_time
            return True
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
        return False
    
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
        
        # More reasonable safety check - limit to 20ml per update (increased)
        if water_consumed > 20.0:
            water_consumed = 20.0
        
        return water_consumed
    
    def end_drinking_session(self, current_time):
        """End the current drinking session and log results"""
        session_duration = current_time - self.drinking_start_time
        
        if session_duration >= self.MIN_DRINKING_TIME:
            print("Drinking session ended!")
            print(f"Session duration: {session_duration:.1f} seconds")
            print(f"Water consumed this session: {round(self.session_water_consumed)} ml")
            print(f"Total water consumed: {self.total_water_consumed:.1f} ml")
            print()
            # --- Set session end flag and amount ---
            self.just_ended_drinking = True
            self.last_session_amount = int(round(self.session_water_consumed))
        
        self.is_drinking = False
        self.session_water_consumed = 0.0
        self.water_amount = 0
    
    def detect_shake(self, shake_threshold=1.2, window_size=5):
        """
        Detect if the bottle is being shaken based on rapid changes in acceleration.
        shake_threshold: minimum change in acceleration (g) to consider as shaking
        window_size: number of samples to consider for shake detection
        """
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
                if not self._shake_printed:
                    print("Shake detected! (max accel diff: {:.2f}g)".format(max_diff))
                    self._shake_printed = True
                self.is_shaking = True
                self.shake_timer = 3.0  # Shake effect lasts 3 seconds
                return True
            else:
                self._shake_printed = False
        
        # Update shake timer
        if self.is_shaking:
            self.shake_timer -= 0.05  # Assuming 20Hz update rate
            if self.shake_timer <= 0:
                self.is_shaking = False
                
        return self.is_shaking
    
    def connect(self):
        """Connect to the sensor via serial (legacy method for compatibility)"""
        return not self.simulation_mode
    
    def disconnect(self):
        """Disconnect from sensor"""
        if self.bus:
            self.bus.close()
            self.bus = None
    
    def get_sensor_status(self):
        """Get current sensor status"""
        return {
            'connected': not self.simulation_mode,
            'calibrated': self.calibrated,
            'tilt_x': self.tilt_angle_x,
            'tilt_y': self.tilt_angle_y,
            'is_drinking': self.is_drinking,
            'is_shaking': self.is_shaking,
            'water_amount': self.water_amount,
            'total_water_consumed': self.total_water_consumed
        }
    
    def reset_water_amount(self):
        """Reset water amount after processing"""
        self.water_amount = 0
    
    def update(self):
        """Update sensor readings and detection - main interface for game"""
        current_time = time.time()
        
        # Read sensor data
        self.read_accelerometer()
        self.calculate_tilt_angles()
        
        # Detect drinking and shaking
        drinking_detected = self.detect_drinking(current_time)
        shaking_detected = self.detect_shake()
        
        return {
            'drinking_detected': drinking_detected,
            'shaking_detected': shaking_detected,
            'water_amount': self.water_amount if drinking_detected else 0,
            # --- Add session end info ---
            'just_ended_drinking': self.just_ended_drinking,
            'last_session_amount': self.last_session_amount
        }
    
    def generate_simulated_data(self):
        """Generate simulated sensor data for testing without hardware"""
        import random
        
        # Simulate random sensor readings
        self.accel_x = random.uniform(-0.1, 0.1)
        self.accel_y = random.uniform(-0.1, 0.1)
        self.accel_z = random.uniform(0.9, 1.1)
        
        if not self.calibrated:
            self.calibrate_sensor()
            
        # Simulate occasional drinking (for testing)
        if random.random() < 0.01:  # 1% chance per update
            self.accel_y = random.uniform(0.5, 1.0)  # Simulate tilt
            
        # Simulate occasional shaking
        if random.random() < 0.005:  # 0.5% chance per update
            self.accel_x = random.uniform(-0.5, 0.5)
            self.accel_y = random.uniform(-0.5, 0.5)
            
        return True
    
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

# Legacy compatibility class
class GY521WaterTrackerFixed(SensorManager):
    """Legacy class name for backward compatibility"""
    pass 