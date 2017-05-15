from django.http import HttpResponse
from django.http.response import JsonResponse
from django.views import View

from lepo.api_info import APIInfo
from lepo.excs import InvalidOperation
from lepo.parameters import read_parameters


class PathView(View):
    api = None  # Filled in by subclasses
    path = None  # Filled in by subclasses

    def dispatch(self, request, **kwargs):
        try:
            operation = self.path.get_operation(request.method)
        except InvalidOperation:
            return self.http_method_not_allowed(request, **kwargs)
        request.api_info = APIInfo(api=self.api, path=self.path, operation=operation)
        params = read_parameters(request.api_info, request, kwargs)
        handler = self.api.get_handler(operation.id)
        response = handler(request, **params)
        if isinstance(response, HttpResponse):
            # TODO: validate against responses
            return response
        return JsonResponse(response, safe=False)  # TODO: maybe less TIMTOWDI here?
