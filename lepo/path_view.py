from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views import View

from lepo.api_info import APIInfo
from lepo.operation import Operation
from lepo.parameters import read_parameters


class PathView(View):
    api = None  # Filled in by subclasses
    path = None  # Filled in by subclasses

    def dispatch(self, request, **kwargs):
        operation_data = self.path.mapping.get(request.method.lower())
        if not operation_data:
            return self.http_method_not_allowed(request, **kwargs)
        operation = Operation(api=self.api, path=self.path, data=operation_data)
        request.api_info = APIInfo(api=self.api, path=self.path, operation=operation)
        params = read_parameters(request.api_info, request, kwargs)
        handler = self.api.get_handler(operation.id)
        response = handler(request, **params)
        if isinstance(response, HttpResponse):
            # TODO: validate against responses
            return response
        return JsonResponse(response, safe=False)  # TODO: maybe less TIMTOWDI here?
