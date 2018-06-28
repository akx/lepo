from fnmatch import fnmatch

from django.utils.text import camel_case_to_spaces


def maybe_resolve(object, resolve):
    """
    Call `resolve` on the `object`'s `$ref` value if it has one.

    :param object: An object.
    :param resolve: A resolving function.
    :return: An object, or some other object! :sparkles:
    """
    if isinstance(object, dict) and object.get('$ref'):
        return resolve(object['$ref'])
    return object


def snake_case(string):
    return camel_case_to_spaces(string).replace(' ', '_')


def match_content_type(content_type, content_type_mapping):
    for map_content_type in content_type_mapping:
        if fnmatch(content_type, map_content_type):
            return map_content_type


def get_content_type_specificity(content_type):
    major, minor = content_type.split('/', 1)
    return (100 if major == '*' else 0) + (10 if minor == '*' else 0)
