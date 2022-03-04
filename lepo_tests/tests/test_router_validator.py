import pytest

from lepo.excs import InvalidParameterDefinition, RouterValidationError
from lepo.validate import validate_router
from lepo_tests.tests.utils import doc_versions, get_router


@doc_versions
def test_validator(doc_version):
    router = get_router(f'{doc_version}/schema-refs.yaml')
    with pytest.raises(RouterValidationError) as ei:
        validate_router(router)
    assert len(ei.value.errors) == 2


@doc_versions
def test_header_underscore(doc_version):
    router = get_router(f'{doc_version}/header-underscore.yaml')
    with pytest.raises(RouterValidationError) as ei:
        validate_router(router)
    errors = list(ei.value.flat_errors)
    assert any(isinstance(e[1], InvalidParameterDefinition) for e in errors)
