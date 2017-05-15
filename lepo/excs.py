class MissingParameter(ValueError):
    pass


class InvalidOperation(ValueError):
    pass


class MissingHandler(ValueError):
    pass


class ErroneousParameters(Exception):
    def __init__(self, error_map):
        self.errors = error_map
