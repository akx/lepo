import os

from lepo_tests.tests.utils import doc_versions
from lepo import codegen


@doc_versions
def test_handler_codegen(doc_version, capsys):
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), doc_version, 'petstore-expanded.yaml'))
    codegen.cmdline(['--mode=handler', path])
    out, err = capsys.readouterr()
    # Compile to test for syntax errors
    compile(out, '{}-generated.py'.format(doc_version), 'exec')
