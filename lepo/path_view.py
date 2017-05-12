import json

from django.http import HttpResponse, HttpRequest
from django.http.response import JsonResponse
from django.views import View

from lepo.excs import MissingParameter


def read_parameters(operation, request, view_kwargs):
    """
    :type operation: dict 
    :type request: HttpRequest 
    :type view_kwargs: dict[str, object]
    :rtype: dict[str, object] 
    """
    params = {}
    for param in operation['parameters']:
        try:
            if param['in'] == 'query':
                value = request.GET[param['name']]
            elif param['in'] == 'path':
                value = view_kwargs[param['name']]
            elif param['in'] == 'body':
                # TODO: support other formats than JSON
                value = json.load(request)  # use the file-like API of HTTPRequests
            else:
                raise ValueError('unsupported `in` value in %r' % param)
        except KeyError:
            if param.get('required'):
                raise MissingParameter('parameter %s is required but missing' % param['name'])
            continue
        # TODO: validate type and format?
        params[param['name']] = value
    return params


class APIInfo:
    def __init__(self, api, path, operation):
        self.api = api
        self.path = path
        self.operation = operation



class PathView(View):
    api = None  # Filled in by subclasses
    path = None  # Filled in by subclasses

    def dispatch(self, request, **kwargs):
        operation = self.path.mapping.get(request.method.lower())
        if not operation:
            return self.http_method_not_allowed(request, **kwargs)
        operation_id = operation['operationId']
        params = read_parameters(operation, request, kwargs)
        handler = self.api.get_handler(operation_id)
        request.api_info = APIInfo(api=self.api, path=self.path, operation=operation)
        response = handler(request, **params)
        if isinstance(response, HttpResponse):
            # TODO: validate against responses
            return response
        return JsonResponse(response, safe=False)  # TODO: maybe less TIMTOWDI here?
