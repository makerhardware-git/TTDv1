import pygame
import os
import random
import time
import signal
import sys
import threading
from gpiozero import Button
from music_player import MusicPlayer
from lcd_manager import LCDManager
from playlist_manager import PlaylistManager
from volume_control import VolumeControl
from time import sleep

class MusicPlayerSystem:
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.init()
        self.lcd_manager = LCDManager()
        self.playlist_manager = PlaylistManager()
        self.volume_control = VolumeControl()
        # Pass `self.on_music_end` as the callback when creating MusicPlayer
        self.music_player = MusicPlayer(self.on_music_end)

        # Set up buttons with debouncing
        self.up_button = Button(21, bounce_time=0.15)  # Further increased debounce time
        self.down_button = Button(20, bounce_time=0.15)
        self.left_button = Button(16, bounce_time=0.15)
        self.right_button = Button(26, bounce_time=0.15)
        self.select_button = Button(19, bounce_time=0.1)
        self.set_button = Button(0, bounce_time=0.15)

        # Button press lock to prevent multiple rapid presses
        self.button_lock = threading.Lock()
        self.last_press_time = 0
        self.button_cooldown = 0.2  # Increased cooldown between button presses
        self.setup_button_handlers()
        self.is_playing_music = False
        self.volume_thread = None  # Thread for volume control

        # Changed initial state to "home" (homescreen)
        self.state = "home"  # Initial state is now the homescreen
        self.selected_playlist = None
        self.playlists = self.playlist_manager.playlists  # Get playlists

        # Set up signal handlers for safe exit
        signal.signal(signal.SIGTERM, self.safe_exit)
        signal.signal(signal.SIGHUP, self.safe_exit)


    def setup(self):
        """Start volume control in a separate thread and show homescreen"""
        self.volume_thread = threading.Thread(target=self.volume_control.start)
        self.volume_thread.daemon = True  # Thread will exit when main program exits
        self.volume_thread.start()
        self.lcd_manager.clear()
        self.lcd_manager.reset_selection()
        self.playlists = self.playlist_manager.playlists  # Refresh playlists
        # Display home screen instead of playlists on startup
        self.lcd_manager.display_home()


    def is_button_press_valid(self):
        """Check if enough time has passed since the last button press"""
        with self.button_lock:
            current_time = time.time()
            if current_time - self.last_press_time < self.button_cooldown:
                return False
            self.last_press_time = current_time
            return True


    def setup_button_handlers(self):
        """Set up handlers for all button presses"""
        self.up_button.when_pressed = self.handle_up_button
        self.down_button.when_pressed = self.handle_down_button
        self.select_button.when_pressed = self.handle_select_button
        self.left_button.when_pressed = self.handle_left_button
        self.right_button.when_pressed = self.handle_right_button


    def return_to_menu(self):
        """Handle transition from playback to menu mode"""        
        try:
            self.state = "menu"
            self.lcd_manager.reset_selection()
            # First clear the LCD
            self.lcd_manager.clear()
            sleep(0.1)  # Allow LCD to process
            self.lcd_manager.display_playlists(self.playlists)            
            # Update selected playlist reference
            self.selected_playlist = self.lcd_manager.get_selected_playlist(self.playlists)
    
        except Exception as e:
            print(f"ERROR in return_to_menu: {e}")
            # If something fails, try a more aggressive approach
            try:
                # Force recreate LCD manager
                self.lcd_manager = LCDManager()
                time.sleep(0.1)
                self.playlists = self.playlist_manager.playlists
                self.lcd_manager.display_playlists(self.playlists)
            except Exception as e2:
                print(f"CRITICAL ERROR: Could not reset LCD: {e2}")

    def return_to_home(self):
        """Handle transition to home screen"""
        try:
            self.state = "home"
            # First clear the LCD
            self.lcd_manager.clear()
            sleep(0.1)  # Allow LCD to process
            self.lcd_manager.display_home()
        except Exception as e:
            print(f"ERROR in return_to_home: {e}")
            # If something fails, try a more aggressive approach
            try:
                # Force recreate LCD manager
                self.lcd_manager = LCDManager()
                time.sleep(0.1)
                self.lcd_manager.display_home()
            except Exception as e2:
                print(f"CRITICAL ERROR: Could not reset home screen: {e2}")


    def handle_up_button(self):
        if not self.is_button_press_valid():
            return
        
        if self.state == "home":
            # In home screen, navigate between home options
            self.lcd_manager.home_scroll_up()
        elif self.state == "menu":
            self.lcd_manager.scroll_up(self.playlists)
            self.selected_playlist = self.lcd_manager.get_selected_playlist(self.playlists)
        elif self.state == "playback":
            self.music_player.stop()
            self.return_to_menu()


    def handle_down_button(self):
        if not self.is_button_press_valid():
            return
        
        if self.state == "home":
            # In home screen, navigate between home options
            self.lcd_manager.home_scroll_down()
        elif self.state == "menu":
            self.lcd_manager.scroll_down(self.playlists)
            self.selected_playlist = self.lcd_manager.get_selected_playlist(self.playlists)
        elif self.state == "playback":
            self.music_player.stop()
            self.return_to_menu()


    def handle_select_button(self):
        if not self.is_button_press_valid():
            return
        
        if self.state == "home":
            # Handle selection from home screen
            selected_option = self.lcd_manager.get_selected_home_option()
            if selected_option == "Playlists":
                self.state = "menu"
                self.lcd_manager.reset_selection()
                self.lcd_manager.display_playlists(self.playlists)
                self.selected_playlist = self.lcd_manager.get_selected_playlist(self.playlists)
            elif selected_option == "Bluetooth":
                self.state = "bluetooth"
                self.lcd_manager.display_bluetooth()
        elif self.state == "menu":
            self.selected_playlist = self.lcd_manager.get_selected_playlist(self.playlists)
            if self.selected_playlist:
                print(f"DEBUG: Selected playlist: {self.selected_playlist}")
                self.state = "playback"                
                playlist_path = os.path.join("playlists", self.selected_playlist)
                self.music_player.play_playlist(playlist_path, self.lcd_manager)
        elif self.state == "playback":
            print("DEBUG: SELECT - Playback mode - toggling play/pause")
            self.music_player.toggle_play_pause()
        elif self.state == "bluetooth":
            # Return to home if select is pressed in bluetooth mode
            self.return_to_home()


    def handle_left_button(self):
        if not self.is_button_press_valid():
            return
        
        if self.state == "menu" or self.state == "bluetooth":
            # Return to home screen from menu or bluetooth
            self.return_to_home()
        elif self.state == "playback":
            self.music_player.rewind_song()


    def handle_right_button(self):
        if not self.is_button_press_valid():
            return
        
        if self.state == "menu" or self.state == "bluetooth":
            # Return to home screen from menu or bluetooth
            self.return_to_home()
        elif self.state == "playback":
            self.music_player.skip_song()


    def on_music_end(self):
        """Callback function triggered when the playlist finishes."""
        self.return_to_menu()


    def safe_exit(self, signum, frame):
        """Clean up and exit safely"""
        try:
            self.music_player.stop()
            self.volume_control.cleanup()
            self.lcd_manager.clear()
        except Exception as e:
            print(f"ERROR during exit: {e}")
        finally:
            sys.exit(0)

    def run(self):
        """Start the system"""
        try:
            self.setup()
            print("DEBUG: System started and running")
            signal.pause()  # Keeps the program running and waits for signals
        except KeyboardInterrupt:
            self.safe_exit(None, None)
        except Exception as e:
            print(f"ERROR: {e}")
            self.safe_exit(None, None)

if __name__ == "__main__":
    system = MusicPlayerSystem()
    system.run()
