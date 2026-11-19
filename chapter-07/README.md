# Chapter 7 Experiment: AI Scenario Analysis and Stress Testing

This project implements a minimal, self-contained Python 3.11+ experiment for:

- **Chapter**: 7
- **Title**: Scenario Analysis and Stress Testing for AI Model Collapse
- **Experiment ID**: `ch7-scenario-ai-model-collapse-stresstest-v1`

The goal is to demonstrate an AI-augmented stress testing framework with:

- A **baseline** engine (macro-only, no explicit AI failures).
- A **treatment** engine (macro + explicit AI failure scenarios at micro, firm-wide, and systemic levels).

It produces a single evidence file at `/evidence/results.json` (path given by `BOOKMAS_EVIDENCE_DIR` env var) following the specified runtime contract.

## Contents

- `run.py` – main entry point; runs baseline and treatment variants for all workloads and writes the evidence JSON.
- `experiment/__init__.py` – package marker.
- `experiment/model.py` – core data structures, synthetic portfolios, and loss models.
- `experiment/scenarios.py` – baseline macro scenarios and AI scenario definitions.
- `experiment/engine.py` – baseline vs treatment run logic and workload orchestration.
- `tests/test_experiment.py` – unit tests verifying the evidence schema and basic model behaviour.
- `requirements.txt` – intentionally empty of runtime dependencies; standard library only.

## Design Overview

This implementation is **pedagogical** and safe for offline execution. It is not a production risk engine.

### Baseline vs Treatment

- **Baseline**:
  - Uses only a simple macro stress index to adjust probabilities of default (PD) and market P&L.
  - No explicit AI state or failure modes.
  - Losses: credit, market, operational (basic proxy), and conduct (assumed zero here).

- **Treatment**:
  - Adds AI state variables and specific AI scenario templates (micro, firm-wide, systemic).
  - AI shocks change PD multipliers, booking volumes, fraud/operational losses, and trading P&L volatility.
  - Produces **incremental AI-attributed loss** on top of the macro baseline.

Both engines share the same macro-driven core models to ensure comparability.

### Workloads Implemented

The code encodes five workloads, each run once under baseline and once under treatment:

1. `W1_micro_level_ai_failure_scenarios`
2. `W2_firm_wide_common_cause_ai_failure_scenarios`
3. `W3_systemic_ai_feedback_loop_scenarios`
4. `W4_reverse_stress_testing_from_ai_perspective`
5. `W5_tabletop_exercise_and_communication_outputs`

Each workload returns at least one **numeric metric** for both baseline and treatment. Metrics are intentionally simplified:

- `total_loss` – aggregated over the scenario horizon.
- `ai_attributed_loss` – only in treatment (0 for baseline).
- `min_capital_ratio` – minimal capital ratio over the horizon using a toy capital model.

Additional metrics from the chapter specification (e.g., liquidity ratios, distance_to_breach) are conceptually represented in the internal logic, but only a subset is exported as numeric metrics to guarantee correctness within this offline, bounded setting.

### Evidence Schema Contract

`run.py` writes JSON to `/evidence/results.json`:

```json
{
  "chapter": 7,
  "experiment_id": "ch7-scenario-ai-model-collapse-stresstest-v1",
  "environment": {"os": "...", "python": "..."},
  "runs": [
    {
      "variant": "baseline",
      "workload_id": "W1_micro_level_ai_failure_scenarios",
      "run_id": "...",
      "success": true,
      "metrics": {"total_loss": 123.4, "min_capital_ratio": 0.11, "ai_attributed_loss": 0.0}
    },
    {
      "variant": "treatment",
      "workload_id": "W1_micro_level_ai_failure_scenarios",
      "run_id": "...",
      "success": true,
      "metrics": {"total_loss": 150.0, "min_capital_ratio": 0.10, "ai_attributed_loss": 26.6}
    },
    ...
  ],
  "notes": "..."
}
```

Notes:

- Every `metrics` value is a **number** (no strings, nulls, dicts, or lists).
- At least one baseline and one treatment record exist for **each** workload.
- Extra explanatory text or derived artifacts are placed in `notes` (a string) rather than inside `metrics`.

### Determinism and Safety

- All synthetic data are generated deterministically using fixed seeds.
- No external I/O is performed except writing `/evidence/results.json`.
- No non-standard libraries, networking, or subprocesses are used.

## How to Run

1. Ensure you are in the project root where `run.py` is located.
2. Make sure the evidence directory exists (the harness usually creates `/evidence`). If running manually you can do:

   ```bash
   mkdir -p /evidence
   ```

3. Run the experiment:

   ```bash
   python run.py
   ```

   This will execute all workloads under baseline and treatment and write `/evidence/results.json`.

4. Run tests:

   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```

## Interpreting Results

- Compare `total_loss` and `min_capital_ratio` between baseline and treatment per workload to see the incremental effect of explicit AI scenarios.
- `ai_attributed_loss` in the treatment runs shows how much additional loss is due to AI failures in this simplified framework.

This experiment is meant to be a transparent, reproducible scaffold that teams can extend with richer models, data, and reporting suitable for real enterprise stress testing.
