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