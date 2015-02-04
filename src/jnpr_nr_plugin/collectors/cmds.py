class Command(object):
    def __init__(self, name):
        self.name = name


class CommandResult(object):
    def __init__(self, name, result):
        self.name = name
        self.result = result
