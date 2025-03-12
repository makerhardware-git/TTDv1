import pygame
import os
import random
import time
import threading
from mutagen.mp3 import MP3
from mutagen.id3 import ID3

class MusicPlayer:
    def __init__(self, on_music_end_callback):
        pygame.mixer.init()
        self.return_to_menu = False
        self.on_music_end_callback = on_music_end_callback
        self.play_thread = None  # Thread for playing songs
        self.current_song = None  # Store the currently playing song
        self.stop_flag = False  # Flag to stop playback
        self.is_paused = False  # Track whether the music is paused
        self.skip_song_flag = False  # New flag to handle skipping songs

    def get_song_metadata(self, song_filename, song):
        """Retrieve metadata from an MP3 file, handling missing metadata safely"""
        try:
            audio = MP3(song_filename, ID3=ID3)
            metadata = {
                'title': audio.get('TIT2').text[0] if 'TIT2' in audio else song,
                'artist': audio.get('TPE1').text[0] if 'TPE1' in audio else 'Unknown',
                'album': audio.get('TALB').text[0] if 'TALB' in audio else 'Unknown',
                'year': audio.get('TDRC').text[0] if 'TDRC' in audio else 'Unknown'
            }
        except Exception as e:
            print(f"DEBUG: Error reading metadata for {song_filename}: {e}")
            metadata = {
                'title': song,
                'artist': 'Unknown',
                'album': 'Unknown',
                'year': 'Unknown'
            }
        
        return metadata

    def play_playlist(self, playlist_path, lcd_manager):
        """Starts playing a playlist in a separate thread"""
        print(f"DEBUG: Starting playlist from {playlist_path}")
        songs = [f for f in os.listdir(playlist_path) if f.endswith(".mp3")]
        
        if not songs:
            print("DEBUG: No songs found in playlist")
            self.on_music_end_callback()
            return

        print(f"DEBUG: Found {len(songs)} songs, shuffling...")
        random.shuffle(songs)

        # Start playback in a separate thread
        self.stop_flag = False  # Reset stop flag
        self.is_paused = False  # Reset pause flag
        self.skip_song_flag = False  # Reset skip flag
        self.play_thread = threading.Thread(target=self._play_songs, args=(songs, playlist_path, lcd_manager))
        self.play_thread.start()

    def _play_songs(self, songs, playlist_path, lcd_manager):
        """Plays songs in a separate thread to prevent blocking"""
        for song in songs:
            if self.stop_flag:
                print("DEBUG: Playback interrupted - returning to menu")
                pygame.mixer.music.stop()
                return

            # Reset skip flag for each new song
            self.skip_song_flag = False
            song_path = os.path.join(playlist_path, song)
            self.current_song = song_path  # Store the current song
            print(f"DEBUG: Loading song: {song}")
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()

            metadata = self.get_song_metadata(song_path, song)
            lcd_manager.display_song(metadata)

            # Wait for the song to finish or until playback is stopped or skipped
            while pygame.mixer.music.get_busy() or self.is_paused:
                time.sleep(0.1)
                if self.stop_flag:
                    pygame.mixer.music.stop()
                    print("Stopping song and returning to menu")
                    self.stop()
                    return
                if self.skip_song_flag:
                    print("Song skipped")
                    self.skip_song_flag = False
                    break  # Break out of the loop to move to the next song
        
        print("DEBUG: Playlist finished - signaling return to menu")
        self.on_music_end_callback()

    def toggle_play_pause(self):
        """Pauses or resumes playback"""
        if self.is_paused:
            print("DEBUG: Resuming playback")
            pygame.mixer.music.unpause()
            self.is_paused = False
        elif pygame.mixer.music.get_busy():
            print("DEBUG: Pausing playback")
            pygame.mixer.music.pause()
            self.is_paused = True

    def rewind_song(self):
        """Rewinds the currently playing song"""
        if self.current_song:
            print("DEBUG: Rewinding song")
            pygame.mixer.music.stop()
            pygame.mixer.music.load(self.current_song)
            pygame.mixer.music.play()
            self.is_paused = False  # Reset pause state when rewinding

    def skip_song(self):
        """Stops the current song and moves to the next one"""
        print("DEBUG: Skipping song")
        self.skip_song_flag = True  # Set flag to skip to next song
        pygame.mixer.music.stop()  # Immediately stop playback
        self.is_paused = False  # Reset pause state when skipping

    def stop(self):
        """Stops playback and returns to menu"""
        print("DEBUG: Stopping music playback")
        self.stop_flag = True  # Set flag to stop playback
        pygame.mixer.music.stop()  # Immediately stop playback
        self.is_paused = False  # Reset pause state when stopping