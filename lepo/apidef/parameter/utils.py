import jsonschema
from django.core.files import File
from django.utils.encoding import force_str
from jsonschema import Draft4Validator

from lepo.decoders import get_decoder
from lepo.excs import InvalidBodyContent
from lepo.utils import maybe_resolve


def comma_split(value):
    return force_str(value).split(',')


def dot_split(value):
    return force_str(value).split('.')


def space_split(value):
    return force_str(value).split(' ')


def tab_split(value):
    return force_str(value).split('\t')


def pipe_split(value):
    return force_str(value).split('|')


def read_body(request, parameter=None):
    if parameter:
        if parameter.type == 'binary':
            return request.body.read()
    try:
        if request.content_type == 'multipart/form-data':
            # TODO: this definitely doesn't handle multiple values for the same key correctly
            data = dict()
            data.update(request.POST.items())
            data.update(request.FILES.items())
            return data
        decoder = get_decoder(request.content_type)
        if decoder:
            return decoder(request.body, encoding=request.content_params.get('charset', 'UTF-8'))
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
    if 'discriminator' in schema:  # Swagger/OpenAPI 3 Polymorphism support
        discriminator = schema['discriminator']
        if isinstance(discriminator, dict):  # OpenAPI 3
            type = value[discriminator['propertyName']]
            if 'mapping' in discriminator:
                actual_type = discriminator['mapping'][type]
            else:
                actual_type = '#/components/schemas/%s' % type
        else:
            type = value[discriminator]
            actual_type = '#/definitions/%s' % type
        schema = api.resolve_reference(actual_type)
        jsonschema.validate(
            value,
            schema,
            cls=LepoDraft4Validator,
            resolver=api.resolver,
        )
    return value
