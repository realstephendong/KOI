#!/usr/bin/env python3
"""
KOI - GY521 Water Consumption Tracker for Raspberry Pi 5 (Raspberry Pi OS)

This code uses a GY521 (MPU6050) gyroscope module to detect when a water bottle
is tilted for drinking and calculates water consumption based on tilt angle and duration.

Hardware:
- GY521 (MPU6050) gyroscope module
- Raspberry Pi 5 with Raspberry Pi OS (Bookworm or later)

Connections:
- VCC to 3.3V (Pin 1) or 5V (Pin 2) - GY521 works with both
- GND to GND (Pin 6)
- SCL to GPIO3/SCL (Pin 5)
- SDA to GPIO2/SDA (Pin 3)

Setup Instructions:
1. Enable I2C: sudo raspi-config -> Interface Options -> I2C -> Enable
2. Install dependencies: sudo apt install python3-smbus i2c-tools
3. Test connection: sudo i2cdetect -y 1
4. Add user to i2c group: sudo usermod -a -G i2c $USER
5. Logout and login again
"""

import smbus
import time
import math
from datetime import datetime

class GY521WaterTracker:
    def __init__(self):
        # GY521 (MPU6050) I2C address (can be 0x68 or 0x69 depending on AD0 pin)
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
        
        # Initialize I2C bus for Raspberry Pi OS
        self.bus = None
        i2c_buses = [1, 0]  # Try bus 1 first (standard for Pi 5), then bus 0
        addresses = [0x68, 0x69]  # Try both possible addresses
        
        print("Initializing I2C connection...")
        print("Note: If 'Resource temporarily unavailable' error occurs, retrying...")
        
        # Try different combinations of bus and address with retry logic
        success = False
        max_retries = 3
        
        for bus_num in i2c_buses:
            if success:
                break
                
            for addr in addresses:
                if success:
                    break
                    
                for retry in range(max_retries):
                    try:
                        if retry > 0:
                            print(f"Retry {retry + 1}/{max_retries} for I2C bus {bus_num} address 0x{addr:02X}...")
                            time.sleep(0.5)  # Wait before retry
                        else:
                            print(f"Trying I2C bus {bus_num} with address 0x{addr:02X}...")
                        
                        # Close any existing bus connection first
                        try:
                            test_bus = smbus.SMBus(bus_num)
                            time.sleep(0.1)  # Small delay after opening
                            
                            # Test communication by reading WHO_AM_I register with timeout protection
                            who_am_i = test_bus.read_byte_data(addr, 0x75)
                            print(f"WHO_AM_I register: 0x{who_am_i:02X}")
                            
                            if who_am_i == 0x68:
                                print(f"✅ MPU6050 found on I2C bus {bus_num} at address 0x{addr:02X}")
                                self.bus = test_bus
                                self.MPU6050_ADDR = addr
                                success = True
                                break
                            else:
                                print(f"⚠️  Device found but unexpected WHO_AM_I: 0x{who_am_i:02X}")
                                test_bus.close()
                                time.sleep(0.1)
                                
                        except OSError as e:
                            if e.errno == 11:  # Resource temporarily unavailable
                                print(f"   I2C busy (errno 11), waiting and retrying...")
                                try:
                                    test_bus.close()
                                except:
                                    pass
                                time.sleep(1.0)  # Wait longer for busy resource
                                continue
                            else:
                                print(f"   Failed: {e}")
                                try:
                                    test_bus.close()
                                except:
                                    pass
                                break
                        except Exception as e:
                            print(f"   Failed: {e}")
                            try:
                                test_bus.close()
                            except:
                                pass
                            break
                    except Exception as e:
                        print(f"   Bus creation failed: {e}")
                        continue
        
        if not self.bus:
            print("\n❌ Failed to initialize I2C communication with MPU6050")
            print("\nThe 'Resource temporarily unavailable' error suggests:")
            print("1. Another process is using I2C (check for other sensor programs)")
            print("2. I2C bus may be locked - try these steps:")
            print("   sudo systemctl stop any-i2c-services")
            print("   sudo rmmod i2c_dev && sudo modprobe i2c_dev")
            print("   sudo reboot")
            print("3. Check for conflicting processes:")
            print("   sudo lsof /dev/i2c-1")
            print("   ps aux | grep i2c")
            print("4. Disable other I2C services temporarily:")
            print("   sudo systemctl disable any-sensor-services")
            raise Exception("I2C initialization failed - see troubleshooting steps above")
        
        # Initialize MPU6050
        if not self.init_mpu6050():
            raise Exception("Failed to initialize MPU6050!")
        
        # Calibrate the sensor
        self.calibrate_sensor()
    
    def init_mpu6050(self):
        """Initialize the MPU6050 sensor for Raspberry Pi OS"""
        try:
            print("Configuring MPU6050 for Raspberry Pi OS...")
            
            # Step 1: Wake up the MPU6050 (clear sleep bit in PWR_MGMT_1)
            print("  Waking up MPU6050...")
            self.bus.write_byte_data(self.MPU6050_ADDR, self.PWR_MGMT_1, 0x00)
            time.sleep(0.1)
            
            # Step 2: Verify device is awake
            pwr_mgmt = self.bus.read_byte_data(self.MPU6050_ADDR, self.PWR_MGMT_1)
            print(f"  Power management register: 0x{pwr_mgmt:02X}")
            
            # Step 3: Configure accelerometer (±2g range)
            print("  Configuring accelerometer...")
            self.bus.write_byte_data(self.MPU6050_ADDR, 0x1C, 0x00)  # ACCEL_CONFIG
            time.sleep(0.05)
            
            # Step 4: Configure gyroscope (±250°/s range)
            print("  Configuring gyroscope...")
            self.bus.write_byte_data(self.MPU6050_ADDR, 0x1B, 0x00)  # GYRO_CONFIG
            time.sleep(0.05)
            
            # Step 5: Set sample rate (1kHz / (1 + 7) = 125Hz)
            print("  Setting sample rate...")
            self.bus.write_byte_data(self.MPU6050_ADDR, 0x19, 0x07)  # SMPLRT_DIV
            time.sleep(0.05)
            
            # Step 6: Configure Digital Low Pass Filter (DLPF)
            print("  Configuring filters...")
            self.bus.write_byte_data(self.MPU6050_ADDR, 0x1A, 0x06)  # CONFIG register
            time.sleep(0.05)
            
            # Step 7: Test reading accelerometer data
            print("  Testing accelerometer readings...")
            accel_x_h = self.bus.read_byte_data(self.MPU6050_ADDR, self.ACCEL_XOUT_H)
            accel_x_l = self.bus.read_byte_data(self.MPU6050_ADDR, self.ACCEL_XOUT_H + 1)
            print(f"  Sample reading - X-axis: 0x{accel_x_h:02X}{accel_x_l:02X}")
            
            print("✅ MPU6050 initialized successfully for Raspberry Pi OS")
            return True
            
        except Exception as e:
            print(f"❌ Failed to initialize MPU6050: {e}")
            print("\nPossible issues:")
            print("- I2C not enabled in raspi-config")
            print("- Incorrect wiring connections")
            print("- Device at different address (try 0x69)")
            print("- Insufficient permissions (add user to i2c group)")
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
        """Main loop for water tracking on Raspberry Pi OS"""
        print("KOI - GY521 Water Consumption Tracker for Raspberry Pi 5")
        print("Running on Raspberry Pi OS")
        print("Initialization complete!")
        print(f"I2C Address: 0x{self.MPU6050_ADDR:02X}")
        print(f"Tilt threshold: {self.TILT_THRESHOLD}°")
        print(f"Noise threshold: {self.NOISE_THRESHOLD:.1f}°")
        print("Tilt the bottle to start tracking water consumption...")
        print("Press Ctrl+C to stop")
        print()
        
        last_update_time = time.time()
        last_print_time = time.time()
        update_interval = 0.05  # Update every 50ms (20 Hz)
        
        try:
            while True:
                current_time = time.time()
                
                # Update sensor readings at regular intervals
                if current_time - last_update_time >= update_interval:
                    self.read_accelerometer()
                    self.calculate_tilt_angles()
                    self.detect_drinking(current_time)
                    self.detect_shake()
                    last_update_time = current_time
                
                # Print status every second
                if current_time - last_print_time >= 1.0:
                    self.print_status()
                    last_print_time = current_time
                
                time.sleep(0.01)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            print("\n\nStopping water tracker...")
            print(f"Final total water consumed: {self.total_water_consumed:.1f} ml")
            print("Thank you for using KOI Water Tracker! 🐟")
        except Exception as e:
            print(f"\nUnexpected error: {e}")
            print("Stopping water tracker...")
        finally:
            try:
                self.bus.close()
                print("I2C bus closed successfully")
            except:
                pass

if __name__ == "__main__":
    print("KOI Water Tracker - Raspberry Pi 5 Edition")
    print("=" * 50)
    
    try:
        tracker = GY521WaterTracker()
        tracker.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nSetup checklist for Raspberry Pi 5:")
        print("1. sudo raspi-config -> Interface Options -> I2C -> Enable")
        print("2. sudo apt update && sudo apt install python3-smbus i2c-tools")
        print("3. sudo usermod -a -G i2c $USER")
        print("4. Logout and login again")
        print("5. sudo i2cdetect -y 1  # Should show device at 68 or 69")
        print("6. Check wiring: VCC->3.3V, GND->GND, SCL->Pin5, SDA->Pin3")
        print("\nFor more help, check the Raspberry Pi documentation or run 'pinout' command.") 