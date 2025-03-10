from gpiozero import Button

class ButtonController:
    def __init__(self):
        print("DEBUG: Initializing button controller")
        self.up_button = Button(21, bounce_time=0.05)
        self.down_button = Button(20, bounce_time=0.05)
        self.left_button = Button(16, bounce_time=0.05)
        self.right_button = Button(26, bounce_time=0.05)
        self.select_button = Button(19, bounce_time=0.05)
        self.set_button = Button(0, bounce_time=0.05)
        print("DEBUG: All buttons initialized")

    def setup_handlers(self, up_handler, down_handler, select_handler, 
                      left_handler=None, right_handler=None, set_handler=None):
        print("DEBUG: Setting up button handlers")
        
        # Remove any existing handlers to avoid conflicts
        self.up_button.when_pressed = None
        self.down_button.when_pressed = None
        self.select_button.when_pressed = None
        self.left_button.when_pressed = None
        self.right_button.when_pressed = None
        self.set_button.when_pressed = None
        
        # Add new handlers
        self.up_button.when_pressed = up_handler
        print("DEBUG: Up button handler set")
        
        self.down_button.when_pressed = down_handler
        print("DEBUG: Down button handler set")
        
        self.select_button.when_pressed = select_handler
        print("DEBUG: Select button handler set")
        
        # Add handlers for the other buttons if provided
        if left_handler:
            self.left_button.when_pressed = left_handler
            print("DEBUG: Left button handler set")
            
        if right_handler:
            self.right_button.when_pressed = right_handler
            print("DEBUG: Right button handler set")
            
        if set_handler:
            self.set_button.when_pressed = set_handler
            print("DEBUG: Set button handler set")
