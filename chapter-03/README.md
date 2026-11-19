# Chapter 3 Experiment: Failure Modes of Autonomous AI in Finance

This is a **self-contained, offline Python 3.11+ project** that demonstrates small, deterministic simulations for the Chapter 3 taxonomy:

> **Failure Modes of Autonomous AI in Finance**

It is designed to run in a restricted sandbox without any third-party libraries. All numerical results are generated at runtime by `run.py`.

## Contents

- `run.py` – main entry point; runs a minimal baseline and treatment for each workload and writes `results.json` into the directory specified by `BOOKMAS_EVIDENCE_DIR` (or `/evidence` by default).
- `experiments/` – simple, synthetic models and workloads for each failure mode.
- `tests/test_experiment.py` – schema tests for `results.json`.
- `requirements.txt` – intentionally empty of runtime dependencies; **standard library only**.

The workloads correspond to the specification:

1. `wl-3.2-drift-credit-risk` – credit default classifier under drift.
2. `wl-3.3-rl-credit-limits` – misaligned optimization in a simple RL-like setting.
3. `wl-3.4-feedback-loop-trading` – reflexivity and feedback loops in a toy market.
4. `wl-3.5-adversarial-fraud-and-llm` – adversarial manipulation in a fraud classifier.
5. `wl-3.6-fairness-credit-approvals` – bias and fairness breakdowns.
6. `wl-3.7-emergent-llm-agent-behaviour` – emergent behaviours in a toy "LLM" agent.
7. `wl-3.8-multi-stage-failure-cascade` – cascades in a small risk pipeline.

Each workload has:

- A **baseline** variant designed to behave reasonably.
- A **treatment** variant designed to exhibit a specific failure mode.

`run.py` executes both variants for each workload and records simple numeric metrics.

## Environment assumptions

- Python **3.11+**.
- No external network or system access.
- Writable `/tmp`, `/tmp/work`, and `/evidence` directories.

## Installation

Even though this project does not need third-party packages, a `requirements.txt` file is provided to satisfy tooling. It is effectively empty of real dependencies.

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Running the experiment

From the project root:

```bash
export BOOKMAS_EVIDENCE_DIR=/evidence  # or another writable directory
python run.py
```

This will:

1. Execute a **baseline** and **treatment** run for each workload.
2. Collect numeric metrics from each run.
3. Write an evidence file at:

```text
$BOOKMAS_EVIDENCE_DIR/results.json
```

with this exact structure:

```json
{
  "chapter": 3,
  "experiment_id": "ch3-failure-modes-of-autonomous-ai-in-finance",
  "environment": {"os": "...", "python": "..."},
  "runs": [
    {
      "variant": "baseline" | "treatment",
      "workload_id": "...",   
      "run_id": "...",        
      "success": true | false,
      "metrics": {"some_metric": 1.23}
    }
  ],
  "notes": "...optional text..."
}
```

- **Metrics values** are always JSON numbers.
- Additional non-metric information appears outside `metrics`.

At least one baseline and one treatment run are produced for every workload.

## Running tests

Tests validate the evidence schema only and use the Python standard library.

From the project root:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

The tests will:

- Ensure `/evidence/results.json` exists.
- Validate that it conforms to the contract above.
- Check that each workload has both baseline and treatment runs, with numeric metrics.

## Design notes

- All simulations are **tiny** and **deterministic** (fixed seeds) for reproducibility and bounded runtime.
- No external libraries are used; implementations rely on plain Python and minimal numerical logic.
- Metrics are intentionally simplified proxies of the more sophisticated KPIs in the chapter specification, but the **direction and nature** of failure modes are preserved:
  - Drift and regime shifts degrade classification accuracy.
  - Misaligned optimization improves the reward but harms true profit.
  - Feedback loops increase volatility and destabilize forecasts.
  - Adversarial manipulation worsens fraud metrics.
  - Fairness breakdowns increase disparity metrics.
  - Emergent behavior appears as new "off-policy" actions.
  - Cascades aggregate small model errors into larger capital misestimation.

This project is **educational only** and does **not** represent production-grade financial risk models.
