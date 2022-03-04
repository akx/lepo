import os

from lepo import codegen
from lepo_tests.tests.utils import doc_versions


@doc_versions
def test_codegen(doc_version, capsys):
    path = os.path.realpath(os.path.join(os.path.dirname(__file__), doc_version, 'petstore-expanded.yaml'))
    codegen.cmdline([path])
    out, err = capsys.readouterr()
    # Compile to test for syntax errors
    compile(out, f'{doc_version}-generated.py', 'exec')
