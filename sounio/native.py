"""Explicit optional native API; not an interchangeable legacy Knowledge backend."""
try:
    from _sounio_native import (
        Knowledge, measure, confidence_gate, GUMPropagation,
        EpistemicResult, SensitivityCoefficient,
    )
except ImportError as exc:
    raise ImportError(
        "The optional sounio-native extension is not installed. "
        "Build/install the native project from this repository."
    ) from exc

__all__ = [
    "Knowledge", "measure", "confidence_gate", "GUMPropagation",
    "EpistemicResult", "SensitivityCoefficient",
]
