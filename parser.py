class Parser:

    @staticmethod
    def parse_voice_command(cmd):
        known_commands = ["open spotify", "close spotify"]

        if cmd in known_commands:
            return cmd, None
        parts = str(cmd).split(" ",1)
        command = parts[0].lower()
        args = parts[1] if len(parts) > 1 else None

        return command,args