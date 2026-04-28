class BaseError(Exception):
    def __init__(self, message, original: Exception | None):
        super().__init__(message)
        self.original = original