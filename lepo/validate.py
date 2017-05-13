def validate_router(router):
    operations = set()
    for path in router.api['paths'].values():
        for mapping in path.values():
            operations.add(mapping['operationId'])
    for operation in operations:
        try:
            router.get_handler(operation)
        except Exception as e:
            yield e
