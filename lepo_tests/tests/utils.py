import json
import os

import pytest
from django.test import RequestFactory

from lepo.api_info import APIInfo
from lepo.apidef.doc import OpenAPI3APIDefinition, Swagger2APIDefinition
from lepo.router import Router

TESTS_DIR = os.path.dirname(__file__)


def get_router(fixture_name):
    return Router.from_file(os.path.join(TESTS_DIR, fixture_name))


def get_data_from_response(response, status=200):
    if status and response.status_code != status:
        raise ValueError(f'failed status check ({response.status_code} != expected {status})')  # pragma: no cover
    return json.loads(response.content.decode('utf-8'))


DOC_VERSIONS = ['swagger2', 'openapi3']
doc_versions = pytest.mark.parametrize('doc_version', DOC_VERSIONS)


def cast_parameter_value(apidoc, parameter, value):
    if isinstance(parameter, dict):
        parameter_class = apidoc.operation_class.parameter_class
        parameter = parameter_class(parameter)
    return parameter.cast(apidoc, value)


def get_apidoc_from_version(version, content={}):
    if version == 'swagger2':
        return Swagger2APIDefinition(content)
    elif version == 'openapi3':
        return OpenAPI3APIDefinition(content)
    else:  # pragma: no cover
        raise NotImplementedError('...')


def make_request_for_operation(operation, method='GET', query_string=''):
    request = RequestFactory().generic(method=method, path=operation.path.path, QUERY_STRING=query_string)
    request.api_info = APIInfo(operation)
    return request
