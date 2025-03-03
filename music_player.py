import pygame
import random
from mutagen.id3 import ID3
import os

class MusicPlayer:
    def __init__(self):
        pygame.mixer.init()
        self.current_song = None
        self.is_playing = False
        self.skip_current = False

    def play_playlist(self, playlist_path, lcd_manager):
        songs = [f for f in os.listdir(playlist_path) if f.endswith('.mp3')]
        if not songs:
            return

        random.shuffle(songs)
        
        for song in songs:
            if self.skip_current:
                self.skip_current = False
                continue

            song_path = os.path.join(playlist_path, song)
            metadata = self.get_metadata(song_path)
            
            try:
                pygame.mixer.music.load(song_path)
                pygame.mixer.music.play()
                lcd_manager.display_now_playing(metadata)
                
                while pygame.mixer.music.get_busy() and not self.skip_current:
                    pygame.time.Clock().tick(10)
                
            except Exception as e:
                print(f"Error playing {song}: {e}")
                continue

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
        
        return metadata

    def stop(self):
        pygame.mixer.music.stop()
        pygame.mixer.quit()
