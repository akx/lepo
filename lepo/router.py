try:
    from collections.abc import Iterable
except ImportError:
    from collections import Iterable
from functools import reduce
from importlib import import_module
from inspect import isfunction, ismethod

from django.urls import re_path
from django.http import HttpResponse

from lepo.apidef.doc import APIDefinition
from lepo.excs import MissingHandler
from lepo.utils import snake_case


def root_view(request):
    return HttpResponse('API root')


class Router:

    def __init__(self, api):
        """
        Instantiate a new Lepo router.

        :param api: An APIDefinition object
        :type api: APIDefinition
        """
        assert isinstance(api, APIDefinition)
        self.api = api
        self.handlers = {}

    @classmethod
    def from_file(cls, filename):
        """
        Construct a Router by parsing the given `filename`.

        If PyYAML is installed, YAML files are supported.
        JSON files are always supported.

        :param filename: The filename to read.
        :rtype: Router
        """
        return cls(api=APIDefinition.from_file(filename))

    def get_path(self, path):
        return self.api.get_path(path)

    def get_paths(self):
        for path in self.api.get_path_names():
            yield self.get_path(path)

    def get_path_view_class(self, path):
        return self.get_path(path).get_view_class(router=self)

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
        for path in self.api.get_paths():
            regex = path.regex
            if optional_trailing_slash:
                regex = regex.rstrip('$')
                if not regex.endswith('/'):
                    regex += '/'
                regex += '?$'
            view = decorate(path.get_view_class(router=self).as_view())
            urls.append(re_path(regex, view, name=name_template.format(name=path.name)))

        if root_view_name:
            urls.append(re_path(r'^$', root_view, name=name_template.format(name=root_view_name)))
        return urls

    def get_handler(self, operation_id):
        """
        Get the handler function for a given operation.

        To remain Pythonic, both the original and the snake_cased version of the operation ID are
        supported.

        This could be overridden in a subclass.

        :param operation_id: Operation ID.
        :return: Handler function
        :rtype: function
        """
        handler = (
            self.handlers.get(operation_id)
            or self.handlers.get(snake_case(operation_id))
        )
        if handler:
            return handler
        raise MissingHandler(
            'Missing handler for operation %s (tried %s too)' % (operation_id, snake_case(operation_id))
        )

    def add_handlers(self, namespace):
        """
        Add handler functions from the given `namespace`, for instance a module.

        The namespace may be a string, in which case it is expected to be a name of a module.
        It may also be a dictionary mapping names to functions.

        Only non-underscore-prefixed functions and methods are imported.

        :param namespace: Namespace object.
        :type namespace: str|module|dict[str, function]
        """
        if isinstance(namespace, str):
            namespace = import_module(namespace)

        if isinstance(namespace, dict):
            namespace = namespace.items()
        else:
            namespace = vars(namespace).items()

        for name, value in namespace:
            if name.startswith('_'):
                continue
            if isfunction(value) or ismethod(value):
                self.handlers[name] = value
