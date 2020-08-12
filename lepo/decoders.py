import json

from django.utils.encoding import force_str

DEFAULT_ENCODING = 'utf-8'


def decode_json(content, encoding=None, **kwargs):
    return json.loads(force_str(content, encoding=(encoding or DEFAULT_ENCODING)))


def decode_plain_text(content, encoding=None, **kwargs):
    return force_str(content, encoding=(encoding or DEFAULT_ENCODING))


DECODERS = {
    'application/json': decode_json,
    'text/plain': decode_plain_text,
}


def get_decoder(content_type):
    """
    Get a decoder function for the content type given, or None if there is none.

    :param content_type: Content type string
    :type content_type: str
    :return: function or None
    """
    if content_type.endswith('+json'):  # Process all +json vendor types like JSON
        content_type = 'application/json'

    if content_type in DECODERS:
        return DECODERS[content_type]

    return None
