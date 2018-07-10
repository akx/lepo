SWAGGER_2 = 'swagger2'
OPENAPI_3 = 'openapi3'


def split_version(version):
    # Not perfectly Semver safe.
    return [int(bit) for bit in str(version).split('.')]


def parse_version(doc_dict):
    if 'swagger' in doc_dict:
        version = split_version(doc_dict['swagger'])
        if version[0] != 2:  # pragma: no cover
            raise ValueError('Only Swagger 2.x is supported')
        return SWAGGER_2
    elif 'openapi' in doc_dict:
        version = split_version(doc_dict['openapi'])
        if version[0] != 3:  # pragma: no cover
            raise ValueError('Only OpenAPI 3.x is supported')
        return OPENAPI_3
    raise ValueError('API document is missing version specifier')
