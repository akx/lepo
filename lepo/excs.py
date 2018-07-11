from django.core.exceptions import ImproperlyConfigured


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


class InvalidComplexContent(ValueError):
    def __init__(self, message, error_map):
        super(InvalidComplexContent, self).__init__(message)
        self.errors = error_map


class InvalidParameterDefinition(ImproperlyConfigured):
    pass


class RouterValidationError(Exception):
    def __init__(self, error_map):
        self.errors = error_map
        self.description = '\n'.join('%s: %s' % (operation.id, error) for (operation, error) in self.flat_errors)
        super(RouterValidationError, self).__init__('Router validation failed:\n%s' % self.description)

    @property
    def flat_errors(self):
        for operation, errors in sorted(self.errors.items(), key=str):
            for error in errors:
                yield (operation, error)


class ExceptionalResponse(Exception):
    """
    Wraps a Response in an exception.

    These exceptions are caught in PathView.
    """
    def __init__(self, response):
        self.response = response
