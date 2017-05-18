import os

from lepo.router import Router

TESTS_DIR = os.path.dirname(__file__)


def get_router(fixture_name):
    return Router.from_file(os.path.join(TESTS_DIR, fixture_name))
