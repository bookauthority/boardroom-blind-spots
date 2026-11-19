# Chapter 9 Experiment: Operational Resilience for AI

Experiment ID: `exp-09-operational-resilience-ai-ewd-response`

This self-contained project implements a minimal, offline-friendly simulation of
baseline vs. AI-aware operational resilience for an AI-driven credit approval
process. It focuses on determinism and reproducibility over realism.

Key elements:
- Synthetic credit-like data and a deterministic linear "model".
- Baseline variant: generic monitoring (only approval rate metric).
- Treatment variant: AI-specific meta-monitoring (approval rate + drift metric).
- Two workloads (to keep runtime bounded in this sandbox):
  - `WL1_normal_operations`
  - `WL3_abrupt_model_corruption`
- Evidence written to `/evidence/results.json` following the required schema.
- Tests validating evidence structure and basic invariants.

## Quick start

```bash
python run.py
python -m unittest discover -s tests -p "test_*.py"
```

If the environment variable `BOOKMAS_EVIDENCE_DIR` is set, evidence will be
written to `$BOOKMAS_EVIDENCE_DIR/results.json`. Otherwise it will fall back to
`/evidence/results.json`.

## Design overview

### Model

We simulate a credit approval model as a simple linear score over three
features:

- `income` (scaled)
- `debt_to_income`
- `credit_utilization`

The "champion" model and a degraded/corrupted model are both deterministic and
implemented with fixed coefficient vectors. A logistic transform converts the
linear score to an approval probability; approval is granted if
`p_approve >= 0.5`.

### Workloads

Only a subset of the long-form specification is implemented to keep runtime
bounded in this sandbox, while still exercising the contrast between baseline
and treatment.

#### WL1_normal_operations

- Generate synthetic applications from a fixed distribution.
- Score with the champion model.
- Baseline and treatment see identical data (shared RNG seed per workload
  and variant tag).
- Monitoring metrics:
  - Baseline: approval rate.
  - Treatment: approval rate and a simple input drift magnitude between first
    and second half of the batch (as a proxy for AI-specific metrics).
- This workload primarily demonstrates that treatment can run without spurious
  divergence in metrics structure.

#### WL3_abrupt_model_corruption

- Half of the applications are scored with the champion model, then abruptly
  switch to a corrupted model for the second half (simulating T0 corruption).
- The underlying data distribution stays the same.
- Monitoring/"detection" behavior (implemented in-code, no external systems):
  - Baseline: continues to compute approval rate; no AI-specific detection.
  - Treatment: computes a simple disagreement metric between champion and
    corrupted outputs on the second half. This metric is used to emulate
    early detection capability in treatment.

The implementation does *not* attempt to simulate true wall-clock time,
incident workflows, or real alert routing. All metrics are computed within a
single process run, and only numeric metrics that are actually computed in this
sandbox are recorded.

### Evidence schema (runtime contract)

`run.py` writes JSON with this shape to `/evidence/results.json`:

```json
{
  "chapter": 9,
  "experiment_id": "exp-09-operational-resilience-ai-ewd-response",
  "environment": {"os": "...", "python": "..."},
  "runs": [
    {
      "variant": "baseline" | "treatment",
      "workload_id": "WL1_normal_operations" | "WL3_abrupt_model_corruption",
      "run_id": "...",  # unique per workload+variant
      "success": true,
      "metrics": {
        "approval_rate": 0.73,
        "drift_magnitude": 0.02,        # treatment-only for WL1
        "post_corruption_approval_rate": 0.60,  # WL3
        "disagreement_rate": 0.40               # treatment-only WL3
      }
    }
  ],
  "notes": "Free-form string with contextual information."
}
```

- Every metric value is a JSON number (no strings, booleans, lists, objects, or
  nulls inside `metrics`).
- At least one baseline and one treatment run are produced for each workload.
- Metrics reflect actual computations performed in this code; no invented
  runtimes or external error rates are logged.

### Determinism and fairness

- Only the Python standard library is used.
- A fixed random seed is used per workload, and both variants share derived
  seeds so that they see identical synthetic data (fair comparison).
- The corrupted model is defined analytically, not via random training, to keep
  behavior predictable between runs.

## Project layout

- `run.py` – entry point; runs workloads and writes evidence.
- `experiment/__init__.py` – package marker.
- `experiment/model.py` – simple deterministic model and corruption logic.
- `experiment/workloads.py` – synthetic data generation and workload runners.
- `experiment/metrics.py` – utility functions to compute numeric metrics.
- `tests/test_experiment.py` – unit tests validating schema and basic behavior.
- `requirements.txt` – intentionally empty of external runtime deps.

## Extending this experiment

If you wish to extend this skeleton toward the full specification:

- Add additional workloads (WL2, WL4) in `experiment/workloads.py` using
  similar patterns.
- Implement more sophisticated monitoring/alert logic (e.g., PSI, champion
  vs. shadow metrics) in a separate module, but remember that only standard
  library is allowed in this context.
- Expand `metrics` emitted per run, as long as they remain numeric and are
  actually computed.

Be sure to keep runtime bounded and tests fast, as this project is meant to
run in restricted automated environments.
