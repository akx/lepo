import jsonschema

from lepo.apidef.parameter.base import BaseParameter, BaseTopParameter, NO_VALUE
from lepo.apidef.parameter.utils import comma_split, pipe_split, read_body, space_split, tab_split, validate_schema
from lepo.excs import InvalidBodyFormat
from lepo.parameter_utils import cast_primitive_value
from lepo.utils import maybe_resolve

COLLECTION_FORMAT_SPLITTERS = {
    'csv': comma_split,
    'ssv': space_split,
    'tsv': tab_split,
    'pipes': pipe_split,
}

OPENAPI_JSONSCHEMA_VALIDATION_KEYS = (
    'maximum', 'exclusiveMaximum',
    'minimum', 'exclusiveMinimum',
    'maxLength', 'minLength',
    'pattern',
    'maxItems', 'minItems',
    'uniqueItems',
    'enum', 'multipleOf',
)


class Swagger2BaseParameter(BaseParameter):

    @property
    def type(self):
        return self.data.get('type')

    @property
    def format(self):
        return self.data.get('format')

    @property
    def schema(self):
        return self.data.get('schema')

    @property
    def has_default(self):
        return 'default' in self.data

    @property
    def default(self):
        return self.data.get('default')

    @property
    def collection_format(self):
        return self.data.get('collectionFormat')

    @property
    def validation_keys(self):
        return {
            key: self.data[key]
            for key in self.data
            if key in OPENAPI_JSONSCHEMA_VALIDATION_KEYS
        }

    def validate_primitive(self, value):
        jsonschema_validation_object = self.validation_keys
        if jsonschema_validation_object:
            jsonschema.validate(value, jsonschema_validation_object)
        return value

    def validate_schema(self, api, value):
        schema = maybe_resolve(self.schema, resolve=api.resolve_reference)
        return validate_schema(schema, api, value)

    def arrayfy_value(self, value):
        collection_format = self.collection_format or 'csv'
        splitter = COLLECTION_FORMAT_SPLITTERS.get(collection_format)
        if not splitter:
            raise NotImplementedError('unsupported collection format in %r' % self)
        value = splitter(value)
        return value

    def cast_array(self, api, value):
        if not isinstance(value, list):  # could be a list already if collection format was multi
            value = self.arrayfy_value(value)
        items_param = Swagger2BaseParameter(self.items, api=api)
        return [items_param.cast(api, item) for item in value]

    def cast(self, api, value):
        if self.type == 'array':
            value = self.cast_array(api, value)

        if self.schema:
            return self.validate_schema(api, value)

        value = cast_primitive_value(self.type, self.format, value)
        value = self.validate_primitive(value)
        return value


class Swagger2Parameter(Swagger2BaseParameter, BaseTopParameter):

    def get_value(self, request, view_kwargs):
        if self.location == 'path':
            return view_kwargs.get(self.name, NO_VALUE)

        if self.location == 'header':
            meta_key = 'HTTP_%s' % self.name.upper().replace('-', '_')
            return request.META.get(meta_key, NO_VALUE)

        if self.location == 'body':
            return self.read_body(request)

        if self.location == 'formData' and self.type == 'file':
            return request.FILES.get(self.name, NO_VALUE)

        if self.location in ('query', 'formData'):
            source = (request.POST if self.location == 'formData' else request.GET)

            if self.name not in source:
                return NO_VALUE

            if self.type == 'array' and self.collection_format == 'multi':
                return source.getlist(self.name)
            else:
                return source[self.name]

        return super().get_value(request, view_kwargs)  # pragma: no cover

    def read_body(self, request):
        consumes = request.api_info.operation.consumes
        if request.content_type not in consumes:
            raise InvalidBodyFormat('Content-type %s is not supported (%r are)' % (
                request.content_type,
                consumes,
            ))

        return read_body(request, None)
