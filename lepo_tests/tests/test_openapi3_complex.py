import json

import pytest
from django.utils.http import urlencode
from jsonschema import ValidationError

from lepo.apidef.doc import APIDefinition
from lepo.excs import ErroneousParameters, InvalidComplexContent
from lepo.parameter_utils import read_parameters
from lepo_tests.tests.utils import make_request_for_operation

doc = APIDefinition.from_yaml('''
openapi: 3.0.0
paths:
  /complex-parameter:
    get:
      parameters:
      - in: query
        name: coordinates
        required: true
        content:
          application/json:
            schema:
              type: object
              required:
                - lat
                - long
              properties:
                lat:
                  type: number
                long:
                  type: number
''')


def test_complex_parameter():
    coords_obj = {'lat': 8, 'long': 7}
    request = make_request_for_operation(
        doc.get_path('/complex-parameter').get_operation('get'),
        query_string=urlencode({
            'coordinates': json.dumps(coords_obj),
        }),
    )
    params = read_parameters(request)
    assert params == {'coordinates': coords_obj}


def test_complex_parameter_fails_validation():
    request = make_request_for_operation(
        doc.get_path('/complex-parameter').get_operation('get'),
        query_string=urlencode({
            'coordinates': json.dumps({'lat': 8, 'long': 'hoi there'}),
        }),
    )
    with pytest.raises(ErroneousParameters) as ei:
        read_parameters(request, capture_errors=True)
    assert isinstance(ei.value.errors['coordinates'], ValidationError)


def test_malformed_complex_parameter():
    request = make_request_for_operation(
        doc.get_path('/complex-parameter').get_operation('get'),
        query_string=urlencode({
            'coordinates': '{{{{{{{{{{{{{it\'s so cold and miserable',
        }),
    )
    with pytest.raises(ErroneousParameters) as ei:
        read_parameters(request, capture_errors=True)
    assert isinstance(ei.value.errors['coordinates'], InvalidComplexContent)
