import json
import os

import pytest

from lepo.router import Router

TESTS_DIR = os.path.dirname(__file__)


def get_router(fixture_name):
    return Router.from_file(os.path.join(TESTS_DIR, fixture_name))


def get_data_from_response(response, status=200):
    if status and response.status_code != status:
        raise ValueError('failed status check (%s != expected %s)' % (response.status_code, status))  # pragma: no cover
    return json.loads(response.content.decode('utf-8'))


DOC_VERSIONS = ['swagger2']
doc_versions = pytest.mark.parametrize('doc_version', DOC_VERSIONS)
