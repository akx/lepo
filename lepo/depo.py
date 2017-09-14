from collections import OrderedDict, defaultdict
import inspect

type_map = {
    str: 'str',
    int: 'integer',
    float: 'float',
}


class DepoParameter:
    def __init__(self, *, type, location, description=None, required=False):
        self.type = type
        self.location = location
        self.description = description
        self.required = required


class DepoOperation:
    def __init__(self, *, function, method, path, id=None):
        self.function = function
        self.method = str(method).lower()
        self.path = path
        self.id = str(id or function.__name__)

    def to_openapi(self):
        sig = inspect.signature(self.function)
        parameters = [
            OrderedDict([kv for kv in [
                ('name', param.name),
                ('in', param.annotation.location),
                ('description', param.annotation.description),
                ('required', param.annotation.required),
                ('type', type_map.get(param.annotation.type, str(param.annotation.type))),
            ] if kv[1] is not None])
            for param
            in sorted(sig.parameters.values(), key=lambda p: p.name)
            if param.annotation != sig.empty and isinstance(param.annotation, DepoParameter)
        ]
        return OrderedDict([
            ('description', inspect.getdoc(self.function)),
            ('operationId', self.id),
            ('parameters', parameters),
        ])


class Depo:
    def __init__(self):
        self.operations = []

    def operation(self, *, method, path, id=None):
        def decorator(fn):
            self.operations.append(DepoOperation(
                function=fn,
                method=method,
                path=path,
                id=id,
            ))
            return fn

        return decorator

    def param(self, **kwargs):
        return DepoParameter(**kwargs)

    def to_openapi(self):
        doc = OrderedDict([
            ('swagger', '2.0'),
            ('info', {}),
            ('host', 'https://example.com'),
            ('schemes', ['http']),
            ('consumes', ['application/json']),
            ('produces', ['application/json']),
        ])
        doc['paths'] = paths = OrderedDict()
        by_path_and_method = defaultdict(dict)
        for op in self.operations:
            by_path_and_method[op.path][op.method] = op
        for path, by_method in sorted(by_path_and_method.items()):
            path = paths.setdefault(path, OrderedDict())
            for method, op in sorted(by_method.items()):
                path[method] = op.to_openapi()
        return doc
