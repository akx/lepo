from collections import Iterable
from copy import deepcopy
from functools import reduce
from importlib import import_module

from django.conf.urls import url
from django.http import HttpResponse
from django.utils.text import camel_case_to_spaces
from jsonschema import RefResolver

from lepo.excs import MissingHandler
from lepo.path import Path
from lepo.utils import maybe_resolve


def root_view(request):
    return HttpResponse('API root')


class Router:
    path_class = Path

    def __init__(self, api):
        self.api = deepcopy(api)
        self.api.pop('host', None)
        self.handlers = {}
        self.resolver = RefResolver('', self.api)

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

    def get_path(self, path):
        """
        Construct a Path object from a path string.

        The Path string must be declared in the API.

        :type path: str
        :rtype: lepo.path.Path
        """
        mapping = maybe_resolve(self.api['paths'][path], self.resolve_reference)
        return self.path_class(api=self, path=path, mapping=mapping)

    def get_paths(self):
        for path in self.api['paths']:
            yield self.get_path(path)

    def get_urls(
        self,
        root_view_name=None,
        optional_trailing_slash=False,
        decorate=(),
        name_template='{name}',
    ):
        """
        Get the router's URLs, ready to be installed in `urlpatterns` (directly or via `include`).

        :param root_view_name: The optional url name for an API root view.
                               This may be useful for projects that do not explicitly know where the
                               router is mounted; those projects can then use `reverse('api:root')`,
                               for instance, if they need to construct URLs based on the API's root URL.
        :type root_view_name: str|None

        :param optional_trailing_slash: Whether to fix up the regexen for the router to make any trailing
                                        slashes optional.
        :type optional_trailing_slash: bool

        :param decorate: A function to decorate view functions with, or an iterable of such decorators.
                         Use `(lepo.decorators.csrf_exempt,)` to mark all API views as CSRF exempt.
        :type decorate: function|Iterable[function]

        :param name_template: A `.format()` template for view naming.
        :type name_template: str

        :return: List of URL tuples.
        :rtype: list[tuple]
        """
        if isinstance(decorate, Iterable):
            decorators = decorate

            def decorate(view):
                return reduce(lambda view, decorator: decorator(view), decorators, view)

        urls = []
        for path in self.get_paths():
            regex = path.regex
            if optional_trailing_slash:
                regex = regex.rstrip('$')
                if not regex.endswith('/'):
                    regex += '/'
                regex += '?$'
            view = decorate(path.view_class.as_view())
            urls.append(url(regex, view, name=name_template.format(name=path.name)))

        if root_view_name:
            urls.append(url(r'^$', root_view, name=name_template.format(name=root_view_name)))
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

    def resolve_reference(self, ref):
        url, resolved = self.resolver.resolve(ref)
        return resolved
