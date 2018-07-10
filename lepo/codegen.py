import argparse
import sys

from django.utils.text import camel_case_to_spaces
from six import StringIO

from lepo.apidef.doc import APIDefinition
from lepo.router import Router

HANDLER_TEMPLATE = '''
def {func_name}(request, {parameters}):
    raise NotImplementedError('Handler {operation_id} not implemented')
'''.strip()


def generate_handler_stub(router, handler_template=HANDLER_TEMPLATE):
    output = StringIO()
    func_name_to_operation = {}
    for path in router.get_paths():
        for operation in path.get_operations():
            snake_operation_id = camel_case_to_spaces(operation.id).replace(' ', '_')
            func_name_to_operation[snake_operation_id] = operation
    for func_name, operation in sorted(func_name_to_operation.items()):
        parameter_names = [p.name for p in operation.parameters]
        handler = handler_template.format(
            func_name=func_name,
            operation_id=operation.id,
            parameters=', '.join(parameter_names),
        )
        output.write(handler)
        output.write('\n\n\n')
    return output.getvalue()


def cmdline(args=None):  # pragma: no cover
    ap = argparse.ArgumentParser()
    ap.add_argument('input', default=None, nargs='?')
    args = ap.parse_args(args)
    if args.input:
        apidoc = APIDefinition.from_file(args.input)
    else:  # pragma: no cover
        apidoc = APIDefinition.from_yaml(sys.stdin)
    print(generate_handler_stub(Router(apidoc)))


if __name__ == '__main__':  # pragma: no cover
    cmdline()
