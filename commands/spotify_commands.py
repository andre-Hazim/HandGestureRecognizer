from commands.command import Command

# Concrete Command to open Spotify
class OpenSpotifyCommand(Command):
    def __init__(self, receiver):
        self.receiver = receiver

    def execute(self):
        self.receiver.open_spotify()
class CloseSpotifyCommand(Command):
    def __init__(self, receiver):
        self.receiver = receiver

    def execute(self):
        self.receiver.close_spotify()

class PlaySpotifyCommand(Command):
    def __init__(self,receiver):
        self.receiver = receiver

    def execute(self):
        self.receiver.play_song()
