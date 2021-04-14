class CommandNotPresentException(Exception):
    def __init__(self, command, commands_list):
        self.message = 'The command {} is not configured, the available commands are {}'.format(command, commands_list)

    def __str__(self):
        return self.message
