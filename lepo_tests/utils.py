import os
import sys
import types

from django.urls import include, re_path
from django.contrib import admin

from lepo.decorators import csrf_exempt
from lepo.router import Router
from lepo.validate import validate_router
from lepo_doc.urls import get_docs_urls
from lepo_tests.tests.utils import DOC_VERSIONS


def get_urlpatterns(handler_module, definition_file='swagger2/petstore-expanded.yaml'):
    # NB: This could just as well be your `urls.py` – it's here to make testing various handler
    #     configurations easier.

    router = Router.from_file(os.path.join(os.path.dirname(__file__), 'tests', definition_file))
    router.add_handlers(handler_module)
    validate_router(router)
    router_urls = router.get_urls(
        decorate=(csrf_exempt,),
        optional_trailing_slash=True,
        root_view_name='api_root',
    )

    urlpatterns = [
        re_path(r'^admin/', admin.site.urls),
        re_path(r'^api/', include((router_urls, 'api'), 'api')),
        re_path(r'^api/', include((get_docs_urls(router, 'api-docs'), 'api-docs'), 'api-docs')),
    ]
    return urlpatterns


URLCONF_TEMPLATE = '''
from lepo_tests.handlers import %(module)s
from lepo_tests.utils import get_urlpatterns
urlpatterns = get_urlpatterns(%(module)s, %(file)r)
'''


def generate_urlconf_module(handler_style, version):
    modname = 'lepo_tests.generated_urls_{handler_style}_{version}'.format(
        handler_style=handler_style,
        version=version,
    )
    mod = types.ModuleType(modname)
    code = URLCONF_TEMPLATE % {
        'module': handler_style,
        'file': '%s/petstore-expanded.yaml' % version,
    }
    exec(code, mod.__dict__)
    sys.modules[modname] = mod
    return mod


def generate_urlconf_modules(handler_styles, versions):
    urlconf_modules = {}
    for handler_style in handler_styles:
        for version in versions:
            mod = generate_urlconf_module(handler_style, version)
            urlconf_modules[(handler_style, version)] = mod
    return urlconf_modules


urlconf_map = generate_urlconf_modules(
    handler_styles=('pets_cb', 'pets_bare'),
    versions=DOC_VERSIONS,
)
