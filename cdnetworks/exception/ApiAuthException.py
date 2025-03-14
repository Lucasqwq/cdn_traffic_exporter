class ApiAuthException(Exception):
    def __init__(self, message, cause=None):
        super().__init__(message)
        self.cause = cause
