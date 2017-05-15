from django.utils.functional import cached_property


class Operation:
    def __init__(self, api, path, data):
        """
        :type api: lepo.router.Router
        :type path: lepo.path.Path
        :type data: dict
        """
        self.api = api
        self.path = path
        self.data = data

    @property
    def id(self):
        return self.data['operationId']

    @property
    def parameters(self):
        return self.data.get('parameters', ())

    def _get_overridable(self, key, default=None):
        # TODO: This probes a little too deeply into the specifics of these objects, I think...
        for obj in (
            self.data,
            self.path.mapping,
            self.api.api,
        ):
            if key in obj:
                return obj[key]
        return default

    @cached_property
    def consumes(self):
        value = self._get_overridable('consumes', [])
        if not isinstance(value, (list, tuple)):
            raise TypeError('`consumes` must be a list, got %r' % value)
        return value

    @cached_property
    def produces(self):
        value = self._get_overridable('produces', [])
        if not isinstance(value, (list, tuple)):
            raise TypeError('`produces` must be a list, got %r' % value)
        return value
