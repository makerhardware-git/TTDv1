# main.py
from lcd_manager import LCDManager
from button_controller import ButtonController
from playlist_manager import PlaylistManager
from music_player import MusicPlayer
import signal
import sys

class MusicPlayerSystem:
    def __init__(self):
        self.lcd_manager = LCDManager()
        self.button_controller = ButtonController()
        self.playlist_manager = PlaylistManager()
        self.music_player = MusicPlayer()
        
        signal.signal(signal.SIGTERM, self.safe_exit)
        signal.signal(signal.SIGHUP, self.safe_exit)

    def setup(self):
        self.button_controller.setup_handlers(
            self.handle_up,
            self.handle_down,
            self.handle_select
        )
        # Initial display of playlists
        self.lcd_manager.display_playlists(self.playlist_manager.playlists)

    def handle_up(self):
        self.lcd_manager.scroll_up(self.playlist_manager.playlists)

    def handle_down(self):
        self.lcd_manager.scroll_down(self.playlist_manager.playlists)

    def handle_select(self):
        selected = self.lcd_manager.get_selected_playlist(self.playlist_manager.playlists)
        if selected:
            playlist_path = self.playlist_manager.get_playlist_path(selected)
            self.music_player.play_playlist(playlist_path, self.lcd_manager)
            # After playlist ends or is interrupted, show playlist selection again
            self.lcd_manager.display_playlists(self.playlist_manager.playlists)

    def safe_exit(self, signum, frame):
        self.music_player.stop()
        self.lcd_manager.clear()
        sys.exit(0)

    def run(self):
        try:
            self.setup()
            while True:
                pass  # Main loop keeps program running
        except KeyboardInterrupt:
            self.safe_exit(None, None)

if __name__ == "__main__":
    system = MusicPlayerSystem()
    system.run()
