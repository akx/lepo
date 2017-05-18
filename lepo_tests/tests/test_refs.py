import json

from lepo.api_info import APIInfo
from lepo.parameters import read_parameters
from lepo_tests.tests.utils import get_router


def test_path_refs():
    router = get_router('path-refs.yaml')
    assert router.get_path('/b').mapping == router.get_path('/a').mapping


def test_schema_refs(rf):
    router = get_router('schema-refs.yaml')
    lil_bub = {'name': 'Lil Bub', 'petType': 'Cat', 'huntingSkill': 'lazy'}
    request = rf.post('/cat', json.dumps(lil_bub), content_type='application/json')
    request.api_info = APIInfo(router.get_path('/cat').get_operation('post'))
    params = read_parameters(request, {})
    assert params['cat'] == lil_bub
