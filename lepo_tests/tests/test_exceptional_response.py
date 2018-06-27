from django.http.response import HttpResponse

from lepo.excs import ExceptionalResponse
from lepo_tests.tests.utils import get_router, doc_versions


def greet(request, greeting, greetee):
    raise ExceptionalResponse(HttpResponse('oh no', status=400))


@doc_versions
def test_exceptional_response(rf, doc_version):
    router = get_router('{}/parameter-test.yaml'.format(doc_version))
    router.add_handlers({'greet': greet})
    path_view = router.get_path('/greet').view_class.as_view()
    response = path_view(rf.get('/', {'greeting': 'hello', 'greetee': 'world'}))
    assert response.content == b'oh no'
