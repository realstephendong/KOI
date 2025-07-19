import platform
import time

# Use mock GPIO on non-Raspberry Pi systems
if platform.system() == "Linux" and platform.machine().startswith("arm"):
    try:
        import RPi.GPIO as GPIO
    except ImportError:
        from mock_gpio import *
        import mock_gpio as GPIO
else:
    from mock_gpio import *
    import mock_gpio as GPIO

class Button:
    def __init__(self, port):
        self.port = port
        self.pressed = False
        self.last_press_time = 0
        self.debounce_time = 0.2  # 200ms debounce
        
        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.port, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Add event detection for button press
        GPIO.add_event_detect(self.port, GPIO.FALLING, callback=self._button_callback, bouncetime=200)
        
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
        """Read the current state of the button (0 = pressed, 1 = not pressed with pull-up)"""
        return GPIO.input(self.port)
        
    def cleanup(self):
        """Clean up GPIO resources"""
        GPIO.remove_event_detect(self.port)
        GPIO.cleanup()

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
