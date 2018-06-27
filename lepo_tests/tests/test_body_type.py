import yaml

from lepo.api_info import APIInfo
from lepo.parameter_utils import read_parameters
from lepo.router import Router

JSONIFY_DOC = """
swagger: "2.0"
consumes:
  - text/plain
produces:
  - application/json
paths:
  /jsonify:
    post:
      parameters:
      - name: text
        in: body
        
"""


def test_text_body_type(rf):
    router = Router(yaml.safe_load(JSONIFY_DOC))
    operation = router.get_path('/jsonify').get_operation('post')
    request = rf.post('/jsonify', 'henlo worl', content_type='text/plain')
    request.api_info = APIInfo(operation=operation)
    params = read_parameters(request, {})
    assert params['text'] == 'henlo worl'
