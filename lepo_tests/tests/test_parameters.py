import pytest
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from jsonschema import ValidationError

from lepo.api_info import APIInfo
from lepo.parameters import cast_parameter_value, read_parameters
from lepo.router import Router
from lepo_tests.tests.consts import PARAMETER_TEST_YAML_PATH


def test_parameter_validation():
    with pytest.raises(ValidationError):
        cast_parameter_value(
            None,
            {
                'type': 'array',
                'collectionFormat': 'ssv',
                'items': {
                    'type': 'string',
                    'maxLength': 3,
                },
            },
            'what it do',
        )


router = Router.from_file(PARAMETER_TEST_YAML_PATH)


def test_files(rf):
    request = rf.post('/upload', {
        'file': ContentFile(b'foo', name='foo.txt'),
    })
    request.api_info = APIInfo(router.get_path('/upload').get_operation('post'))
    parameters = read_parameters(request, {})
    assert isinstance(parameters['file'], UploadedFile)


def test_multi(rf):
    request = rf.get('/multiple-tags?tag=a&tag=b&tag=c')
    request.api_info = APIInfo(router.get_path('/multiple-tags').get_operation('get'))
    parameters = read_parameters(request, {})
    assert parameters['tag'] == ['a', 'b', 'c']


def test_default(rf):
    request = rf.get('/greet?greetee=doggo')
    request.api_info = APIInfo(router.get_path('/greet').get_operation('get'))
    parameters = read_parameters(request, {})
    assert parameters == {'greeting': 'henlo', 'greetee': 'doggo'}
