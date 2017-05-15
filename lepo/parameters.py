import json

import jsonschema
from django.utils.encoding import force_text

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


def get_parameter_value(request, view_kwargs, param):
    if param['in'] == 'query':
        return request.GET[param['name']]
    elif param['in'] == 'path':
        return view_kwargs[param['name']]
    elif param['in'] == 'body':
        # TODO: support other formats than JSON
        return json.loads(request.body.decode('UTF-8'))
    else:
        raise NotImplementedError('unsupported `in` value in %r' % param)


def read_parameters(api_info, request, view_kwargs):
    """
    :type api_info: APIInfo
    :type request: HttpRequest
    :type view_kwargs: dict[str, object]
    :rtype: dict[str, object]
    """
    params = {}
    errors = {}
    for param in api_info.operation.parameters:
        try:
            value = get_parameter_value(request, view_kwargs, param)
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
