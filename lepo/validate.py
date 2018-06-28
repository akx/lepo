from collections import defaultdict

from lepo.excs import InvalidParameterDefinition, MissingHandler, RouterValidationError


def validate_router(router):
    errors = defaultdict(list)
    for path in router.get_paths():
        for operation in path.get_operations():
            # Check the handler exists.
            try:
                router.get_handler(operation.id)
            except MissingHandler as e:
                errors[operation].append(e)

            for param in operation.parameters:
                if param.location == 'header' and '_' in param.name:  # See https://github.com/akx/lepo/issues/23
                    ipd = InvalidParameterDefinition(
                        '{name}: Header parameter names may not contain underscores (Django bug 25048)'.format(
                            name=param.name,
                        )
                    )
                    errors[operation].append(ipd)

    if errors:
        raise RouterValidationError(errors)
