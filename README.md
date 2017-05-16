# Lepo – Contract-first REST APIs in Django

[![Build Status](https://travis-ci.org/akx/lepo.svg?branch=master)](https://travis-ci.org/akx/lepo) [![Codecov](https://img.shields.io/codecov/c/github/akx/lepo.svg)]()

Lepo is a *contract-first* API framework that enables you to design your API using the [OpenAPI specification](https://github.com/OAI/OpenAPI-Specification) (formerly known as Swagger) and implement it in Python 3 and [Django](https://www.djangoproject.com/).

What does it mean when we say *contract-first*? Contrast this to *code-first*:

* **Code-first**: First write the implementation of your API endpoints. Interactive API documentation is generated from docstrings and other meta-data embedded in the implementation. The [Django REST Framework](http://www.django-rest-framework.org/) is a popular example of a framework that promotes code-first style.
* **Contract-first** (or **API first**): Write the *contract* of your API first in machine-readable documentation describing the available endpoints and their input and output. API calls are mapped into view functions using meta-data embedded in this machine-readable documentation. Other examples of contract-first frameworks include [connexion](https://github.com/zalando/connexion) (using [Flask](https://github.com/pallets/flask)) and [Apigee 127](https://github.com/apigee-127/swagger-tools) (using Node.js and Express).

## Features

* Automatic routing of requests to endpoints
* Body and query parameter validation
* Output validation (soon!)
* Embedded Swagger UI

## Documentation

Please see the [docs](./docs) folder for more extensive documentation.

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
