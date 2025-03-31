import subprocess
class VoiceReceiver:
    def open_spotify(self):
        print("Opening Spotify...")
        subprocess.Popen(["spotify.exe"])

    def close_spotify(self):
        print("Closing Spotify")
        try:
            subprocess.run("taskkill /f /im Spotify.exe", shell=True)
            print("Spotify closed.")
        except Exception as e:
            print(f"Error closing Spotify: {e}")