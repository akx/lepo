from collections import namedtuple
from datetime import date, datetime

import pytest
from iso8601 import UTC

from lepo.apidef.doc import Swagger2APIDefinition
from lepo.parameter_utils import cast_primitive_value
from lepo_tests.tests.utils import cast_parameter_value, doc_versions, get_apidoc_from_version

DATA_EXAMPLES = [
    {'spec': {'type': 'integer'}, 'input': '5041211', 'output': 5041211},
    {'spec': {'format': 'long'}, 'input': '88888888888888888888888', 'output': 88888888888888888888888},
    {'spec': {'format': 'float'}, 'input': '-6.3', 'output': -6.3},
    {'spec': {'format': 'double'}, 'input': '-6.7', 'output': -6.7},
    {'spec': {'type': 'string'}, 'input': '', 'output': ''},
    {'spec': {'type': 'string'}, 'input': 'hee', 'output': 'hee'},
    {'spec': {'format': 'byte'}, 'input': 'c3VyZS4=', 'output': b'sure.'},
    {'spec': {'format': 'binary'}, 'input': 'v', 'output': b'v'},
    {'spec': {'type': 'boolean'}, 'input': 'true', 'output': True},
    {'spec': {'type': 'boolean'}, 'input': 'false', 'output': False},
    {'spec': {'format': 'date'}, 'input': '2016-03-06 15:33:33', 'output': date(2016, 3, 6)},
    {'spec': {'format': 'date'}, 'input': '2016-03-06', 'output': date(2016, 3, 6)},
    {
        'spec': {'format': 'dateTime'}, 'input': '2016-03-06 15:33:33',
        'output': datetime(2016, 3, 6, 15, 33, 33, tzinfo=UTC)
    },
    {'spec': {'format': 'password'}, 'input': 'ffffffffffff', 'output': 'ffffffffffff'},
]


@pytest.mark.parametrize('case', DATA_EXAMPLES)
def test_data(case):
    spec = case['spec']
    type = spec.get('type')
    format = spec.get('format')
    parsed = cast_primitive_value(type, format, case['input'])
    assert parsed == case['output']


Case = namedtuple('Case', 'swagger2_schema openapi3_schema input expected')

collection_format_cases = [
    Case(
        {'type': 'array', 'collectionFormat': 'tsv', 'items': {'type': 'boolean'}},
        None,  # TSV does not exist in OpenAPI 3
        'true\ttrue\tfalse',
        [True, True, False],
    ),
    Case(
        {'type': 'array', 'collectionFormat': 'ssv', 'items': {'type': 'string'}},
        None,
        'what it do',
        ['what', 'it', 'do'],
    ),
    Case(
        {
            'type': 'array',
            'collectionFormat': 'pipes',
            'items': {
                'type': 'array',
                'items': {
                    'type': 'integer',
                },
            }
        },
        None,
        '1,2,3|4,5,6|7,8,9',
        [[1, 2, 3], [4, 5, 6], [7, 8, 9]],
    ),
]


@doc_versions
@pytest.mark.parametrize('case', collection_format_cases)
def test_collection_formats(doc_version, case):
    schema = (case.swagger2_schema if doc_version == 'swagger2' else case.openapi3_schema)
    if schema is None:
        pytest.xfail('{}: no schema for {}'.format(case, doc_version))
    apidoc = get_apidoc_from_version(doc_version)
    assert cast_parameter_value(apidoc, schema, case.input) == case.expected
