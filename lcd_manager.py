# lcd_manager.py
from rpi_lcd import LCD
from time import sleep

class LCDManager:
    def __init__(self):
        self.lcd = LCD()
        self.window_start = 0  # Start index of the current 4-playlist window
        self.selected_index = 0  # Currently selected playlist index
        self.max_lines = 4
        self.current_window = []  # Keep track of what's currently displayed
        
        # Home screen options
        self.home_options = ["Playlists", "Bluetooth"]
        self.home_selected = 0  # Index of selected option on home screen
    
    def clear(self):
        self.lcd.clear()
    
    def display_home(self):
        """Display home screen with options"""
        self.clear()
        self.current_window = []  # Reset window tracking
        
        # Display the home screen options with arrow indicator
        for i, option in enumerate(self.home_options):
            line_num = i + 1
            if i == self.home_selected:
                self.lcd.text(f"-> {option}", line_num)
            else:
                self.lcd.text(f"   {option}", line_num)
    
    def home_scroll_up(self):
        """Move selection up in home screen"""
        if self.home_selected > 0:
            self.home_selected -= 1
            self.display_home()
            return True
        return False
    
    def home_scroll_down(self):
        """Move selection down in home screen"""
        if self.home_selected < len(self.home_options) - 1:
            self.home_selected += 1
            self.display_home()
            return True
        return False
    
    def get_selected_home_option(self):
        """Return the currently selected home option"""
        if 0 <= self.home_selected < len(self.home_options):
            return self.home_options[self.home_selected]
        return None
    
    def display_playlists(self, playlists, prev_index=None):
        """Display playlists with arrow indicating selection"""
        # Initialize the current window if it's empty
        if not self.current_window:
            # Initial display - show the first page of playlists
            window_end = min(self.window_start + self.max_lines, len(playlists))
            self.current_window = playlists[self.window_start:window_end]
            
            # Display each playlist
            for i, playlist in enumerate(self.current_window):
                line_num = i + 1
                if i == 0:  # First item is selected
                    self.lcd.text(f"-> {playlist}", line_num)
                else:
                    self.lcd.text(f"   {playlist}", line_num)
            return
            
        # Calculate relative positions within the window
        relative_prev = prev_index - self.window_start if prev_index is not None else None
        relative_current = self.selected_index - self.window_start
        
        # Check if we need to redraw the entire screen (pagination)
        if self.selected_index < self.window_start or self.selected_index >= self.window_start + self.max_lines:
            # Calculate new window boundaries - align to multiples of max_lines
            self.window_start = (self.selected_index // self.max_lines) * self.max_lines
            window_end = min(self.window_start + self.max_lines, len(playlists))
            
            # Fully redraw the screen with new playlists
            self.clear()
            self.current_window = playlists[self.window_start:window_end]
            
            for i, playlist in enumerate(self.current_window):
                line_num = i + 1
                if self.window_start + i == self.selected_index:
                    self.lcd.text(f"-> {playlist}", line_num)
                else:
                    self.lcd.text(f"   {playlist}", line_num)
        else:
            # Just move the arrow - remove old arrow if within current window
            if relative_prev is not None and 0 <= relative_prev < len(self.current_window):
                prev_line = relative_prev + 1
                self.lcd.text(f"   {self.current_window[relative_prev]}", prev_line)
            
            # Add new arrow
            if 0 <= relative_current < len(self.current_window):
                current_line = relative_current + 1
                self.lcd.text(f"-> {self.current_window[relative_current]}", current_line)

    def scroll_up(self, playlists):
        """Move selection up one line, updating window if necessary"""
        if self.selected_index > 0:
            prev_index = self.selected_index
            self.selected_index -= 1
            self.display_playlists(playlists, prev_index)
            return True
        return False

    def scroll_down(self, playlists):
        """Move selection down one line, updating window if necessary"""
        if self.selected_index < len(playlists) - 1:
            prev_index = self.selected_index
            self.selected_index += 1
            self.display_playlists(playlists, prev_index)
            return True
        return False

    def get_selected_playlist(self, playlists):
        """Return the currently selected playlist name"""
        if 0 <= self.selected_index < len(playlists):
            return playlists[self.selected_index]
        return None
        
    def reset_selection(self):
        """Reset the selection state to initial values"""
        self.window_start = 0
        self.selected_index = 0
        self.current_window = []  # Reset the currently displayed window

    def display_now_playing(self, metadata):
        """Display current song information"""
        self.clear()
        self.current_window = []  # Reset window tracking when showing now playing
        self.lcd.text(f"Title: {str(metadata.get('title', ''))[:14]}", 1)
        self.lcd.text(f"Artist: {str(metadata.get('artist', ''))[:13]}", 2)
        self.lcd.text(f"Album: {str(metadata.get('album', ''))[:14]}", 3)
        self.lcd.text(f"Year: {str(metadata.get('year', ''))[:15]}", 4)
        
    def display_bluetooth(self):
        """Display bluetooth screen"""
        self.clear()
        self.current_window = []  # Reset window tracking
        self.lcd.text("Bluetooth Mode", 1)
        self.lcd.text("tits", 2)  # As requested in your specification
