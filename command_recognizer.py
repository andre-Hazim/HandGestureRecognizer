import subprocess

# Command interface
class Command:
    def execute(self):
        pass

# Concrete Command to open Spotify
class OpenSpotifyCommand(Command):
    def __init__(self, receiver):
        self.receiver = receiver

    def execute(self):
        self.receiver.open_spotify()

# Receiver class: This is where the actual work happens
class VoiceReceiver:
    @staticmethod
    def open_spotify():
        print("Opening Spotify...")
        subprocess.run("spotify.exe")

class VoiceCommandInvoker:
    def __init__(self):
        self.commands = {}

    def set_command(self, command_name, command):
        self.commands[command_name] = command

    def execute_command(self, command_name):
        if command_name in self.commands:
            self.commands[command_name].execute()
        else:
            print(f"Command '{command_name}' not recognized.")