class BaseParameter:
    def __init__(self, data):
        self.data = data

    def __repr__(self):
        return '<%s (%r)>' % (self.__class__.__name__, self.data)

    @property
    def location(self):
        return self.data['in']

    @property
    def required(self):
        return bool(self.data.get('required'))

    @property
    def items(self):
        return self.data.get('items')

    def cast(self, api, value):
        raise NotImplementedError('...')

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
        raise NotImplementedError('unsupported `in` value %r in %r' % (self.location, self))  # pragma: no cover
