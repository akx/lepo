import pytest

from lepo_tests.utils import urlconf_map


# TODO: test OpenAPI 3 too
@pytest.mark.urls(urlconf_map[('pets_cb', 'swagger2')].__name__)
def test_docs(client):
    assert '/api/swagger.json' in client.get('/api/docs/').content.decode('utf-8')
    assert client.get('/api/swagger.json').content.startswith(b'{')
