import os
from unittest.mock import patch
from sounio_kernel.executor import CellExecutor


def test_installed_launcher_compile_contract(tmp_path):
    launcher = tmp_path / 'souc'
    launcher.write_text('#!/bin/sh\nprintf "%s\\n" "$1" "$2" "$3" "$4" "${SOUNIO_STDLIB_PATH-unset}"\n')
    launcher.chmod(0o755)
    with patch.dict(os.environ, {'PATH': str(tmp_path)}, clear=True):
        executor = CellExecutor()
        try:
            stdout, stderr, code = executor._raw_compile('source.sio', 'program')
            assert code == 0, stderr
            assert stdout == 'compile\nsource.sio\n-o\nprogram\nunset\n'
            assert executor.souc_binary == str(launcher)
        finally:
            executor.cleanup()
