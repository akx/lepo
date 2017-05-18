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
