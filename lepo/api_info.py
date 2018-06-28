class APIInfo:
    def __init__(self, operation, router=None):
        """
        :type operation: lepo.operation.Operation
        :type router: lepo.router.Router
        """
        self.api = operation.api
        self.path = operation.path
        self.operation = operation
        self.router = router
