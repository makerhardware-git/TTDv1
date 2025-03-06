# lcd_manager.py
from rpi_lcd import LCD
from time import sleep

class LCDManager:
    def __init__(self):
        self.lcd = LCD()
        self.window_start = 0  # Start index of the current 4-playlist window
        self.selected_index = 0  # Currently selected playlist index
        self.max_lines = 4

    def clear(self):
        self.lcd.clear()

def display_playlists(self, playlists):
    """Display current window of playlists with arrow indicating selection"""
    window_end = min(self.window_start + self.max_lines, len(playlists))
    displayed_playlists = playlists[self.window_start:window_end]

    for i, playlist in enumerate(displayed_playlists):
        # Calculate which line should show the arrow
        prefix = '->' if (self.window_start + i) == self.selected_index else '  '
        
        # Write only this line instead of clearing everything
        self.lcd.text(f"{prefix} {playlist}", i + 1)  # LCD lines are 1-based


    def scroll_up(self, playlists):
        """Move selection up one line, updating window if necessary"""
        if self.selected_index > 0:
            self.selected_index -= 1
            
            # If we scrolled above current window, shift window up
            if self.selected_index < self.window_start:
                self.window_start = max(0, self.window_start - self.max_lines)
            
            self.display_playlists(playlists)
            return True
        return False

    def scroll_down(self, playlists):
        """Move selection down one line, updating window if necessary"""
        if self.selected_index < len(playlists) - 1:
            self.selected_index += 1
            
            # If we scrolled below current window, shift window down
            if self.selected_index >= self.window_start + self.max_lines:
                self.window_start += self.max_lines
            
            self.display_playlists(playlists)
            return True
        return False

    def get_selected_playlist(self, playlists):
        """Return the currently selected playlist name"""
        if 0 <= self.selected_index < len(playlists):
            return playlists[self.selected_index]
        return None

    def display_now_playing(self, metadata):
        """Display current song information"""
        self.clear()
        self.lcd.text(f"Title: {str(metadata.get('title', ''))[:14]}", 1)
        self.lcd.text(f"Artist: {str(metadata.get('artist', ''))[:13]}", 2)
        self.lcd.text(f"Album: {str(metadata.get('album', ''))[:14]}", 3)
        self.lcd.text(f"Year: {str(metadata.get('year', ''))[:15]}", 4)
