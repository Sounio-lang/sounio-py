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
