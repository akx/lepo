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
    def name(self):
        return self.data['name']

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


class Parameter(BaseParameter):
    """
    Top-level Parameter, such as in an operation
    """

    def __init__(self, data, operation=None):
        super(Parameter, self).__init__(data)
        self.operation = operation
