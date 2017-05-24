from django.http.response import HttpResponse

from lepo.excs import ExceptionalResponse
from lepo_tests.tests.utils import get_router


def greet(request, greeting, greetee):
    raise ExceptionalResponse(HttpResponse('oh no', status=400))


def test_exceptional_response(rf):
    router = get_router('parameter-test.yaml')
    router.add_handlers({'greet': greet})
    path_view = router.get_path('/greet').view_class.as_view()
    response = path_view(rf.get('/', {'greeting': 'hello', 'greetee': 'world'}))
    assert response.content == b'oh no'
