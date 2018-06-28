import json

from lepo.excs import InvalidBodyContent, InvalidBodyFormat

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
    def collection_format(self):
        return self.data.get('collectionFormat')

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

    def get_value(self, request, view_kwargs):  # pragma: no cover
        """
        :type request: WSGIRequest
        :type view_kwargs: dict
        """
        raise NotImplementedError('...')


class Parameter(BaseParameter):
    """
    Top-level Parameter, such as in an operation
    """

    def __init__(self, data, operation=None):
        super(Parameter, self).__init__(data)
        self.operation = operation

    @property
    def name(self):
        return self.data['name']

    @property
    def in_body(self):
        return self.location in ('formData', 'body')

    def get_value(self, request, view_kwargs):
        if self.location == 'formData' and self.type == 'file':
            return request.FILES[self.name]

        if self.location in ('query', 'formData'):
            source = (request.POST if self.location == 'formData' else request.GET)
            if self.type == 'array' and self.collection_format == 'multi':
                return source.getlist(self.name)
            else:
                return source[self.name]

        if self.location == 'path':
            return view_kwargs[self.name]

        if self.location == 'header':
            return request.META['HTTP_%s' % self.name.upper().replace('-', '_')]

        raise NotImplementedError('unsupported `in` value in %r' % self)  # pragma: no cover


class Swagger2Parameter(Parameter):

    def get_value(self, request, view_kwargs):
        if self.location == 'body':
            return self.read_body(request)

        return super().get_value(request, view_kwargs)

    def read_body(self, request):
        consumes = request.api_info.operation.consumes
        if request.content_type not in consumes:
            raise InvalidBodyFormat('Content-type %s is not supported (%r are)' % (
                request.content_type,
                consumes,
            ))

        try:
            if request.content_type == 'application/json':
                return json.loads(request.body.decode(request.content_params.get('charset', 'UTF-8')))
            elif request.content_type == 'text/plain':
                return request.body.decode(request.content_params.get('charset', 'UTF-8'))
        except Exception as exc:
            raise InvalidBodyContent('Unable to parse this body as %s' % request.content_type) from exc
        raise NotImplementedError('No idea how to parse content-type %s' % request.content_type)  # pragma: no cover
