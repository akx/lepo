# Lepo – Contract-first REST APIs in Django

[![Build Status](https://travis-ci.org/akx/lepo.svg?branch=master)](https://travis-ci.org/akx/lepo) [![Codecov](https://img.shields.io/codecov/c/github/akx/lepo.svg)]()

Lepo is a *contract-first* API framework that enables you to design your API using the OpenAPI specification (formerly known as Swagger) and implement it in Python 3 and Django.

What does it mean when we say *contract-first*? Contrast this to *code-first*:

* **Code-first**: First write the implementation of your API endpoints. Interactive API documentation is generated from docstrings and other meta-data embedded in the implementation. The [Django REST Framework](http://www.django-rest-framework.org/) is a popular example of a framework that promotes code-first style.
* **Contract-first** (or **API first**): Write the *contract* of your API first in machine-readable documentation describing the available endpoints and their input and output. API calls are mapped into view functions using meta-data embedded in this machine-readable documentation. Other examples of contract-first frameworks include [connexion](https://github.com/zalando/connexion) (using [Flask](https://github.com/pallets/flask)) and [Apigee 127](https://github.com/apigee-127/swagger-tools) (using Node.js and Express).

### Features

* Automatic routing of requests to endpoints
* Body and query parameter validation
* Output validation
* Embedded Swagger UI

## Usage

Write the contract of the first version of your API in the [OpenAPI]() format (formerly know as Swagger). You'll end up with a YAML file popularly called `swagger.yml`.

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
import json
from pkg_resources import resource_string

from django.conf.urls import include, url
from django.contrib import admin

from lepo.router import Router
from lepo.validate import validate_router
from lepo_doc.urls import get_docs_urls

from . import views


router = Router(json.loads(resource_string(__name__, 'swagger.yml')))
router.add_handlers(views)

for error in validate_router(router):
    print('Validation error:', error)

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

### Class based views

Lepo provides a base class for class based views that validate their input and output against the schema. More documentation on this is TBD.

## Why is it called *lepo*?

*Lepo* is Finnish for *rest*.

## License

    The MIT License (MIT)

    Copyright (c) 2017 Aarni Koskela, Santtu Pajukanta

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all
    copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
    SOFTWARE.
