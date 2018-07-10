from jsonschema import RefResolver

from lepo.apidef.operation.openapi import OpenAPI3Operation
from lepo.apidef.operation.swagger import Swagger2Operation
from lepo.apidef.path import Path
from lepo.apidef.version import OPENAPI_3, parse_version, SWAGGER_2
from lepo.utils import maybe_resolve


class APIDefinition:
    version = None
    path_class = Path
    operation_class = None

    def __init__(self, doc):
        """
        Instantiate a new Lepo router.

        :param doc: The OpenAPI definition document.
        :type doc: dict
        """
        self.doc = doc
        self.resolver = RefResolver('', self.doc)

    def resolve_reference(self, ref):
        """
        Resolve a JSON Pointer object reference to the object itself.

        :param ref: Reference string (`#/foo/bar`, for instance)
        :return: The object, if found
        :raises jsonschema.exceptions.RefResolutionError: if there is trouble resolving the reference
        """
        url, resolved = self.resolver.resolve(ref)
        return resolved

    def get_path_mapping(self, path):
        return maybe_resolve(self.doc['paths'][path], self.resolve_reference)

    def get_path_names(self):
        for path in self.doc['paths']:
            yield path

    def get_path(self, path):
        """
        Construct a Path object from a path string.

        The Path string must be declared in the API.

        :type path: str
        :rtype: lepo.path.Path
        """
        mapping = self.get_path_mapping(path)
        return self.path_class(api=self, path=path, mapping=mapping)

    def get_paths(self):
        """
        Iterate over all Path objects declared by the API.

        :rtype: Iterable[lepo.path.Path]
        """
        for path_name in self.get_path_names():
            yield self.get_path(path_name)

    @classmethod
    def from_file(cls, filename):
        """
        Construct an APIDefinition by parsing the given `filename`.

        If PyYAML is installed, YAML files are supported.
        JSON files are always supported.

        :param filename: The filename to read.
        :rtype: APIDefinition
        """
        with open(filename) as infp:
            if filename.endswith('.yaml') or filename.endswith('.yml'):
                import yaml
                data = yaml.safe_load(infp)
            else:
                import json
                data = json.load(infp)
        return cls.from_data(data)

    @classmethod
    def from_data(cls, data):
        version = parse_version(data)
        if version == SWAGGER_2:
            return Swagger2APIDefinition(data)
        if version == OPENAPI_3:
            return OpenAPI3APIDefinition(data)
        raise NotImplementedError('We can never get here.')  # pragma: no cover

    @classmethod
    def from_yaml(cls, yaml_string):
        from yaml import safe_load
        return cls.from_data(safe_load(yaml_string))


class Swagger2APIDefinition(APIDefinition):
    version = SWAGGER_2
    operation_class = Swagger2Operation


class OpenAPI3APIDefinition(APIDefinition):
    version = OPENAPI_3
    operation_class = OpenAPI3Operation
