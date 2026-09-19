# sounio — Python Interface for Epistemic Programming

Python interface for the [Sounio programming language](https://github.com/Sounio-lang/sounio), enabling epistemic computing with uncertainty propagation in Python workflows.

## Install

```bash
pip install sounio
```

## Quick Start

```python
from sounio import Knowledge, SounioExecutor

# Epistemic values with uncertainty
mass = Knowledge(75.0, 0.5, provenance="scale")
height = Knowledge(1.80, 0.01, provenance="stadiometer")

# Run Sounio code
executor = SounioExecutor()
result = executor.run_code("""
    let dose: mg = 500.0
    let volume: mL = 250.0
    let concentration = dose / volume
    print(concentration)
""")

# Drug discovery pipeline
from sounio.pipeline import DrugDiscoveryPipeline
pipeline = DrugDiscoveryPipeline()
result = pipeline.run_full()
print(f"Screened: {result.molecules_screened}, Passed: {result.molecules_passed}")

# Generate report
from sounio.report import ReportBuilder
rb = ReportBuilder("PK Analysis")
rb.add_section("Results", f"Concentration: {result.summary}")
print(rb.to_markdown())
```

## Features

- **Knowledge[T]** — Values with uncertainty and provenance
- **SounioExecutor** — Run .sio files from Python
- **DrugDiscoveryPipeline** — End-to-end drug discovery
- **ReportBuilder** — Generate Markdown/LaTeX reports
- **Integrations** — NumPy, pandas, matplotlib, RDKit, PubChem, clinical data

## Requirements

- Python 3.8+
- Sounio compiler (`souc`) — see [installation guide](https://github.com/Sounio-lang/sounio)

## License

Apache-2.0

### Installed compiler discovery

Install a versioned Madaros distribution and add its `bin` directory to `PATH`.
`SounioExecutor` uses an explicit `souc_path` first, then `SOUC`,
`SOUNIO_SOUC_PATH`, `SOUC_BIN`, and finally `souc` on `PATH`. An invalid explicit
selection fails instead of silently running another compiler. Paths containing
spaces are supported. Select the distribution's `bin/souc` launcher rather than
its raw ELF so compiler routing remains owned by the distribution.

Without an explicit `stdlib_path` or `SOUNIO_STDLIB_PATH`, the launcher selects
its bundled, matching standard library. Python does not infer a standard library
from the current working directory.

The discovery contract is tested with:

```sh
python -m unittest discover -s tests -p test_distribution_resolution.py -v
```

These tests use fixture launchers and validate subprocess routing only; actual
compiler execution is a separate integration check.

### Knowledge API compatibility during consolidation

The existing `Knowledge` / `PureKnowledge` API uses `epsilon` and a textual
`provenance`. The imported uncertainty/confidence API is exposed separately as
`EpistemicKnowledge`, with `measure`, `confidence_gate`, `EpistemicResult`, and
`GUMPropagation`. These APIs have distinct constructors and semantics; they are
not interchangeable. The pure-Python legacy type also supports the transported
`ProvenanceChain` and `ProvenanceNode` tracking API. Native backend reconciliation
is still in progress and parity is not implied by these exports.

### Optional native extension

The pure-Python installation does not require Rust. To build the optional
extension from this repository, install `./native` in the same Python environment:

```sh
python -m pip install .
python -m pip install ./native
```

Use `from sounio import native` to select it explicitly. Installing the extension
never changes `sounio.Knowledge`: the native constructor uses `uncertainty`,
`confidence`, `unit`, and `prov`, while the legacy constructor uses `epsilon`
and textual `provenance`. Their full behavior is not interchangeable.

The native numeric operations use independent-input, first-order propagation.
They do not implement covariance or dimensional algebra: unit strings are
annotations, addition/subtraction retain the left annotation, and
multiplication/division clear it. Check unit compatibility before arithmetic.
`abs` preserves the uncertainty annotation; it does not compute the moments of
a folded distribution near zero. These inherited behaviors are not claims of
full GUM coverage or native/Python equivalence.
