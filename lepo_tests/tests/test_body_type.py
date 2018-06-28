import yaml

from lepo.api_info import APIInfo
from lepo.apidef.doc import APIDefinition
from lepo.parameter_utils import read_parameters

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


# TODO: add OpenAPI 3 version of this test
def test_text_body_type(rf):
    apidoc = APIDefinition.from_data(yaml.safe_load(JSONIFY_DOC))
    operation = apidoc.get_path('/jsonify').get_operation('post')
    request = rf.post('/jsonify', 'henlo worl', content_type='text/plain')
    request.api_info = APIInfo(operation=operation)
    params = read_parameters(request, {})
    assert params['text'] == 'henlo worl'
