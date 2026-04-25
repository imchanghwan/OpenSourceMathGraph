class ParseError(Exception):
    def __init__(self, message, original=None):
        super().__init__(message)
        self.original = original