from lepo.apidef.doc import APIDefinition
from lepo.parameter_utils import read_parameters
from lepo_tests.tests.utils import make_request_for_operation

doc = APIDefinition.from_yaml('''
openapi: 3.0.0
servers: []
paths:
  /single/{thing}/data{format}:
    get:
      parameters:
        - name: format
          in: path
          style: label
          schema:
            type: string
        - name: thing
          in: path
          schema:
            type: string
  /array/{thing}/data{format}:
    get:
      parameters:
        - name: format
          in: path
          style: label
          explode: true
          schema:
            type: array
            items:
              type: string
        - name: thing
          in: path
          schema:
            type: string
  /object/{thing}/data{format}:
    get:
      parameters:
        - name: format
          in: path
          style: label
          explode: false
          schema:
            type: object
            items:
              type: string
        - name: thing
          in: path
          schema:
            type: string
''')


def test_label_parameter():
    request = make_request_for_operation(doc.get_path('/single/{thing}/data{format}').get_operation('get'))
    params = read_parameters(request, {
        'thing': 'blorp',
        'format': '.json',
    })
    assert params == {
        'thing': 'blorp',
        'format': 'json',  # Notice the missing dot
    }


def test_label_array_parameter():
    request = make_request_for_operation(doc.get_path('/array/{thing}/data{format}').get_operation('get'))
    params = read_parameters(request, {
        'thing': 'blorp',
        'format': '.json.yaml.xml.pdf',
    })
    assert params == {
        'thing': 'blorp',
        'format': ['json', 'yaml', 'xml', 'pdf'],  # An eldritch monstrosity
    }


def test_label_object_parameter():
    request = make_request_for_operation(doc.get_path('/object/{thing}/data{format}').get_operation('get'))
    params = read_parameters(request, {
        'thing': 'blorp',
        'format': '.some,body,once,told',
    })
    assert params == {
        'thing': 'blorp',
        'format': {'some': 'body', 'once': 'told'},
    }
