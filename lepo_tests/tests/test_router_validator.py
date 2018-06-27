import pytest

from lepo.excs import RouterValidationError, InvalidParameterDefinition
from lepo.validate import validate_router
from lepo_tests.tests.utils import get_router


def test_validator():
    router = get_router('swagger2/schema-refs.yaml')
    with pytest.raises(RouterValidationError) as ei:
        validate_router(router)
    assert len(ei.value.errors) == 2


def test_header_underscore():
    router = get_router('swagger2/header-underscore.yaml')
    with pytest.raises(RouterValidationError) as ei:
        validate_router(router)
    errors = list(ei.value.flat_errors)
    assert any(isinstance(e[1], InvalidParameterDefinition) for e in errors)
