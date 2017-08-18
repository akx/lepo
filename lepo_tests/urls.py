import os

from django.conf.urls import include, url
from django.contrib import admin

from lepo.decorators import csrf_exempt
from lepo.router import Router
from lepo.validate import validate_router
from lepo_doc.urls import get_docs_urls

router = Router.from_file(os.path.join(os.path.dirname(__file__), 'tests', 'petstore-expanded.yaml'))
router.add_handlers('lepo_tests.handlers.pets')
validate_router(router)
router_urls = router.get_urls(
    decorate=(csrf_exempt,),
    optional_trailing_slash=True,
)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router_urls, 'api')),
    url(r'^api/', include(get_docs_urls(router, 'api-docs'), 'api-docs')),
]
