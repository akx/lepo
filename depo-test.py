import pyaml

from lepo.depo import Depo

d = Depo()


@d.operation(method='GET', path='/pets')
def list_pets(request, filter: d.param(type=str, location='body')):
    """
    List pets, optionally filtering by name
    """
    pass


@d.operation(method='POST', path='/pets')
def add_pet(request, name: d.param(type=str, location='query')):
    """
    Add a pet by name
    """
    pass


openapi = d.to_openapi()
print(pyaml.dumps(openapi).decode('utf-8'))

"""
swagger: 2.0
info: {}
host: https://example.com
schemes:
  - http
consumes:
  - application/json
produces:
  - application/json
paths:
  /pets:
    get:
      description: 'List pets, optionally filtering by name'
      operationId: list_pets
      parameters:
        - name: filter
          in: body
          required: false
          type: str
    post:
      description: 'Add a pet by name'
      operationId: add_pet
      parameters:
        - name: name
          in: query
          required: false
          type: str
"""
