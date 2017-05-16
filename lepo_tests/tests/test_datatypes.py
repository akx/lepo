from datetime import date, datetime

import pytest
from iso8601 import UTC

from lepo.parameters import cast_value

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
    parsed = cast_value(case['spec'], case['input'])
    assert parsed == case['output']
