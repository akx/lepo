import pytest
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import UploadedFile
from jsonschema import ValidationError

from lepo.api_info import APIInfo
from lepo.excs import ErroneousParameters, MissingParameter
from lepo.parameter_utils import cast_parameter_value, read_parameters
from lepo_tests.tests.utils import DOC_VERSIONS, get_router

routers = pytest.mark.parametrize('router', [
    get_router('{}/parameter-test.yaml'.format(doc_version))
    for doc_version
    in DOC_VERSIONS
])


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


@routers
def test_files(rf, router):
    request = rf.post('/upload', {
        'file': ContentFile(b'foo', name='foo.txt'),
    })
    request.api_info = APIInfo(router.get_path('/upload').get_operation('post'))
    parameters = read_parameters(request, {})
    assert isinstance(parameters['file'], UploadedFile)


@routers
def test_multi(rf, router):
    request = rf.get('/multiple-tags?tag=a&tag=b&tag=c')
    request.api_info = APIInfo(router.get_path('/multiple-tags').get_operation('get'))
    parameters = read_parameters(request, {})
    assert parameters['tag'] == ['a', 'b', 'c']


@routers
def test_default(rf, router):
    request = rf.get('/greet?greetee=doggo')
    request.api_info = APIInfo(router.get_path('/greet').get_operation('get'))
    parameters = read_parameters(request, {})
    assert parameters == {'greeting': 'henlo', 'greetee': 'doggo'}


@routers
def test_required(rf, router):
    request = rf.get('/greet')
    request.api_info = APIInfo(router.get_path('/greet').get_operation('get'))
    with pytest.raises(ErroneousParameters) as ei:
        read_parameters(request, {})
    assert isinstance(ei.value.errors['greetee'], MissingParameter)


@routers
def test_invalid_collection_format(rf, router):
    request = rf.get('/invalid-collection-format?blep=foo')
    request.api_info = APIInfo(router.get_path('/invalid-collection-format').get_operation('get'))
    with pytest.raises(NotImplementedError):
        read_parameters(request, {})


@routers
def test_type_casting_errors(rf, router):
    request = rf.get('/add-numbers?a=foo&b=8')
    request.api_info = APIInfo(router.get_path('/add-numbers').get_operation('get'))
    with pytest.raises(ErroneousParameters) as ei:
        read_parameters(request, {})
    assert 'a' in ei.value.errors
    assert 'b' in ei.value.parameters


@routers
def test_header_parameter(rf, router):
    # Too bad there isn't a "requests"-like interface for testing that didn't
    # work by creating a `WSGIRequest` environment... Would be more truthful to test with something like that.
    request = rf.get('/header-parameter?blep=foo', HTTP_TOKEN='foo')
    request.api_info = APIInfo(router.get_path('/header-parameter').get_operation('get'))
    assert read_parameters(request, {})['token'] == 'foo'


@routers
def test_parameter_cascade(rf, router):
    request = rf.get('/cascade-parameters?a=7&b=10')
    request.api_info = APIInfo(router.get_path('/cascade-parameters').get_operation('get'))
    assert read_parameters(request, {}) == {'a': 7, 'b': 10}
    request = rf.get('/cascade-parameter-override?a=yylmao')
    request.api_info = APIInfo(router.get_path('/cascade-parameter-override').get_operation('get'))
    assert read_parameters(request, {}) == {'a': 'yylmao'}  # this would fail in the typecast if override didn't work


@routers
def test_parameter_ref(rf, router):
    request = rf.get('/parameter-reference?age=86')
    request.api_info = APIInfo(router.get_path('/parameter-reference').get_operation('get'))
    assert read_parameters(request, {}) == {'age': 86}


@routers
def test_parameters_ref(rf, router):
    # /parameters-reference refers the entire parameters object from parameter-reference, so the test is equivalent
    request = rf.get('/parameters-reference?age=86')
    request.api_info = APIInfo(router.get_path('/parameters-reference').get_operation('get'))
    assert read_parameters(request, {}) == {'age': 86}
