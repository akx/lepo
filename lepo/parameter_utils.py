import base64

import iso8601
from django.utils.encoding import force_bytes, force_text

from lepo.excs import ErroneousParameters, MissingParameter


def cast_parameter_value(apidoc, parameter, value):
    if isinstance(parameter, dict):
        if apidoc:
            parameter_class = apidoc.operation_class.parameter_class
        else:
            raise NotImplementedError(
                'Must have an APIDoc context when passing a plain dict in to cast_parameter_value'
            )

        parameter = parameter_class(parameter)
    return parameter.cast(apidoc, value)


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
            params[param.name] = param.cast(request.api_info.api, value)
        except NotImplementedError:
            raise
        except Exception as e:
            errors[param.name] = e
    if errors:
        raise ErroneousParameters(errors, params)
    return params
