import RPi.GPIO as GPIO
import time
import pygame

class VolumeControl:
    def __init__(self, clk_pin=23, dt_pin=22, sw_pin=27, min_volume=0, max_volume=1.0, step=0.01):
        # Clean up any previous GPIO setup first
        GPIO.cleanup()
        
        # Set up GPIO mode
        GPIO.setmode(GPIO.BCM)
        
        # Define pins
        self.CLK_PIN = clk_pin
        self.DT_PIN = dt_pin
        self.SW_PIN = sw_pin
        
        # Volume settings
        self.min_volume = min_volume
        self.max_volume = max_volume
        self.volume_step = step
        self.current_volume = 0.5  # Start at 50% volume
        
        # Initialize pygame mixer if not already initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        
        # Set initial volume
        pygame.mixer.music.set_volume(self.current_volume)
        
        # Set up the GPIO pins
        GPIO.setup(self.CLK_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.DT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.SW_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Variables for tracking state
        self.last_encoded = 0
        self.last_button_state = 1  # For PUD_UP, button released state is 1
        
        # Start monitoring thread
        self.running = True
    
    def start(self):
        """Start monitoring the rotary encoder in a loop"""
        try:
            while self.running:
                self.check_volume_change()
                self.check_mute_button()
                time.sleep(0.001)  # Short delay for CPU usage
        except KeyboardInterrupt:
            self.cleanup()
    
    def check_volume_change(self):
        # Read the current state
        MSB = GPIO.input(self.CLK_PIN)
        LSB = GPIO.input(self.DT_PIN)
        
        # Convert binary to decimal
        encoded = (MSB << 1) | LSB
        sum_value = (self.last_encoded << 2) | encoded
        
        # Check rotation direction
        changed = False
        if sum_value == 0b1101 or sum_value == 0b0100 or sum_value == 0b0010 or sum_value == 0b1011:
            # Clockwise rotation - increase volume
            self.current_volume = min(self.max_volume, self.current_volume + self.volume_step)
            changed = True
        elif sum_value == 0b1110 or sum_value == 0b0111 or sum_value == 0b0001 or sum_value == 0b1000:
            # Counter-clockwise rotation - decrease volume
            self.current_volume = max(self.min_volume, self.current_volume - self.volume_step)
            changed = True
        
        # Update if volume changed
        if changed:
            pygame.mixer.music.set_volume(self.current_volume)
            print(f"DEBUG: Volume changed to {self.current_volume*100:.0f}%")
        
        # Save the current state for next time
        self.last_encoded = encoded
    
    def check_mute_button(self):
        current_button_state = GPIO.input(self.SW_PIN)
        
        # Button press detected (0 means pressed with pull-up resistor)
        if current_button_state == 0 and self.last_button_state == 1:
            # Toggle mute
            if pygame.mixer.music.get_volume() > 0:
                # Store current volume and mute
                self.stored_volume = self.current_volume
                self.current_volume = 0
                pygame.mixer.music.set_volume(0)
                print("DEBUG: Audio muted")
            else:
                # Restore volume
                self.current_volume = self.stored_volume
                pygame.mixer.music.set_volume(self.current_volume)
                print(f"DEBUG: Audio unmuted, volume restored to {self.current_volume*100:.0f}%")
            
            # Add a small delay to avoid multiple detections
            time.sleep(0.1)
        
        self.last_button_state = current_button_state
    
    def get_volume(self):
        """Return the current volume level (0.0 to 1.0)"""
        return self.current_volume
    
    def set_volume(self, volume):
        """Set volume to a specific level (0.0 to 1.0)"""
        self.current_volume = max(self.min_volume, min(self.max_volume, volume))
        pygame.mixer.music.set_volume(self.current_volume)
        print(f"DEBUG: Volume set to {self.current_volume*100:.0f}%")
    
    def cleanup(self):
        """Clean up GPIO resources"""
        self.running = False
        GPIO.cleanup()
