import re

from lepo.excs import InvalidOperation
from lepo.operation import Operation
from lepo.path_view import PathView

# As defined in the documentation for Path Items:
METHODS = {'get', 'put', 'post', 'delete', 'options', 'head', 'patch'}


class Path:
    def __init__(self, api, path, mapping):
        self.api = api
        self.path = path
        self.mapping = mapping
        self.regex = re.sub(
            r'\{(.+?)\}',
            lambda m: '(?P<%s>.+?)' % m.group(1),
            self.path,
        ).lstrip('/') + '$'
        self.name = re.sub(  # todo: embetter
            r'[^a-z0-9]+',
            '-',
            self.path,
            re.I,
        ).strip('-')
        self.view_class = type('%sView' % self.name.title(), (PathView,), {
            'path': self,
            'api': self.api,
        })

    def get_operation(self, method):
        operation_data = self.mapping.get(method.lower())
        if not operation_data:
            raise InvalidOperation('Path %s does not support method %s' % (self.path, method.upper()))
        return Operation(api=self.api, path=self, data=operation_data, method=method)

    def get_operations(self):
        for method in METHODS:
            if method in self.mapping:
                yield self.get_operation(method)
