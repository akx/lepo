import pytest
from django.contrib.auth.models import AnonymousUser
from django.core.exceptions import PermissionDenied

from lepo.handlers import BaseHandler


class EvalHandler(BaseHandler):
    view_processors = ['ensure_superuser']  # all views will pass through this

    def handle_eval(self):
        return eval(self.args['expression'])

    def ensure_superuser(self, purpose, **kwargs):
        if not self.request.user.is_superuser:
            raise PermissionDenied('oh no')


def test_eval_handler(rf, admin_user):
    eval_fn = EvalHandler.get_view('handle_eval')
    request = rf.post('/')
    request.user = AnonymousUser()
    with pytest.raises(PermissionDenied):
        eval_fn(request, expression='6 + 6')
    request = rf.post('/')
    request.user = admin_user
    assert eval_fn(request, expression='6 + 6') == 12
