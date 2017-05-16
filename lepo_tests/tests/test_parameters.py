import pytest
from jsonschema import ValidationError

from lepo.parameters import cast_parameter_value, read_parameters


def test_parameter_validation():
    with pytest.raises(ValidationError):
        cast_parameter_value(
            None,
            {
                'type': 'array',
                'collectionFormat': 'ssv',
                'items': {
                    'type': 'string',
                    'maxLength': 3,
                },
            },
            'what it do',
        )
