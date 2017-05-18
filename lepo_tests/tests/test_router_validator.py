import pytest

from lepo.excs import RouterValidationError
from lepo.validate import validate_router
from lepo_tests.tests.utils import get_router


def test_validator():
    router = get_router('schema-refs.yaml')
    with pytest.raises(RouterValidationError) as ei:
        validate_router(router)
    assert len(ei.value.errors) == 2
