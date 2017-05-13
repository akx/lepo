from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views import View

from lepo.parameters import read_parameters


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
        request.api_info = APIInfo(api=self.api, path=self.path, operation=operation)
        params = read_parameters(request.api_info, request, kwargs)
        handler = self.api.get_handler(operation_id)
        response = handler(request, **params)
        if isinstance(response, HttpResponse):
            # TODO: validate against responses
            return response
        return JsonResponse(response, safe=False)  # TODO: maybe less TIMTOWDI here?
