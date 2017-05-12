import json

import jsonschema
from django.http import HttpRequest, HttpResponse
from django.http.response import JsonResponse
from django.utils.encoding import force_text
from django.views import View

from lepo.excs import ErroneousParameters, MissingParameter


def coerce_parameter(api_info, parameter, value):
    collection_format = parameter.get('collectionFormat')
    if collection_format:
        if collection_format == 'csv':
            value = force_text(value).split(',')
        else:
            raise NotImplementedError('unsupported collection format in %r' % parameter)
    if 'type' in parameter:
        if parameter['type'] == 'integer':
            value = int(value)
        # TODO: copy other bits from the parameter?
        jsonschema.validate(value, {'type': parameter['type']})
    elif 'schema' in parameter:
        schema = parameter['schema']
        if '$ref' in schema:
            schema = api_info.api.get_schema(schema['$ref'])
        jsonschema.validate(value, schema)
    return value


def read_parameters(api_info, request, view_kwargs):
    """
    :type api_info: APIInfo 
    :type request: HttpRequest 
    :type view_kwargs: dict[str, object]
    :rtype: dict[str, object] 
    """
    params = {}
    errors = {}
    for param in api_info.operation['parameters']:
        try:
            if param['in'] == 'query':
                value = request.GET[param['name']]
            elif param['in'] == 'path':
                value = view_kwargs[param['name']]
            elif param['in'] == 'body':
                # TODO: support other formats than JSON
                value = json.load(request)  # use the file-like API of HTTPRequests
            else:
                raise NotImplementedError('unsupported `in` value in %r' % param)
        except KeyError:
            if param.get('required'):
                raise MissingParameter('parameter %s is required but missing' % param['name'])
            continue
        try:
            params[param['name']] = coerce_parameter(api_info, param, value)
        except Exception as e:
            errors[param['name']] = e
    if errors:
        raise ErroneousParameters(errors)
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
        request.api_info = APIInfo(api=self.api, path=self.path, operation=operation)
        params = read_parameters(request.api_info, request, kwargs)
        handler = self.api.get_handler(operation_id)
        response = handler(request, **params)
        if isinstance(response, HttpResponse):
            # TODO: validate against responses
            return response
        return JsonResponse(response, safe=False)  # TODO: maybe less TIMTOWDI here?
