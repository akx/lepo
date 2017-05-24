import json

import pytest
from django.utils.crypto import get_random_string

from lepo.excs import InvalidBodyFormat, InvalidBodyContent
from lepo_tests.models import Pet


def get_data_from_response(response, status=200):
    if status and response.status_code != status:
        raise ValueError('failed status check (%s != expected %s)' % (response.status_code, status))
    return json.loads(response.content.decode('utf-8'))


@pytest.mark.django_db
def test_get_empty_list(client):
    assert get_data_from_response(client.get('/api/pets')) == []


@pytest.mark.django_db
def test_optional_trailing_slash(client):
    assert get_data_from_response(client.get('/api/pets/')) == []

@pytest.mark.django_db
@pytest.mark.parametrize('with_tag', (False, True))
def test_post_pet(client, with_tag):
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
def test_search_by_tag(client):
    pet1 = Pet.objects.create(name='smolboye', tag='pupper')
    pet2 = Pet.objects.create(name='longboye', tag='doggo')
    assert len(get_data_from_response(client.get('/api/pets'))) == 2
    assert len(get_data_from_response(client.get('/api/pets', {'tags': 'pupper'}))) == 1
    assert len(get_data_from_response(client.get('/api/pets', {'tags': 'daggo'}))) == 0
    assert len(get_data_from_response(client.get('/api/pets', {'tags': 'doggo'}))) == 1
    assert len(get_data_from_response(client.get('/api/pets', {'tags': 'pupper,doggo'}))) == 2


@pytest.mark.django_db
def test_delete_pet(client):
    pet1 = Pet.objects.create(name='henlo')
    pet2 = Pet.objects.create(name='worl')
    assert len(get_data_from_response(client.get('/api/pets'))) == 2
    client.delete('/api/pets/{}'.format(pet1.id))
    assert len(get_data_from_response(client.get('/api/pets'))) == 1


@pytest.mark.django_db
def test_update_pet(client):
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
def test_invalid_operation(client):
    assert client.patch('/api/pets').status_code == 405


@pytest.mark.django_db
def test_invalid_body_format(client):
    with pytest.raises(InvalidBodyFormat):
        client.post(
            '/api/pets',
            b'<pet></pet>',
            content_type='application/xml'
        )


@pytest.mark.django_db
def test_invalid_body_content(client):
    with pytest.raises(InvalidBodyContent):
        client.post(
            '/api/pets',
            b'{',
            content_type='application/json'
        )
