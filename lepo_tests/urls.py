import os

from django.conf.urls import include, url
from django.contrib import admin

from lepo.router import Router
from lepo.validate import validate_router
from lepo_doc.urls import get_docs_urls

router = Router.from_file(os.path.join(os.path.dirname(__file__), 'tests', 'petstore-expanded.yaml'))
router.add_handlers('lepo_tests.handlers.pets')
validate_router(router)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.get_urls(), 'api')),
    url(r'^api/', include(get_docs_urls(router, 'api-docs'), 'api-docs')),
]
