import json

import django.conf
import pytest
from django.utils.crypto import get_random_string

try:
    # Django 2
    from django.urls import clear_url_caches, set_urlconf
except:  # pragma: no cover
    # Django 1.11
    from django.core.urlresolvers import clear_url_caches, set_urlconf

from lepo.excs import InvalidBodyContent, InvalidBodyFormat
from lepo_tests.models import Pet
from lepo_tests.tests.utils import get_data_from_response
from lepo_tests.utils import urlconf_map

# There's some moderate Py.test and Python magic going on here.
# `urlconf_map` is a map of dynamically generated URLconf modules
# that don't actually exist on disk, and this fixture ensures all
# tests in this module which request the `api_urls` fixture (defined below)
# actually get parametrized to include all versions in the map.


def pytest_generate_tests(metafunc):
    if 'api_urls' in metafunc.fixturenames:
        module_names = [m.__name__ for m in urlconf_map.values()]
        metafunc.parametrize('api_urls', module_names, indirect=True)


@pytest.fixture
def api_urls(request):
    urls = request.param
    original_urlconf = django.conf.settings.ROOT_URLCONF
    django.conf.settings.ROOT_URLCONF = urls
    clear_url_caches()
    set_urlconf(None)

    def restore():
        django.conf.settings.ROOT_URLCONF = original_urlconf
        clear_url_caches()
        set_urlconf(None)

    request.addfinalizer(restore)


@pytest.mark.django_db
def test_get_empty_list(client, api_urls):
    assert get_data_from_response(client.get('/api/pets')) == []


@pytest.mark.django_db
def test_optional_trailing_slash(client, api_urls):
    assert get_data_from_response(client.get('/api/pets/')) == []


@pytest.mark.django_db
@pytest.mark.parametrize('with_tag', (False, True))
def test_post_pet(client, api_urls, with_tag):
    payload = {
        'name': get_random_string(),
    }
    if with_tag:
        payload['tag'] = get_random_string()

    pet = get_data_from_response(
        client.post(
            '/api/pets',
            json.dumps(payload),
            content_type='application/json'
        )
    )
    assert pet['name'] == payload['name']
    assert pet['id']
    if with_tag:
        assert pet['tag'] == payload['tag']

    # Test we can get the pet from the API now
    assert get_data_from_response(client.get('/api/pets')) == [pet]
    assert get_data_from_response(client.get('/api/pets/{}'.format(pet['id']))) == pet


@pytest.mark.django_db
def test_search_by_tag(client, api_urls):
    pet1 = Pet.objects.create(name='smolboye', tag='pupper')
    pet2 = Pet.objects.create(name='longboye', tag='doggo')
    assert len(get_data_from_response(client.get('/api/pets'))) == 2
    assert len(get_data_from_response(client.get('/api/pets', {'tags': 'pupper'}))) == 1
    assert len(get_data_from_response(client.get('/api/pets', {'tags': 'daggo'}))) == 0
    assert len(get_data_from_response(client.get('/api/pets', {'tags': 'doggo'}))) == 1
    assert len(get_data_from_response(client.get('/api/pets', {'tags': 'pupper,doggo'}))) == 2


@pytest.mark.django_db
def test_delete_pet(client, api_urls):
    pet1 = Pet.objects.create(name='henlo')
    pet2 = Pet.objects.create(name='worl')
    assert len(get_data_from_response(client.get('/api/pets'))) == 2
    client.delete('/api/pets/{}'.format(pet1.id))
    assert len(get_data_from_response(client.get('/api/pets'))) == 1


@pytest.mark.django_db
def test_update_pet(client, api_urls):
    pet1 = Pet.objects.create(name='henlo')
    payload = {'name': 'worl', 'tag': 'bunner'}
    resp = client.patch(
        '/api/pets/{}'.format(pet1.id),
        json.dumps(payload),
        content_type='application/json'
    )
    assert resp.status_code == 200

    pet_data = get_data_from_response(client.get('/api/pets'))[0]
    assert pet_data['name'] == 'worl'
    assert pet_data['tag'] == 'bunner'


@pytest.mark.django_db
def test_invalid_operation(client, api_urls):
    assert client.patch('/api/pets').status_code == 405


@pytest.mark.django_db
def test_invalid_body_format(client, api_urls):
    with pytest.raises(InvalidBodyFormat):
        client.post(
            '/api/pets',
            b'<pet></pet>',
            content_type='application/xml'
        )


@pytest.mark.django_db
def test_invalid_body_content(client, api_urls):
    with pytest.raises(InvalidBodyContent):
        client.post(
            '/api/pets',
            b'{',
            content_type='application/json'
        )
