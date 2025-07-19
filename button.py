import platform
import time
import threading

# GPIO library selection based on platform and availability
if platform.system() == "Linux" and platform.machine().startswith("arm"):
    try:
        # Try gpiod first (Raspberry Pi 5 compatible)
        import gpiod
        GPIO_LIBRARY = "gpiod"
    except ImportError:
        try:
            # Fallback to RPi.GPIO (Raspberry Pi 4 and earlier)
            import RPi.GPIO as GPIO
            GPIO_LIBRARY = "RPi.GPIO"
        except ImportError:
            # Use mock if neither is available
            from mock_gpio import *
            import mock_gpio as GPIO
            GPIO_LIBRARY = "mock"
else:
    # Use mock GPIO on non-Raspberry Pi systems
    from mock_gpio import *
    import mock_gpio as GPIO
    GPIO_LIBRARY = "mock"

print(f"[BUTTON] Using GPIO library: {GPIO_LIBRARY}")

class Button:
    def __init__(self, port):
        self.port = port
        self.pressed = False
        self.last_press_time = 0
        self.debounce_time = 0.2  # 200ms debounce
        self.running = True
        
        if GPIO_LIBRARY == "gpiod":
            self._setup_gpiod()
        elif GPIO_LIBRARY == "RPi.GPIO":
            self._setup_rpi_gpio()
        else:  # mock
            self._setup_mock_gpio()
    
    def _setup_gpiod(self):
        """Setup button using gpiod (Raspberry Pi 5 compatible)"""
        self.chip = gpiod.Chip('gpiochip4')  # Pi 5 uses gpiochip4
        self.line = self.chip.get_line(self.port)
        
        # Configure line for input with pull-up
        self.line.request(consumer="button", type=gpiod.LINE_REQ_EV_FALLING_EDGE, flags=gpiod.LINE_REQ_FLAG_BIAS_PULL_UP)
        
        # Start monitoring thread
        self.monitor_thread = threading.Thread(target=self._monitor_gpiod, daemon=True)
        self.monitor_thread.start()
        print(f"[BUTTON] Setup gpiod button on pin {self.port}")
    
    def _setup_rpi_gpio(self):
        """Setup button using RPi.GPIO (Pi 4 and earlier)"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.port, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.port, GPIO.FALLING, callback=self._button_callback, bouncetime=200)
        print(f"[BUTTON] Setup RPi.GPIO button on pin {self.port}")
    
    def _setup_mock_gpio(self):
        """Setup button using mock GPIO (development)"""
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.port, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.port, GPIO.FALLING, callback=self._button_callback, bouncetime=200)
        print(f"[BUTTON] Setup mock GPIO button on pin {self.port}")
    
    def _monitor_gpiod(self):
        """Monitor button presses using gpiod"""
        while self.running:
            try:
                if self.line.event_wait(sec=1):  # 1 second timeout
                    event = self.line.event_read()
                    if event.type == gpiod.LineEvent.FALLING_EDGE:
                        self._button_callback(self.port)
            except Exception as e:
                print(f"[BUTTON] Error monitoring button: {e}")
                break
    
    def _button_callback(self, channel):
        """Callback function called when button is pressed"""
        current_time = time.time()
        if current_time - self.last_press_time > self.debounce_time:
            self.pressed = True
            self.last_press_time = current_time
            print(f"Button on pin {self.port} pressed!")
            
    def is_pressed(self):
        """Check if button has been pressed since last check"""
        if self.pressed:
            self.pressed = False  # Reset the flag
            return True
        return False
        
    def read_state(self):
        """Read the current state of the button"""
        if GPIO_LIBRARY == "gpiod":
            return self.line.get_value()
        else:
            return GPIO.input(self.port)
        
    def cleanup(self):
        """Clean up GPIO resources"""
        self.running = False
        
        if GPIO_LIBRARY == "gpiod":
            if hasattr(self, 'monitor_thread'):
                self.monitor_thread.join(timeout=1)
            if hasattr(self, 'line'):
                self.line.release()
            if hasattr(self, 'chip'):
                self.chip.close()
        elif GPIO_LIBRARY == "RPi.GPIO":
            GPIO.remove_event_detect(self.port)
            GPIO.cleanup()
        else:  # mock
            GPIO.remove_event_detect(self.port)
            GPIO.cleanup()
        
        print(f"[BUTTON] Cleaned up button on pin {self.port}")

# # Example usage
# if __name__ == "__main__":
#     # Create a button on pin 18
#     button = Button(18)
    
#     try:
#         print("Button test started. Press the button or wait for simulated presses...")
#         while True:
#             if button.is_pressed():
#                 print("Button press detected!")
#             time.sleep(0.1)
            
#     except KeyboardInterrupt:
#         print("\nExiting...")
#     finally:
#         button.cleanup()
