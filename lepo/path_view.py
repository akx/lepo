from django.http import HttpResponse, JsonResponse
from django.views import View

from lepo.api_info import APIInfo
from lepo.excs import InvalidOperation, ExceptionalResponse
from lepo.parameters import read_parameters
from lepo.utils import snake_case


class PathView(View):
    router = None  # Filled in by subclasses
    path = None  # Filled in by subclasses

    def dispatch(self, request, **kwargs):
        try:
            operation = self.path.get_operation(request.method)
        except InvalidOperation:
            return self.http_method_not_allowed(request, **kwargs)
        request.api_info = APIInfo(operation=operation)
        params = dict(
            (snake_case(name), value)
            for (name, value)
            in read_parameters(request, kwargs).items()
        )
        handler = request.api_info.router.get_handler(operation.id)
        try:
            response = handler(request, **params)
        except ExceptionalResponse as er:
            response = er.response

        return self.transform_response(response)

    def transform_response(self, response):
        status = 200
        if isinstance(response, tuple):
            if len(response) != 2:
                raise ValueError('If a tuple is returned from a handler, it must be a 2-tuple')
            status = int(response[0])
            response = response[1]
        elif isinstance(response, HttpResponse):
            # TODO: validate against responses
            return response
        return JsonResponse(response, safe=False, status=status)  # TODO: maybe less TIMTOWDI here?
