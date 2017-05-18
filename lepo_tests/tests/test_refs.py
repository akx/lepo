import json

import pytest

from lepo.api_info import APIInfo
from lepo.parameters import read_parameters
from lepo_tests.tests.utils import get_router

lil_bub = {'name': 'Lil Bub', 'petType': 'Cat', 'huntingSkill': 'lazy'}
hachiko = {'name': 'Hachiko', 'petType': 'Dog', 'packSize': 83}


def test_path_refs():
    router = get_router('path-refs.yaml')
    assert router.get_path('/b').mapping == router.get_path('/a').mapping


def test_schema_refs(rf):
    router = get_router('schema-refs.yaml')
    request = rf.post('/cat', json.dumps(lil_bub), content_type='application/json')
    request.api_info = APIInfo(router.get_path('/cat').get_operation('post'))
    params = read_parameters(request, {})
    assert params['cat'] == lil_bub


@pytest.mark.parametrize('object', (lil_bub, hachiko))
def test_polymorphism(rf, object):
    router = get_router('schema-refs.yaml')
    request = rf.post('/pet', json.dumps(object), content_type='application/json')
    request.api_info = APIInfo(router.get_path('/pet').get_operation('post'))
    params = read_parameters(request, {})
    assert params['pet'] == object
