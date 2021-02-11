class SourceNotPresentException(Exception):
    def __init__(self, source):
        self.message = 'The source {} is not configured'.format(source)
