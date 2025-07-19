"""
Mock GPIO module for development on non-Raspberry Pi systems.
This allows the code to run on Windows/Mac for development and testing.
"""

import time
import threading
import random

# Constants that mimic RPi.GPIO
BCM = "BCM"
BOARD = "BOARD"
IN = "IN"
OUT = "OUT"
HIGH = 1
LOW = 0
PUD_UP = "PUD_UP"
PUD_DOWN = "PUD_DOWN"
PUD_OFF = "PUD_OFF"
RISING = "RISING"
FALLING = "FALLING"
BOTH = "BOTH"

class MockGPIO:
    def __init__(self):
        self.mode = None
        self.pins = {}
        self.callbacks = {}
        self.running = True
        self.simulation_thread = None
        
    def setmode(self, mode):
        """Set the pin numbering mode"""
        self.mode = mode
        print(f"[MOCK GPIO] Set mode to {mode}")
        
    def setup(self, pin, direction, pull_up_down=PUD_OFF):
        """Setup a pin for input or output"""
        self.pins[pin] = {
            'direction': direction,
            'pull_up_down': pull_up_down,
            'value': LOW if direction == OUT else HIGH  # Buttons typically start HIGH with pull-up
        }
        print(f"[MOCK GPIO] Setup pin {pin} as {direction} with pull={pull_up_down}")
        
        # Start simulation thread for input pins
        if direction == IN and self.simulation_thread is None:
            self.simulation_thread = threading.Thread(target=self._simulate_button_presses, daemon=True)
            self.simulation_thread.start()
            
    def input(self, pin):
        """Read the value of an input pin"""
        if pin in self.pins:
            return self.pins[pin]['value']
        return LOW
        
    def output(self, pin, value):
        """Set the value of an output pin"""
        if pin in self.pins:
            self.pins[pin]['value'] = value
            print(f"[MOCK GPIO] Pin {pin} set to {'HIGH' if value else 'LOW'}")
            
    def add_event_detect(self, pin, edge, callback=None, bouncetime=200):
        """Add edge detection for a pin"""
        if callback:
            self.callbacks[pin] = {
                'callback': callback,
                'edge': edge,
                'bouncetime': bouncetime
            }
            print(f"[MOCK GPIO] Added event detection for pin {pin} on {edge} edge")
            
    def remove_event_detect(self, pin):
        """Remove edge detection for a pin"""
        if pin in self.callbacks:
            del self.callbacks[pin]
            print(f"[MOCK GPIO] Removed event detection for pin {pin}")
            
    def cleanup(self):
        """Clean up GPIO resources"""
        self.running = False
        self.pins.clear()
        self.callbacks.clear()
        print("[MOCK GPIO] Cleanup completed")
        
    def _simulate_button_presses(self):
        """Simulate random button presses for testing"""
        print("[MOCK GPIO] Button simulation started - press Ctrl+C to stop")
        print("[MOCK GPIO] Simulating button presses every 3-8 seconds...")
        
        while self.running:
            time.sleep(random.uniform(3, 8))  # Random delay between 3-8 seconds
            
            # Find input pins and simulate button press
            input_pins = [pin for pin, config in self.pins.items() if config['direction'] == IN]
            
            if input_pins and self.running:
                pin = random.choice(input_pins)
                
                # Simulate button press (HIGH to LOW for pull-up)
                if self.pins[pin]['pull_up_down'] == PUD_UP:
                    old_value = self.pins[pin]['value']
                    self.pins[pin]['value'] = LOW  # Button pressed
                    print(f"[MOCK GPIO] Simulated button press on pin {pin}")
                    
                    # Trigger callback if registered
                    if pin in self.callbacks:
                        callback_info = self.callbacks[pin]
                        if callback_info['edge'] in [FALLING, BOTH]:
                            callback_info['callback'](pin)
                    
                    # Hold button for a short time
                    time.sleep(0.1)
                    
                    # Release button
                    self.pins[pin]['value'] = HIGH
                    print(f"[MOCK GPIO] Simulated button release on pin {pin}")
                    
                    # Trigger callback for rising edge
                    if pin in self.callbacks:
                        callback_info = self.callbacks[pin]
                        if callback_info['edge'] in [RISING, BOTH]:
                            callback_info['callback'](pin)

# Create a global instance to mimic the RPi.GPIO module
_gpio_instance = MockGPIO()

# Export the functions to mimic RPi.GPIO interface
setmode = _gpio_instance.setmode
setup = _gpio_instance.setup
input = _gpio_instance.input
output = _gpio_instance.output
add_event_detect = _gpio_instance.add_event_detect
remove_event_detect = _gpio_instance.remove_event_detect
cleanup = _gpio_instance.cleanup
