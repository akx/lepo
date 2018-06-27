import pytest

from lepo.excs import RouterValidationError, InvalidParameterDefinition
from lepo.validate import validate_router
from lepo_tests.tests.utils import get_router, doc_versions


@doc_versions
def test_validator(doc_version):
    router = get_router('{}/schema-refs.yaml'.format(doc_version))
    with pytest.raises(RouterValidationError) as ei:
        validate_router(router)
    assert len(ei.value.errors) == 2


@doc_versions
def test_header_underscore(doc_version):
    router = get_router('{}/header-underscore.yaml'.format(doc_version))
    with pytest.raises(RouterValidationError) as ei:
        validate_router(router)
    errors = list(ei.value.flat_errors)
    assert any(isinstance(e[1], InvalidParameterDefinition) for e in errors)
