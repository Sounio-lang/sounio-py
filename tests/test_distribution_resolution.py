"""CLI discovery contract; fake launchers test plumbing, not compiler semantics."""
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from sounio._executor import SounioExecutor


class DistributionResolutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="python consumer ")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.launcher = self.root / "souc"
        self.launcher.write_text(
            '#!/bin/sh\nprintf "%s\\n" "$1" "${SOUNIO_STDLIB_PATH-unset}"\n'
        )
        self.launcher.chmod(0o755)
        self.env = patch.dict(os.environ, {"PATH": str(self.root)}, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_path_launcher_keeps_bundled_stdlib_default(self):
        result = SounioExecutor().run_code("fn main() -> i32 { 0 }")
        self.assertEqual(result.exit_code, 0)
        self.assertEqual(result.stdout, "run\nunset\n")

    def test_explicit_path_and_stdlib_survive_spaces(self):
        library = self.root / "custom library"
        library.mkdir()
        executor = SounioExecutor(str(self.launcher), str(library))
        self.assertEqual(executor.run_code("unused").stdout, f"run\n{library}\n")

    def test_environment_precedence(self):
        for variable in ("SOUC", "SOUNIO_SOUC_PATH", "SOUC_BIN"):
            with self.subTest(variable=variable), patch.dict(os.environ, {variable: str(self.launcher)}):
                self.assertEqual(SounioExecutor().souc_path, str(self.launcher))
        with patch.dict(os.environ, {"SOUC": str(self.launcher), "SOUC_BIN": "/missing"}):
            self.assertEqual(SounioExecutor().souc_path, str(self.launcher))

    def test_invalid_override_does_not_fall_back_to_path(self):
        with patch.dict(os.environ, {"SOUC": str(self.root / "missing")}):
            with self.assertRaises(FileNotFoundError):
                SounioExecutor().run_code("unused")

    def test_missing_installation_reports_actionable_error(self):
        with patch.dict(os.environ, {"PATH": ""}):
            with self.assertRaisesRegex(FileNotFoundError, "Install the Madaros distribution"):
                SounioExecutor()

    def test_check_uses_selected_launcher(self):
        self.assertTrue(SounioExecutor().check_file("unused.sio").success)


if __name__ == "__main__":
    unittest.main()
