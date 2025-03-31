from commands.spotify_commands import PlaySpotifyCommand


class VoiceCommandInvoker:
    def __init__(self):
        self.commands = {}

    def set_command(self, command_name, command):
        self.commands[command_name] = command
        print("set command " +command_name )
    def execute_command(self, command_name,  *args):
        if command_name in self.commands:
            command = self.commands[command_name]
            if isinstance(command, PlaySpotifyCommand):
                command.set_song(args[0])

            self.commands[command_name].execute()
        else:
            print(f"Command '{command_name}' not recognized.")