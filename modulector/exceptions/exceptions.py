class SourceNotPresentException(Exception):
    def __init__(self, source_id):
        self.message = 'The source id {} is not configured'.format(source_id)
