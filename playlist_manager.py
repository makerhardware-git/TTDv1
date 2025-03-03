import os

class PlaylistManager:
    def __init__(self, base_dir='playlists'):
        self.base_dir = base_dir
        self.playlists = []
        self.current_playlist = None
        self.refresh_playlists()

    def refresh_playlists(self):
        self.playlists = [d for d in os.listdir(self.base_dir) 
                         if os.path.isdir(os.path.join(self.base_dir, d))]
        self.playlists.sort()

    def get_playlist_path(self, playlist_name):
        return os.path.join(self.base_dir, playlist_name)

    def get_songs_in_playlist(self, playlist_name):
        playlist_path = self.get_playlist_path(playlist_name)
        return [f for f in os.listdir(playlist_path) if f.endswith('.mp3')]
