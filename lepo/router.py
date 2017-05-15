from copy import deepcopy
from importlib import import_module

from django.conf.urls import url
from django.utils.text import camel_case_to_spaces

from lepo.excs import MissingHandler
from lepo.path import Path


class Router:
    path_class = Path

    def __init__(self, api):
        self.api = deepcopy(api)
        self.api.pop('host', None)
        self.handlers = {}

    @classmethod
    def from_file(cls, filename):
        with open(filename) as infp:
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                import yaml
                data = yaml.safe_load(infp)
            else:
                import json
                data = json.load(infp)
        return cls(data)

    def get_urls(self):
        urls = []
        for path, mapping in self.api['paths'].items():
            path = self.path_class(api=self, path=path, mapping=mapping)
            urls.append(url(path.regex, path.view_class.as_view(), name=path.name))
        return urls

    def get_handler(self, operation_id):
        if operation_id in self.handlers:
            return self.handlers[operation_id]
        snake_operation_id = camel_case_to_spaces(operation_id).replace(' ', '_')
        if snake_operation_id in self.handlers:
            return self.handlers[snake_operation_id]
        raise MissingHandler(
            'Missing handler for operation %s (tried %s too)' % (operation_id, snake_operation_id)
        )

    def add_handlers(self, namespace):
        if isinstance(namespace, str):
            namespace = import_module(namespace)
        for name, value in vars(namespace).items():
            if name.startswith('_'):
                continue
            try:
                if callable(value):
                    self.handlers[name] = value
            except:
                pass

    def get_schema(self, ref):
        # TODO: This is not very skookum.
        for name, schema in self.api.get('definitions', {}).items():
            if ref == '#/definitions/%s' % name:
                return schema
