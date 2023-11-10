class CommandNotPresentException(Exception):
    def __init__(self, command, commands_list):
        self.message = f'The command {command} is not configured, the available commands are {commands_list}'

    def __str__(self):
        return self.message
