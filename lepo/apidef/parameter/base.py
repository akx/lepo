import jsonschema

from lepo.parameter_utils import cast_primitive_value
from lepo.utils import maybe_resolve

OPENAPI_JSONSCHEMA_VALIDATION_KEYS = (
    'maximum', 'exclusiveMaximum',
    'minimum', 'exclusiveMinimum',
    'maxLength', 'minLength',
    'pattern',
    'maxItems', 'minItems',
    'uniqueItems',
    'enum', 'multipleOf',
)


class BaseParameter:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return '<%s (%r)>' % (self.__class__.__name__, self.data)

    @property
    def location(self):
        return self.data['in']

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
    def required(self):
        return bool(self.data.get('required'))

    @property
    def default(self):
        return self.data.get('default')

    @property
    def validation_keys(self):
        return {
            key: self.data[key]
            for key in self.data
            if key in OPENAPI_JSONSCHEMA_VALIDATION_KEYS
        }

    @property
    def items(self):
        return self.data.get('items')

    def validate_primitive(self, value):
        jsonschema_validation_object = self.validation_keys
        if jsonschema_validation_object:
            jsonschema.validate(value, jsonschema_validation_object)
        return value

    def validate_schema(self, api, value):
        schema = maybe_resolve(self.schema, resolve=api.resolve_reference)
        jsonschema.validate(value, schema, resolver=api.resolver)
        if 'discriminator' in schema:  # Swagger Polymorphism support
            type = value[schema['discriminator']]
            actual_type = '#/definitions/%s' % type
            schema = api.resolve_reference(actual_type)
            jsonschema.validate(value, schema, resolver=api.resolver)
        return value

    def cast_array(self, api, value):
        if not isinstance(value, list):  # could be a list already if collection format was multi
            value = self.arrayfy_value(value)
        items_param = self.__class__(self.items)
        return [items_param.cast(api, item) for item in value]

    def arrayfy_value(self, value):
        raise NotImplementedError('...')

    def cast(self, api, value):
        if self.type == 'array':
            value = self.cast_array(api, value)

        if self.schema:
            return self.validate_schema(api, value)

        value = cast_primitive_value(self.type, self.format, value)
        value = self.validate_primitive(value)
        return value

    def get_value(self, request, view_kwargs):  # pragma: no cover
        """
        :type request: WSGIRequest
        :type view_kwargs: dict
        """
        raise NotImplementedError('...')


class BaseTopParameter(BaseParameter):
    """
    Top-level Parameter, such as in an operation
    """

    def __init__(self, data, operation=None):
        super(BaseTopParameter, self).__init__(data)
        self.operation = operation

    @property
    def name(self):
        return self.data['name']

    @property
    def in_body(self):
        return self.location in ('formData', 'body')

    def get_value(self, request, view_kwargs):
        if self.location == 'path':
            return view_kwargs[self.name]

        if self.location == 'header':
            return request.META['HTTP_%s' % self.name.upper().replace('-', '_')]

        raise NotImplementedError('unsupported `in` value %r in %r' % (self.location, self))  # pragma: no cover
