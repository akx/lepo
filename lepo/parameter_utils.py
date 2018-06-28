import base64

import iso8601
import jsonschema
from django.utils.encoding import force_bytes, force_text

from lepo.apidef.parameter import BaseParameter
from lepo.excs import ErroneousParameters, MissingParameter
from lepo.utils import maybe_resolve

COLLECTION_FORMAT_SPLITTERS = {
    'csv': lambda value: force_text(value).split(','),
    'ssv': lambda value: force_text(value).split(' '),
    'tsv': lambda value: force_text(value).split('\t'),
    'pipes': lambda value: force_text(value).split('|'),
}


def cast_parameter_value(apidoc, parameter, value):
    if isinstance(parameter, dict):
        parameter = BaseParameter(parameter)
    if parameter.type == 'array':
        if not isinstance(value, list):  # could be a list already if collection format was multi
            collection_format = parameter.collection_format or 'csv'
            splitter = COLLECTION_FORMAT_SPLITTERS.get(collection_format)
            if not splitter:
                raise NotImplementedError('unsupported collection format in %r' % parameter)
            value = splitter(value)
        items = parameter.items
        value = [cast_parameter_value(apidoc, items, item) for item in value]
    if parameter.schema:
        schema = maybe_resolve(parameter.schema, apidoc.resolve_reference)
        jsonschema.validate(value, schema, resolver=apidoc.resolver)
        if 'discriminator' in schema:  # Swagger Polymorphism support
            type = value[schema['discriminator']]
            actual_type = '#/definitions/%s' % type
            schema = apidoc.resolve_reference(actual_type)
            jsonschema.validate(value, schema, resolver=apidoc.resolver)
        return value
    value = cast_primitive_value(parameter.type, parameter.format, value)
    jsonschema_validation_object = parameter.validation_keys
    if jsonschema_validation_object:
        jsonschema.validate(value, jsonschema_validation_object)
    return value


def cast_primitive_value(type, format, value):
    if type == 'boolean':
        return (force_text(value).lower() in ('1', 'yes', 'true'))
    if type == 'integer' or format in ('integer', 'long'):
        return int(value)
    if type == 'number' or format in ('float', 'double'):
        return float(value)
    if format == 'byte':  # base64 encoded characters
        return base64.b64decode(value)
    if format == 'binary':  # any sequence of octets
        return force_bytes(value)
    if format == 'date':  # ISO8601 date
        return iso8601.parse_date(value).date()
    if format == 'dateTime':  # ISO8601 datetime
        return iso8601.parse_date(value)
    if type == 'string':
        return force_text(value)
    return value


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
            value = param.get_value(request, view_kwargs)
        except KeyError:
            if param.has_default:
                params[param.name] = param.default
                continue
            if param.required:  # Required but missing
                errors[param.name] = MissingParameter('parameter %s is required but missing' % param.name)
            continue
        try:
            params[param.name] = cast_parameter_value(request.api_info.api, param, value)
        except NotImplementedError:
            raise
        except Exception as e:
            errors[param.name] = e
    if errors:
        raise ErroneousParameters(errors, params)
    return params
