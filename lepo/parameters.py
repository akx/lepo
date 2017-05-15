import json

import jsonschema
from django.utils.encoding import force_text

from lepo.excs import ErroneousParameters, InvalidBodyContent, InvalidBodyFormat, MissingParameter


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


def read_body(request):
    consumes = request.api_info.operation.consumes
    if request.content_type not in consumes:
        raise InvalidBodyFormat('Content-type %s is not supported (%r are)' % (
            request.content_type,
            consumes,
        ))
    try:
        if request.content_type == 'application/json':
            return json.loads(request.body.decode(request.content_params.get('charset', 'UTF-8')))
        elif request.content_type == 'text/plain':
            return request.body.decode(request.content_params.get('charset', 'UTF-8'))
    except Exception as exc:
        raise InvalidBodyContent('Unable to parse this body as %s' % request.content_type) from exc
    raise InvalidBodyFormat('This API has no idea how to parse content-type %s' % request.content_type)


def get_parameter_value(request, view_kwargs, param):
    if param['in'] == 'query':
        return request.GET[param['name']]
    elif param['in'] == 'path':
        return view_kwargs[param['name']]
    elif param['in'] == 'body':
        return read_body(request)
    else:
        raise NotImplementedError('unsupported `in` value in %r' % param)


def read_parameters(request, view_kwargs):
    """
    :param request: HttpRequest with attached api_info
    :type request: HttpRequest
    :type view_kwargs: dict[str, object]
    :rtype: dict[str, object]
    """
    params = {}
    errors = {}
    for param in request.api_info.operation.parameters:
        try:
            value = get_parameter_value(request, view_kwargs, param)
        except KeyError:
            if param.get('required'):
                raise MissingParameter('parameter %s is required but missing' % param['name'])
            continue
        try:
            params[param['name']] = coerce_parameter(request.api_info, param, value)
        except Exception as e:
            errors[param['name']] = e
    if errors:
        raise ErroneousParameters(errors)
    return params
