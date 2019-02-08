import argparse
import sys

from lepo.apidef.doc import APIDefinition


def cmdline(args=None):  # pragma: no cover
    ap = argparse.ArgumentParser()
    ap.add_argument('input', default=None, nargs='?')
    ap.add_argument('--mode', '-m', required=True, choices=('handler', 'client'))
    args = ap.parse_args(args)
    if args.input:
        apidoc = APIDefinition.from_file(args.input)
    else:  # pragma: no cover
        apidoc = APIDefinition.from_yaml(sys.stdin)
    if args.mode == 'handler':
        from lepo.codegen.handler import generate_handler_stub
        from lepo.router import Router
        print(generate_handler_stub(Router(apidoc)))
    elif args.mode == 'client':
        from lepo.codegen.client import generate_client
        print(generate_client(apidoc))


if __name__ == '__main__':  # pragma: no cover
    cmdline()
