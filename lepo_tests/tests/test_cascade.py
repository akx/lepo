import yaml

from lepo.router import Router

CASCADE_DOC = """
swagger: "2.0"
consumes:
  - application/json
produces:
  - application/x-happiness
paths:
  /cows:
    consumes:
    - application/x-grass
    produces:
    - application/x-moo
    post:
      operationId: tip
    delete:
      operationId: remoove
      produces:
      - application/x-no-more-moo
  /hello:
    get:
      operationId: greet
"""


def test_cascade():
    router = Router(yaml.safe_load(CASCADE_DOC))
    tip_operation = router.get_path('/cows').get_operation('post')
    assert tip_operation.consumes == ['application/x-grass']
    assert tip_operation.produces == ['application/x-moo']
    remooval_operation = router.get_path('/cows').get_operation('delete')
    assert remooval_operation.consumes == ['application/x-grass']
    assert remooval_operation.produces == ['application/x-no-more-moo']
    greet_operation = router.get_path('/hello').get_operation('get')
    assert greet_operation.consumes == ['application/json']
    assert greet_operation.produces == ['application/x-happiness']
