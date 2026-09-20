"""Compile and execute Sounio source through the installed compiler CLI."""

from __future__ import annotations

import os
import subprocess
import tempfile
from pathlib import Path
from typing import Optional, Union

from ._executor import SounioExecutor


def _find_souc() -> str:
    """Use the same installed compiler selection as SounioExecutor."""
    return SounioExecutor._resolve_souc()


class CompiledModule:
    """
    A compiled Sounio module runnable from Python.

    Created by sounio.compile(). Provides a .run() method to execute
    the compiled binary and capture output.
    """

    def __init__(self, source_path: str, binary_path: Optional[str] = None):
        self._source_path = source_path
        self._binary_path = binary_path
        self._compiled = binary_path is not None

    def close(self) -> None:
        """Release owned temporary files; explicitly requested output is retained."""
        workspace = getattr(self, "_workspace", None)
        if workspace is not None:
            workspace.cleanup()
            self._workspace = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()

    def run(self, *args: str, capture: bool = True) -> "RunResult":
        """
        Execute the compiled module.

        Args:
            *args: command-line arguments to pass to the binary
            capture: if True, capture stdout/stderr

        Returns:
            RunResult with stdout, stderr, and exit_code
        """
        if not self._compiled or self._binary_path is None:
            raise RuntimeError(
                "Module is not compiled. Use sounio.compile() to compile first."
            )
        cmd = [self._binary_path] + list(args)
        result = subprocess.run(
            cmd,
            capture_output=capture,
            text=True,
        )
        return RunResult(
            stdout=result.stdout,
            stderr=result.stderr,
            exit_code=result.returncode,
        )

    def __repr__(self) -> str:
        status = "compiled" if self._compiled else "stub"
        return f"CompiledModule(source={self._source_path!r}, status={status})"


class RunResult:
    """Result of running a Sounio binary."""

    def __init__(self, stdout: str, stderr: str, exit_code: int):
        self.stdout = stdout
        self.stderr = stderr
        self.exit_code = exit_code
        self.ok = exit_code == 0

    def __repr__(self) -> str:
        return f"RunResult(exit_code={self.exit_code}, ok={self.ok})"


def compile(
    source: Union[str, Path],
    output: Optional[Union[str, Path]] = None,
    optimize: bool = False,
) -> CompiledModule:
    """
    Compile a Sounio source file to a native binary.

    Args:
        source:   path to .sio file or inline Sounio code string
        output:   path for compiled binary (defaults to temp file)
        optimize: enable compiler optimizations

    Returns:
        CompiledModule that can be .run()

    Example::

        model = sounio.compile("models/pbpk_epistemic.sio")
        result = model.run()
        print(result.stdout)
    """
    executor = SounioExecutor()
    workspace = tempfile.TemporaryDirectory(prefix="sounio-compile-")
    root = Path(workspace.name)
    try:
        text = str(source)
        is_inline = isinstance(source, str) and ("\n" in text or text.lstrip().startswith("fn "))
        if is_inline:
            source_path = root / "source.sio"
            source_path.write_text(text)
        else:
            source_path = Path(source).expanduser().absolute()
            if not source_path.is_file():
                raise FileNotFoundError(source_path)
        binary = root / "program"
        cmd = [executor.souc_path, "compile", str(source_path), "-o", str(binary)]
        if optimize:
            cmd.append("-O")
        result = subprocess.run(cmd, capture_output=True, text=True, env=executor._build_env())
        if result.returncode != 0:
            raise RuntimeError(f"Compilation failed ({result.returncode}):\n{result.stderr}\n{result.stdout}")
        if not binary.is_file() or not os.access(binary, os.X_OK) or binary.stat().st_size == 0:
            raise RuntimeError("Compiler returned success without producing an executable")
        if output is not None:
            import shutil
            destination = Path(output).expanduser().absolute()
            # Stage beside the destination so the final replacement is atomic.
            with tempfile.NamedTemporaryFile(dir=destination.parent, delete=False) as staged:
                staged_path = Path(staged.name)
            try:
                shutil.copy2(binary, staged_path)
                os.replace(staged_path, destination)
            finally:
                staged_path.unlink(missing_ok=True)
            binary = destination
        module = CompiledModule(str(source_path), str(binary))
        module._workspace = workspace
        return module
    except BaseException:
        workspace.cleanup()
        raise


def run(
    source: Union[str, Path],
    *args: str,
    optimize: bool = False,
    capture: bool = True,
) -> RunResult:
    """
    Compile and immediately run a Sounio source file.

    Convenience wrapper around compile() + CompiledModule.run().

    Example::

        result = sounio.run("models/pbpk.sio")
        print(result.stdout)
    """
    module = compile(source, optimize=optimize)
    try:
        return module.run(*args, capture=capture)
    finally:
        module.close()
