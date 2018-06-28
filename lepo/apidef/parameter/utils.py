import json

from lepo.excs import InvalidBodyContent


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
