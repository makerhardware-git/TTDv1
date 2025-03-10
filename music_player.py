import pygame
import random
from mutagen.id3 import ID3
import os

class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.current_song = None
        self.is_playing = True
        self.is_paused = False
        self.skip_current = False
        self.rewind_current = False
        self.return_to_menu = False
        self.current_song_index = 0
        self.current_playlist = []
        self.current_playlist_path = ""
        print("DEBUG: Music Player initialized")

    def play_playlist(self, playlist_path, lcd_manager):
        print(f"DEBUG: Starting playlist from {playlist_path}")
        self.current_playlist_path = playlist_path
        self.current_playlist = [f for f in os.listdir(playlist_path) if f.endswith('.mp3')]
        if not self.current_playlist:
            print("DEBUG: No MP3 files found in playlist directory")
            return
        
        print(f"DEBUG: Found {len(self.current_playlist)} songs, shuffling...")
        random.shuffle(self.current_playlist)
        self.current_song_index = 0
        self.return_to_menu = False
        
        while self.current_song_index < len(self.current_playlist) and not self.return_to_menu:
            if self.skip_current:
                print("DEBUG: Skip flag detected")
                self.skip_current = False
                self.current_song_index += 1
                print(f"DEBUG: Moving to song index {self.current_song_index}")
                if self.current_song_index >= len(self.current_playlist):
                    print("DEBUG: Reached end of playlist")
                    break
                continue
                
            if self.rewind_current:
                print("DEBUG: Rewind flag detected")
                self.rewind_current = False
                self.current_song_index = max(0, self.current_song_index - 1)
                print(f"DEBUG: Moving to song index {self.current_song_index}")
                
            song = self.current_playlist[self.current_song_index]
            song_path = os.path.join(playlist_path, song)
            print(f"DEBUG: Loading song: {song}")
            metadata = self.get_metadata(song_path)
            
            try:
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                self.is_paused = False
                print("DEBUG: Now playing song")
                lcd_manager.display_now_playing(metadata)
                
                while pygame.mixer.music.get_busy() and not self.skip_current and not self.rewind_current and not self.return_to_menu:
                    if self.is_paused:
                        pygame.mixer.music.pause()
                    else:
                        pygame.mixer.music.unpause()
                    pygame.time.Clock().tick(10)
                
                if not self.skip_current and not self.rewind_current and not self.return_to_menu:
                    # Song finished naturally, move to next song
                    print("DEBUG: Song finished naturally")
                    self.current_song_index += 1
                    print(f"DEBUG: Moving to song index {self.current_song_index}")
                    
            except Exception as e:
                print(f"DEBUG: Error playing {song}: {e}")
                self.current_song_index += 1
                continue
                
    def toggle_pause(self):
        self.is_paused = not self.is_paused
        print(f"DEBUG: Pause toggled to: {self.is_paused}")
        return self.is_paused
        
    def skip(self):
        print("DEBUG: Skip requested")
        self.skip_current = True
        
    def rewind(self):
        print("DEBUG: Rewind requested")
        self.rewind_current = True
        
    def back_to_menu(self):
        print("DEBUG: Return to menu requested")
        self.return_to_menu = True
        pygame.mixer.music.stop()
        
    def get_metadata(self, file_path):
        metadata = {
            'title': 'Unknown Title',
            'artist': 'Unknown Artist',
            'album': 'Unknown Album',
            'year': 'Unknown Year'
        }
        
        try:
            audio = ID3(file_path)
            if 'TIT2' in audio: metadata['title'] = str(audio['TIT2'].text[0])
            if 'TPE1' in audio: metadata['artist'] = str(audio['TPE1'].text[0])
            if 'TALB' in audio: metadata['album'] = str(audio['TALB'].text[0])
            if 'TDRC' in audio: metadata['year'] = str(audio['TDRC'].text[0])
        except:
            metadata['title'] = os.path.splitext(os.path.basename(file_path))[0]
        
        print(f"DEBUG: Metadata: {metadata['title']} by {metadata['artist']}")
        return metadata
        
    def stop(self):
        print("DEBUG: Stopping music player")
        pygame.mixer.music.stop()
        pygame.mixer.quit()
