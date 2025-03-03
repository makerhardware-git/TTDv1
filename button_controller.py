from gpiozero import Button

class ButtonController:
    def __init__(self):
        self.up_button = Button(21, bounce_time=0.05)
        self.down_button = Button(20, bounce_time=0.05)
        self.left_button = Button(16, bounce_time=0.05)
        self.right_button = Button(6, bounce_time=0.05)
        self.select_button = Button(5, bounce_time=0.05)
        self.set_button = Button(0, bounce_time=0.05)

    def setup_handlers(self, up_handler, down_handler, select_handler):
        self.up_button.when_pressed = up_handler
        self.down_button.when_pressed = down_handler
        self.select_button.when_pressed = select_handler
