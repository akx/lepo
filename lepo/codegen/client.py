from ast import Expression
from pprint import pformat

from lepo.apidef.doc import APIDefinition
from lepo.apidef.operation.base import Operation
from lepo.apidef.parameter.base import BaseTopParameter
from lepo.apidef.parameter.openapi import OpenAPI3BodyParameter
from lepo.apidef.parameter.swagger import Swagger2Parameter
from lepo.codegen.pyw import Pyw


class ClientGenerator(Pyw):
    def __init__(self):
        super().__init__()

    def emit_apidoc(self, apidoc):
        self.write_block('import requests\n')
        with self.scope('class ClientOptions:'):
            self.write_block('''
            raw = False
            raise_errors = False
            ''')
        with self.scope('class Client:'):
            self.write_block('''
                base_url = ''
                
                _session = None
                _options = ClientOptions()

                @property
                def session(self):
                    if not self._session:
                        self._session = requests.Session()
                    return self._session
                    
                def _get_option(self, override, name, default=None):
                    if hasattr(override, name):
                        return getattr(override, name)
                    return getattr(self._options, name, default)
                
                ''')
            for path in apidoc.get_paths():
                for op in sorted(path.get_operations(), key=lambda op: op.id):
                    self.emit_op(op)

    def emit_op(self, op: Operation):
        op_func = op.id.replace(' ', '_')
        sig_parameters = []
        path_parameters = set()
        param: BaseTopParameter
        body_parameter = None
        query_parameters = set()
        for param in op.parameters:
            py_param = ['%s' % param.name]
            if not param.required:
                py_param.append('=None')
            sig_parameters.append(''.join(py_param))
            if param.location == 'path':
                path_parameters.add(param)
            elif param.in_body:
                body_parameter = param
            elif param.location == 'query':
                query_parameters.add(param)
            else:
                print(param)
                raise NotImplementedError('...')

        sig_parameters.append('_options=None')

        with self.kwfunc(op_func, sig_parameters):
            description = op.data.get('description')
            if description:
                self.write_line('"""%s"""' % description.strip())
            if path_parameters:
                url = '%r.format(%s)' % (op.path.path, ', '.join('%s=%s' % (p.name, p.name) for p in path_parameters))
            else:
                url = repr(op.path.path)
            headers = {}
            request_kwargs = {
                'method': op.method,
                'url': Expression(url),
            }
            if body_parameter:
                body_type = None
                if isinstance(body_parameter, OpenAPI3BodyParameter):
                    if body_parameter.media_map.match('application/json'):
                        body_type = 'json'
                    else:
                        if not body_parameter.media_map.match('multipart/form-data'):
                            # TODO: may be incorrect
                            headers['Content-Type'] = next(body_parameter.media_map)
                elif isinstance(body_parameter, Swagger2Parameter):
                    if op.consumes == 'application/json':
                        body_type = 'json'
                request_kwargs[('json' if body_type == 'json' else 'data')] = Expression(body_parameter.name)

            if query_parameters:
                self.write_line('params = {}')
                for param in query_parameters:
                    with self.scope('if %s is not None:' % (param.name)):
                        self.write_line('params[%r] = %s' % (param.name, param.name))
                request_kwargs['params'] = Expression('params')
            if headers:
                request_kwargs['headers'] = headers

            self.write_func_call(
                retval='resp',
                func='self.session.request',
                kwargs=request_kwargs,
            )
            with self.scope('if self._get_option(_options, \'raw\', False):'):
                self.write_line('return resp')
            with self.scope('if self._get_option(_options, \'raise_errors\', False):'):
                self.write_line('resp.raise_for_status()')

            if op.responses:
                for code, response in sorted(op.responses.items()):
                    if code.isdigit():
                        prelude = 'if resp.status_code == %s:' % code
                    elif code == 'default':
                        prelude = 'else:'
                    else:
                        raise NotImplementedError('...')
                    with self.scope(prelude, pad=False):
                        description = response.get('description')
                        if description:
                            self.write_comment(description)
                        content_types = response.get('content', {})
                        if 'application/json' in content_types:
                            self.write_line('return resp.json()' % response)
                        else:
                            if content_types:
                                self.write_comment(pformat(content_types), pad=False)
                            self.write_line('return resp')
            else:
                self.write_line('# No responses specified in definition')
                self.write_line('return resp')


def generate_client(apidoc: APIDefinition):
    cg = ClientGenerator()
    cg.emit_apidoc(apidoc)
    return cg.io.getvalue()
