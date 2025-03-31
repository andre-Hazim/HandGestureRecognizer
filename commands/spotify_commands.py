from commands.command import Command

# Concrete Command to open Spotify
class OpenSpotifyCommand(Command):
    name = "open spotify"
    def __init__(self, receiver):
        self.receiver = receiver

    def execute(self):
        self.receiver.open_spotify()
class CloseSpotifyCommand(Command):
    name = "close spotify"
    def __init__(self, receiver):
        self.receiver = receiver

    def execute(self):
        self.receiver.close_spotify()

class PlaySpotifyCommand(Command):
    name = "play"
    def __init__(self,receiver):
        self.receiver = receiver
        self.song = ""

    def execute(self):
        self.receiver.play_song(self.song)

    def set_song(self,song):
        self.song = song

class PauseSongCommand(Command):
    name = "pause"
    def __init__(self, receiver):
        self.receiver = receiver
    def execute(self):
        self.receiver.pause_song()

class ResumeSongCommand(Command):
    name = "resume"
    def __init__(self,receiver):
        self.receiver = receiver
    def execute(self):
        self.receiver.resume_song()