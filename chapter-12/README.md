# Experiment 12 – Model Validation Reimagined (Offline Demo)

This project implements a **fully self-contained, offline** Python 3.11+ experiment aligned with:

- Chapter: **12 – Model Validation Reimagined: Independent Challenge for Autonomous AI**
- Experiment ID: **exp-12-model-validation-reimagined-v1**

It demonstrates, in miniature, the difference between a **traditional model-centric validation** (baseline) and a **reimagined, pipeline-centric, adversarial and fairness-aware validation harness** (treatment) for a credit decision workflow.

The implementation is intentionally lightweight and restricted:

- **No third-party libraries** are used (standard library only).
- **Synthetic data** is generated deterministically at runtime (no external datasets).
- **No network, subprocess, or shell access** is used.
- Evidence is written as JSON to an **/evidence/results.json** file (or a directory path specified by the `BOOKMAS_EVIDENCE_DIR` environment variable).

The structure is designed so that institutions can later swap in their own data and models while keeping the harness pattern.

---

## Contents

- `run.py` – Orchestrates baseline and treatment runs for two workloads and writes evidence JSON.
- `experiment/core.py` – Core synthetic data generation, baseline model, and treatment pipeline.
- `experiment/metrics.py` – Metric implementations (AUC, accuracy, simple PSI, volatility, fairness proxies, etc.).
- `experiment/baseline_runner.py` – Traditional validation workflow.
- `experiment/treatment_runner.py` – Enhanced validation harness (probing, adversarial-style tests, fairness/robustness checks).
- `tests/test_experiment.py` – Unit tests and schema checks for `results.json`.
- `requirements.txt` – Empty of runtime deps (comment-only), per constraints.

---

## Conceptual Mapping

Although simplified for an offline sandbox, the code aligns to the specification as follows:

- **Workloads**
  - `WL1-tabular-credit-scoring-pipeline`  
    Represented by a synthetic tabular credit dataset with protected attribute `group` (A/B).  
    We generate different **scenarios** via deterministic perturbations: normal vs stressed features.
  - `WL2-llm-assistant-subcomponent-optional`  
    Represented by a simulated LLM explanation component (no real LLM). Treatment adds a simple rule-based safety checker and tracks a numeric `llm_policy_violation_rate` proxy.

- **Baseline vs Treatment**
  - Baseline:
    - Trains a simple logistic-style linear classifier (implemented from scratch) on synthetic credit data.
    - Computes **AUC ROC** and **accuracy** on a hold-out test split.
    - Computes a minimal **population stability index** (PSI) per feature under a stress scenario.
  - Treatment:
    - Uses the **same core model class** but wraps it in an end-to-end pipeline:
      normalization, scoring, decision threshold, and simple rules.
    - Adds:
      - Probing for **decision volatility** under small perturbations.
      - Simple monotonicity checks to estimate a **monotonicity_violation_rate**.
      - A simplistic adversarial search to find inputs with unexpected approvals to estimate **adversarial_vulnerability_rate**.
      - Group-based approval rate comparisons to estimate fairness metrics
        (`fairness_dp_difference`, `disparate_impact_ratio`).
      - For WL2, a simulated LLM with naive content and a rule-based checker to yield an approximate **llm_policy_violation_rate**.

The implementation does **not** attempt to be production-grade risk tooling, but it demonstrates how a more sophisticated validation harness yields additional metrics and potential issues compared to a minimal baseline.

---

## How to Run

### 1. Run Tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

This validates that:

- The experiment runs end-to-end.
- Evidence JSON at `/evidence/results.json` (or the configured directory) conforms to the exact schema required by the runtime contract.

### 2. Run the Experiment

Set the evidence directory (must be writable):

```bash
export BOOKMAS_EVIDENCE_DIR=/evidence  # or another directory
python run.py
```

After the run, inspect the evidence file:

```bash
cat $BOOKMAS_EVIDENCE_DIR/results.json
```

The file will look like:

```json
{
  "chapter": 12,
  "experiment_id": "exp-12-model-validation-reimagined-v1",
  "environment": {
    "os": "posix",
    "python": "3.11.0"
  },
  "runs": [
    {
      "variant": "baseline",
      "workload_id": "WL1-tabular-credit-scoring-pipeline",
      "run_id": "baseline-WL1",
      "success": true,
      "metrics": {
        "auc_roc": 0.79,
        "accuracy": 0.73,
        "psi_mean": 0.04
      }
    },
    {
      "variant": "treatment",
      "workload_id": "WL1-tabular-credit-scoring-pipeline",
      "run_id": "treatment-WL1",
      "success": true,
      "metrics": {
        "auc_roc": 0.79,
        "accuracy": 0.73,
        "psi_mean": 0.04,
        "decision_volatility_rate": 0.12,
        "monotonicity_violation_rate": 0.03,
        "adversarial_vulnerability_rate": 0.15,
        "fairness_dp_difference": 0.05,
        "disparate_impact_ratio": 0.82
      }
    },
    ...
  ],
  "notes": "..."
}
```

(Exact values will be deterministic but may differ from this example.)

### 3. Extending the Harness

To adapt this harness to real-world use:

- Replace the synthetic data generator (`SyntheticCreditDataGenerator`) with a loader for governed internal datasets.
- Swap the simple linear model with your actual credit risk model, preserving identical configurations between baseline and treatment.
- Enrich `treatment_runner.py` with institution-specific probes, stress scenarios, fairness definitions, and—for LLMs—your real red-teaming prompts and guardrails.

---

## Design Notes

- **Determinism & Reproducibility**: All random draws use fixed seeds to ensure stable results across runs.
- **Fair Comparison Controls**: Baseline and treatment share the same data splits and model class; differences arise from additional tests/metrics.
- **Evidence Schema**: `results.json` is the only required evidence artifact; it contains all numeric metrics under the `metrics` objects, suitable for automated ingestion and comparison.

For more detail, inspect the docstrings in the `experiment/` modules.
