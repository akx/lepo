class APIInfo:
    def __init__(self, operation):
        """
        :type operation: lepo.operation.Operation
        """
        self.api = operation.api
        self.path = operation.path
        self.operation = operation
