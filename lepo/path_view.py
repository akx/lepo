from django.http import HttpResponse, JsonResponse
from django.views import View

from lepo.api_info import APIInfo
from lepo.excs import ExceptionalResponse, InvalidOperation
from lepo.parameter_utils import read_parameters
from lepo.utils import snake_case


class PathView(View):
    router = None  # Filled in by subclasses
    path = None  # Filled in by subclasses

    def dispatch(self, request, **kwargs):
        try:
            operation = self.path.get_operation(request.method)
        except InvalidOperation:
            return self.http_method_not_allowed(request, **kwargs)
        request.api_info = APIInfo(
            operation=operation,
            router=self.router,
        )
        params = {
            snake_case(name): value
            for (name, value)
            in read_parameters(request, kwargs, capture_errors=True).items()
        }
        handler = request.api_info.router.get_handler(operation.id)
        try:
            response = handler(request, **params)
        except ExceptionalResponse as er:
            response = er.response

        return self.transform_response(response)

    def transform_response(self, response):
        if isinstance(response, HttpResponse):
            # TODO: validate against responses
            return response
        return JsonResponse(response, safe=False)  # TODO: maybe less TIMTOWDI here?
