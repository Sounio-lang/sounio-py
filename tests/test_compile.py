"""Compilation bridge contract, using explicit compiler fixtures."""
import os
from pathlib import Path
from unittest.mock import patch

import pytest
from sounio._compile import compile, run


def compiler(tmp_path, body):
    path = tmp_path / 'compiler with spaces'
    path.write_text('#!/bin/sh\n' + body)
    path.chmod(0o755)
    return patch.dict(os.environ, {'SOUC': str(path)})


def test_compile_does_not_run_and_owned_output_is_cleaned(tmp_path):
    body = '''test "$1" = compile || exit 12
printf '#!/bin/sh\\nprintf "executed\\\\n"\\n' > "$4"
chmod +x "$4"
'''
    with compiler(tmp_path, body):
        with compile('fn main() -> i32 { 0 }') as module:
            binary = Path(module._binary_path)
            assert binary.exists()
            assert module.run().stdout == 'executed\n'
        assert not binary.exists()


def test_empty_success_does_not_reuse_old_output(tmp_path):
    output = tmp_path / 'existing'
    output.write_text('old output')
    with compiler(tmp_path, 'exit 0\n'):
        with pytest.raises(RuntimeError, match='without producing an executable'):
            compile('fn main() -> i32 { 0 }', output=output)
    assert output.read_text() == 'old output'


def test_failure_preserves_output_and_reports_diagnostic(tmp_path):
    output = tmp_path / 'existing'
    output.write_text('old output')
    with compiler(tmp_path, 'echo rejected >&2\nexit 7\n'):
        with pytest.raises(RuntimeError, match='rejected'):
            compile('fn main() -> i32 { 0 }', output=output)
    assert output.read_text() == 'old output'


def test_explicit_output_survives_close_and_run_reports_exit(tmp_path):
    body = '''printf '#!/bin/sh\\nexit 23\\n' > "$4"
chmod +x "$4"
'''
    output = tmp_path / 'program with spaces'
    with compiler(tmp_path, body):
        with compile('fn main() -> i32 { 23 }', output=output) as module:
            assert module.run().exit_code == 23
        assert output.exists()
        assert run('fn main() -> i32 { 23 }').exit_code == 23
