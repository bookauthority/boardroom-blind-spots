# Chapter 8 Guardrails Experiment

This is a self-contained Python 3.11+ experiment project for:

- **Chapter**: 8
- **Title**: Designing Guardrails: Controls for Training, Deployment, and Autonomy
- **Experiment ID**: `exp-8-guardrails-controls-training-deployment-autonomy`

The goal is to compare a **baseline** AI service (minimal controls) against a **treatment** service (guardrails across the lifecycle) using synthetic workloads. The project is intentionally lightweight and CPU-bounded so it can run in an offline sandbox.

## What this project demonstrates

Within the constraints of a small offline environment, this project:

- Implements a toy **AI model service** (simple scoring function) and **action engine**.
- Provides **baseline** and **treatment** variants using the same model logic.
- Adds a treatment **guardrail framework**:
  - Simple policy & risk appetite checks.
  - Human oversight emulation (scripted accept/reject of medium/high risk).
  - Runtime controls: kill switch, rate limiter, simple circuit breaker.
  - Access control & structured logging into an in-memory store.
- Defines several synthetic workloads (WL1–WL5) that exercise different aspects of the controls.
- Measures a small set of numeric metrics that are actually computed at runtime:
  - `unsafe_decision_rate`
  - `decision_throughput`
  - `guardrail_activation_rate`

The design is structured so additional metrics could be added later (e.g., latency histograms, audit completeness), but we limit ourselves to metrics that are realistically measurable in this offline, single-process setting.

## Layout

- `run.py` – Main entrypoint; executes all workloads for both baseline and treatment and writes evidence.
- `experiment/__init__.py` – Package marker.
- `experiment/model.py` – Simple deterministic scoring model.
- `experiment/policy.py` – Risk appetite, policy checks, and unsafe decision evaluation.
- `experiment/guardrails.py` – Treatment guardrail framework (rate limiter, circuit breaker, kill switch, oversight, logging).
- `experiment/workloads.py` – Synthetic workload generators for WL1–WL5.
- `experiment/runner.py` – Orchestrates running workloads for baseline and treatment, collecting metrics, and building evidence.
- `tests/test_experiment.py` – Unit tests verifying evidence schema and basic behavior.
- `requirements.txt` – Empty of third-party runtime deps (standard library only).

## Running the experiment

1. **Ensure Python 3.11+ is available.**

2. **Set the evidence directory (optional)**

   By default, evidence is written to `/evidence/results.json`. You can override this by setting the `BOOKMAS_EVIDENCE_DIR` environment variable to a writable directory.

   ```bash
   export BOOKMAS_EVIDENCE_DIR=/evidence
   ```

3. **Run the experiment**

   ```bash
   python run.py
   ```

   This will:
   - Execute each workload (WL1–WL5) once for **baseline** and once for **treatment**.
   - Measure a few simple numeric metrics.
   - Write a JSON evidence file at `${BOOKMAS_EVIDENCE_DIR}/results.json` with the schema required by the prompt.

4. **Run tests**

   ```bash
   python -m unittest discover -s tests -p "test_*.py"
   ```

   Tests ensure:
   - The evidence file exists and is valid JSON.
   - The top-level schema requirements are met.
   - There is at least one baseline and one treatment run per workload.
   - Metrics contain only numeric values.

## Evidence file schema (runtime contract)

The experiment writes a single JSON object with the following shape:

```json
{
  "chapter": 8,
  "experiment_id": "exp-8-guardrails-controls-training-deployment-autonomy",
  "environment": {"os": "...", "python": "..."},
  "runs": [
    {
      "variant": "baseline" | "treatment",
      "workload_id": "WL1_normal_traffic" | ... | "WL5_kill_switch_operational_test",
      "run_id": "<unique string>",
      "success": true,
      "metrics": {
        "unsafe_decision_rate": 0.01,
        "decision_throughput": 123.4,
        "guardrail_activation_rate": 0.0
      }
    }
  ],
  "notes": "... optional free text ..."
}
```

Additional non-metric fields may be added in the future, but all **metric values must be finite JSON numbers** and derived from actual execution.

## Design notes

- **Determinism and reproducibility**: We seed the Python `random` module per workload/variant pair so that inputs are repeatable. This supports fair baseline vs treatment comparisons.
- **No external side effects**: The project avoids network calls, subprocesses, or file writes outside the current working directory and `/evidence`.
- **Guardrail simplification**: The guardrail components are minimal illustrative implementations (e.g., in-process counters and state) rather than network services. They are sufficient for demonstrating behavior differences in the treatment variant under the given workloads.

## Extending the experiment

In a richer environment, you could extend this scaffolding by:

- Swapping the toy model for a real ML model (e.g., scikit-learn), provided dependencies are allowed.
- Adding latency measurements using `time.perf_counter()` and simple histograms.
- Implementing hash-chained logs and explicit audit reconstruction as per the detailed specification.

Here, we keep the implementation focused on safe, bounded execution within an offline sandbox.