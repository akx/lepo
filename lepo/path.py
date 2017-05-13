import re

from lepo.path_view import PathView


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
