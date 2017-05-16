class MissingParameter(ValueError):
    pass


class InvalidOperation(ValueError):
    pass


class MissingHandler(ValueError):
    pass


class ErroneousParameters(Exception):
    def __init__(self, error_map, parameters):
        self.errors = error_map
        self.parameters = parameters


class InvalidBodyFormat(ValueError):
    pass


class InvalidBodyContent(ValueError):
    pass
