# Getting started

Write the contract of the first version of your API in the [OpenAPI format](https://github.com/OAI/OpenAPI-Specification). You'll end up with a YAML file popularly called `swagger.yml`.

```yaml
swagger: "2.0"
info:
  version: 0.0.1
  title: Lepo Petstore
  description: A sample API that uses a petstore as an example to …
host: localhost:8000
basePath: /api
schemes:
  - http
consumes:
  - application/json
produces:
  - application/json
paths:
  /pets:
    get:
      description: |
        Returns all pets from the system that the user has access to
      operationId: findPets
      responses:
        200:
          description: Great success.
```

Note the `operationId` field. It's converted from camel case to snake case (`findPets` becomes `find_pets`) and used to route an API call to the correct handler (or *view* in Django lingo).

Add `lepo` to your `INSTALLED_APPS`. If you want to use the Swagger UI, also add `lepo_docs`.

```python
INSTALLED_APPS = [
    # …
    'lepo',
    'lepo_doc',
]
```

Make a Django app, say `petstore`, add it to `INSTALLED_APPS`, and hook the `swagger.yml` up to your application in `urls.py`:

```python
from pkg_resources import resource_filename

from django.conf.urls import include, url
from django.contrib import admin

from lepo.router import Router
from lepo.validate import validate_router
from lepo_doc.urls import get_docs_urls

from . import views


router = Router.from_file(resource_filename(__name__, 'swagger.yml'))
router.add_handlers(views)
validate_router(router)

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^api/', include(router.get_urls(), 'api')),
    url(r'^api/', include(get_docs_urls(router, 'api-docs'), 'api-docs')),
]
```

Observe it is your responsibility to mount the API at the correct base path. Lepo does not read `basePath` from your `swagger.yml`.

Finally, implement the operations in `petstore/views.py`:

```python
from django.http import JSONResponse

def find_pets(request):
    return JSONResponse({'pets': []})
```
