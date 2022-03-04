from django.http.response import HttpResponse

from lepo.excs import ExceptionalResponse
from lepo_tests.tests.utils import doc_versions, get_router


def greet(request, greeting, greetee):
    raise ExceptionalResponse(HttpResponse('oh no', status=400))


@doc_versions
def test_exceptional_response(rf, doc_version):
    router = get_router(f'{doc_version}/parameter-test.yaml')
    router.add_handlers({'greet': greet})
    path_view = router.get_path_view_class('/greet').as_view()
    response = path_view(rf.get('/', {'greeting': 'hello', 'greetee': 'world'}))
    assert response.content == b'oh no'
