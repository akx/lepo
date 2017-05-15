class APIInfo:
    def __init__(self, api, path, operation):
        """
        :type api: lepo.router.Router
        :type path: lepo.path.Path
        :type operation: lepo.operation.Operation
        """
        self.api = api
        self.path = path
        self.operation = operation
