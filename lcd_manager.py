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

    def display_playlists(self, playlists, prev_index=None):
        """Display current window of playlists with arrow indicating selection, optimized for speed"""
        window_end = min(self.window_start + self.max_lines, len(playlists))
        displayed_playlists = playlists[self.window_start:window_end]

        for i, playlist in enumerate(displayed_playlists):
            list_index = self.window_start + i  # Absolute index in playlists
            
            # If this line was previously selected, remove the old arrow
            if list_index == prev_index:
                self.lcd.text(f"   {playlist}", i + 1)  # Space out the old arrow
            
            # If this line is the new selected item, place the new arrow
            if list_index == self.selected_index:
                self.lcd.text(f"-> {playlist}", i + 1)  # Move new arrow



    def scroll_up(self, playlists):
        """Move selection up one line, updating window if necessary"""
        if self.selected_index > 0:
            prev_index = self.selected_index  # Store previous position
            self.selected_index -= 1
            
            if self.selected_index < self.window_start:
                self.window_start = max(0, self.window_start - self.max_lines)
            
            self.display_playlists(playlists, prev_index)
            return True
        return False


    def scroll_down(self, playlists):
        """Move selection down one line, updating window if necessary"""
        if self.selected_index < len(playlists) - 1:
            prev_index = self.selected_index  # Store previous position
            self.selected_index += 1
            
            if self.selected_index >= self.window_start + self.max_lines:
                self.window_start += self.max_lines
            
            self.display_playlists(playlists, prev_index)
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
