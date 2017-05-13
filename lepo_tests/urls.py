import os

from django.conf.urls import include, url
from django.contrib import admin

from lepo.router import Router
from lepo.validate import validate_router

router = Router.from_file(os.path.join(os.path.dirname(__file__), '..', 'tests', 'petstore-expanded.yaml'))
router.add_handlers('lepo_tests.handlers.pets')

for error in validate_router(router):
    print('Validation error:', error)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.get_urls(), 'api')),
]
