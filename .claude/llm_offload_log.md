# Review log

## 2026-09-19 — Python API reconciliation

Target: `knowledge.py`, `_knowledge.py`, `_epistemic.py`, `provenance.py`.
Task: math-review. Source imported from Sounio commit a7f298652ca3 (unchanged ecosystem source from its base), then reconciled in this branch.

Providers and actual outcomes:
- Local fan-out: no usable responses; providers unavailable.
- Remote xai / grok-4.5: completed review, identified defects.
- Remote zai / glm-5.2: ERROR, no review.
- Fallback deepseek / deepseek-v4-pro: ERROR, no review.

The main repository's `.claude/AGENT_OFFLOAD_POLICY.md` failure-mode rule allows progress after failed alternate providers are documented. This is not a second-provider approval. Re-review with an available independent provider remains outstanding before declaring scientific/backend parity. This draft consolidation makes no such declaration.

Finding disposition:
- Corrected zero-nominal multiplication in legacy Knowledge and zero-numerator division in both Python implementations using absolute first-order sensitivities. Added positive/negative denominator regression cases.
- Corrected inaccurate dose/volume example and removed the incorrect section-13 reference.
- Kept the two APIs distinct: public legacy Knowledge/PureKnowledge versus EpistemicKnowledge. Their confidence, provenance, constructors, and equality semantics are not interchangeable.
- Legacy confidence is documented as a precision heuristic; uncertain zero has infinite relative uncertainty and zero heuristic confidence. Negative epsilon is rejected.
- Correlation finding qualified: EpistemicResult is a metadata container, not an input accepted by GUMPropagation. Correlation metadata now survives serialization; the calculator explicitly documents independent inputs only. No correlated-propagation support is claimed.
- Scalar operations preserve legacy provenance ancestry. Unknown DAG parent IDs now raise instead of being silently filtered.
- Remaining legacy limitations: compound units are not propagated by the epistemic API; reverse scalar arithmetic methods are not added to that API; expanded_uncertainty remains a default-coverage property. These are not advertised as parity with the native backend.

Validation before this log: 76 tests passed, 2 live compiler checks skipped, 3 subtests passed. An additional missing-parent regression is included in this commit and is run before commit.
