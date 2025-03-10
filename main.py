# main.py
from lcd_manager import LCDManager
from button_controller import ButtonController
from playlist_manager import PlaylistManager
from music_player import MusicPlayer
from volume_control import VolumeControl
import signal
import sys
import threading

class MusicPlayerSystem:
    def __init__(self):
        self.lcd_manager = LCDManager()
        self.button_controller = ButtonController()
        self.playlist_manager = PlaylistManager()
        self.music_player = MusicPlayer()
        self.volume_control = VolumeControl()
        self.is_playing_music = False
        
        signal.signal(signal.SIGTERM, self.safe_exit)
        signal.signal(signal.SIGHUP, self.safe_exit)

    def setup(self):
        # Start volume control in a separate thread
        self.volume_thread = threading.Thread(target=self.volume_control.start)
        self.volume_thread.daemon = True  # Thread will exit when main program exits
        self.volume_thread.start()
        print("DEBUG: Volume control thread started")
        
        # Set up different handlers depending on current state
        self.setup_menu_mode()
        # Initial display of playlists
        self.lcd_manager.display_playlists(self.playlist_manager.playlists)

    def setup_menu_mode(self):
        print("DEBUG: Entering menu mode - buttons configured for menu navigation")
        self.button_controller.setup_handlers(
            self.handle_menu_up,
            self.handle_menu_down,
            self.handle_menu_select,
            lambda: print("DEBUG: Left button pressed in menu mode (no action)"),
            lambda: print("DEBUG: Right button pressed in menu mode (no action)"),
            lambda: print("DEBUG: Set button pressed in menu mode (no action)")
        )
        self.is_playing_music = False

    def setup_playback_mode(self):
        print("DEBUG: Entering playback mode - buttons configured for music control")
        self.button_controller.setup_handlers(
            self.handle_playback_up,
            self.handle_playback_down,
            self.handle_playback_select,
            self.handle_playback_left,
            self.handle_playback_right,
            lambda: print("DEBUG: Set button pressed in playback mode (no action)")
        )
        self.is_playing_music = True

    # Menu mode handlers
    def handle_menu_up(self):
        print("DEBUG: UP button pressed in menu mode - scrolling up")
        self.lcd_manager.scroll_up(self.playlist_manager.playlists)

    def handle_menu_down(self):
        print("DEBUG: DOWN button pressed in menu mode - scrolling down")
        self.lcd_manager.scroll_down(self.playlist_manager.playlists)

    def handle_menu_select(self):
        print("DEBUG: SELECT button pressed in menu mode - starting playlist")
        selected = self.lcd_manager.get_selected_playlist(self.playlist_manager.playlists)
        if selected:
            print(f"DEBUG: Selected playlist: {selected}")
            # Switch to playback mode before starting playback
            self.setup_playback_mode()
            playlist_path = self.playlist_manager.get_playlist_path(selected)
            self.music_player.play_playlist(playlist_path, self.lcd_manager)
            # After playlist ends or is interrupted, show playlist selection again
            print("DEBUG: Playlist finished or interrupted - returning to menu mode")
            self.setup_menu_mode()
            self.lcd_manager.display_playlists(self.playlist_manager.playlists)

    # Playback mode handlers
    def handle_playback_up(self):
        print("DEBUG: UP button pressed in playback mode - returning to menu")
        self.music_player.back_to_menu()

    def handle_playback_down(self):
        print("DEBUG: DOWN button pressed in playback mode - returning to menu")
        self.music_player.back_to_menu()

    def handle_playback_select(self):
        print("DEBUG: SELECT button pressed in playback mode - toggling pause/play")
        # Toggle pause/play
        is_paused = self.music_player.toggle_pause()
        # Optionally update LCD to show paused status
        if is_paused:
            print("DEBUG: Music paused")
            self.lcd_manager.display_paused()
        else:
            print("DEBUG: Music playing")
            self.lcd_manager.display_playing()

    def handle_playback_left(self):
        print("DEBUG: LEFT button pressed in playback mode - rewinding to previous song")
        self.music_player.rewind()

    def handle_playback_right(self):
        print("DEBUG: RIGHT button pressed in playback mode - skipping to next song")
        self.music_player.skip()

    def safe_exit(self, signum, frame):
        print("DEBUG: Exiting safely")
        self.music_player.stop()
        self.volume_control.cleanup()
        self.lcd_manager.clear()
        sys.exit(0)

    def run(self):
        try:
            self.setup()
            print("DEBUG: System started and running")
            while True:
                pass  # Main loop keeps program running
        except KeyboardInterrupt:
            self.safe_exit(None, None)

if __name__ == "__main__":
    system = MusicPlayerSystem()
    system.run()
