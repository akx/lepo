import re

from lepo.excs import InvalidOperation
from lepo.path_view import PathView

PATH_PLACEHOLDER_REGEX = r'\{(.+?)\}'

# As defined in the documentation for Path Items:
METHODS = {'get', 'put', 'post', 'delete', 'options', 'head', 'patch'}


class Path:
    def __init__(self, api, path, mapping):
        """
        :type api: lepo.apidef.APIDefinition
        :type path: str
        :type mapping: dict
        """
        self.api = api
        self.path = path
        self.mapping = mapping
        self.regex = self._build_regex()
        self.name = self._build_view_name()

    def get_view_class(self, router):
        return type('%sView' % self.name.title(), (PathView,), {
            'path': self,
            'router': router,
        })

    def _build_view_name(self):
        path = re.sub(PATH_PLACEHOLDER_REGEX, r'\1', self.path)
        name = re.sub(r'[^a-z0-9]+', '-', path, flags=re.I).strip('-').lower()
        return name

    def _build_regex(self):
        return re.sub(
            PATH_PLACEHOLDER_REGEX,
            lambda m: '(?P<%s>[^/]+?)' % m.group(1),
            self.path,
        ).lstrip('/') + '$'

    def get_operation(self, method):
        operation_data = self.mapping.get(method.lower())
        if not operation_data:
            raise InvalidOperation('Path %s does not support method %s' % (self.path, method.upper()))
        return self.api.operation_class(api=self.api, path=self, data=operation_data, method=method)

    def get_operations(self):
        for method in METHODS:
            if method in self.mapping:
                yield self.get_operation(method)
