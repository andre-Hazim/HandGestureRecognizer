import os
import subprocess
import spotipy
from spotipy.oauth2 import SpotifyOAuth
class VoiceReceiver:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=os.environ['spotify_client_id'],
            client_secret=os.environ['spotify_client_secret'],
            redirect_uri="http://localhost:8888/callback",
            scope="user-modify-playback-state user-read-playback-state"
        ))
    def open_spotify(self):
        print("Opening Spotify...")

        subprocess.run(['spotify.exe'])

    def close_spotify(self):
        print("Closing Spotify")
        try:
            subprocess.run("taskkill /f /im Spotify.exe", shell=True)
            print("Spotify closed.")
        except Exception as e:
            print(f"Error closing Spotify: {e}")

    def play_song(self):
        search_results = self.sp.search(q="Shape of You", type="track", limit=1)

        # Check if any track was found
        if search_results['tracks']['items']:
            track = search_results['tracks']['items'][0]
            track_uri = track['uri']
            track_name = track['name']
            artist_name = track['artists'][0]['name']

            # Get an active device
            devices = self.sp.devices()
            if devices['devices']:
                device_id = devices['devices'][0]['id']  # Use first available device

                # Play the track
                self.sp.start_playback(device_id=device_id, uris=[track_uri])
                print(f"Now Playing: {track_name} by {artist_name}")
            else:
                print("No active Spotify device found. Open Spotify and play something first.")
        else:
            print("No tracks found.")
