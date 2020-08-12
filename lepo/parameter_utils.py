import base64

import iso8601
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_bytes, force_str

from lepo.apidef.parameter.base import NO_VALUE
from lepo.excs import ErroneousParameters, MissingParameter


def cast_primitive_value(type, format, value):
    if type == 'boolean':
        return (force_str(value).lower() in ('1', 'yes', 'true'))
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
        return force_str(value)
    return value


def read_parameters(request, view_kwargs=None, capture_errors=False):  # noqa: C901
    """
    :param request: HttpRequest with attached api_info
    :type request: HttpRequest
    :type view_kwargs: dict[str, object]
    :type capture_errors: bool
    :rtype: dict[str, object]
    """
    if view_kwargs is None:
        view_kwargs = {}
    params = {}
    errors = {}
    for param in request.api_info.operation.parameters:
        try:
            value = param.get_value(request, view_kwargs)
            if value is NO_VALUE:
                if param.has_default:
                    params[param.name] = param.default
                elif param.required:  # Required but missing
                    errors[param.name] = MissingParameter('parameter %s is required but missing' % param.name)
                continue  # No value, or a default was added, or an error was added.
            params[param.name] = param.cast(request.api_info.api, value)
        except (NotImplementedError, ImproperlyConfigured):
            raise
        except Exception as e:
            if not capture_errors:
                raise
            errors[param.name] = e
    if errors:
        raise ErroneousParameters(errors, params)
    return params
