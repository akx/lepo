import json

import jsonschema
from django.core.files import File
from jsonschema import Draft4Validator

from lepo.excs import InvalidBodyContent
from lepo.utils import maybe_resolve


def read_body(request, parameter=None):
    if parameter:
        if parameter.type == 'binary':
            return request.body.read()
    try:
        if request.content_type == 'application/json':
            return json.loads(request.body.decode(request.content_params.get('charset', 'UTF-8')))
        elif request.content_type == 'text/plain':
            return request.body.decode(request.content_params.get('charset', 'UTF-8'))
        if request.content_type == 'multipart/form-data':
            # TODO: this definitely doesn't handle multiple values for the same key correctly
            data = dict()
            data.update(request.POST.items())
            data.update(request.FILES.items())
            return data
    except Exception as exc:
        raise InvalidBodyContent('Unable to parse this body as %s' % request.content_type) from exc
    raise NotImplementedError('No idea how to parse content-type %s' % request.content_type)  # pragma: no cover


class LepoDraft4Validator(Draft4Validator):
    def iter_errors(self, instance, _schema=None):
        if isinstance(instance, File):
            # Skip validating File instances that come from POST requests...
            return
        for error in super(LepoDraft4Validator, self).iter_errors(instance, _schema):
            yield error


def validate_schema(schema, api, value):
    schema = maybe_resolve(schema, resolve=api.resolve_reference)
    jsonschema.validate(
        value,
        schema,
        cls=LepoDraft4Validator,
        resolver=api.resolver,
    )
    if 'discriminator' in schema:  # Swagger Polymorphism support
        type = value[schema['discriminator']]
        actual_type = '#/definitions/%s' % type
        schema = api.resolve_reference(actual_type)
        jsonschema.validate(
            value,
            schema,
            cls=LepoDraft4Validator,
            resolver=api.resolver,
        )
    return value
