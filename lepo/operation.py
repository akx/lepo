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

