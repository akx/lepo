from lepo_tests.tests.utils import get_router


def test_path_refs():
    router = get_router('path-refs.yaml')
    assert router.get_path('/b').mapping == router.get_path('/a').mapping
