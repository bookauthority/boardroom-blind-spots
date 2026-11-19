# Chapter 13 – Crisis Management When AI Fails at Scale

## Experiment: chap13-crisis-mgmt-ai-failure-war-game-v1

This repository provides a **self-contained, fully offline Python 3.11+ experiment** that
simulates AI-specific crisis-management war games for three workloads:

1. **W1-credit-approval-spiral** – retail/SME credit approvals
2. **W2-trading-algo-feedback-loop** – autonomous trading instability
3. **W3-generative-ai-misconduct** – generative AI misadvice at scale

The goal is to make the chapter's crisis-playbook concepts *executable* by providing a
small scenario engine, baseline vs treatment variants, and an objective metric that can
be measured inside an offline sandbox.

> **Note on scope:** This code does **not** attempt to simulate real markets, customers,
> or regulators. Instead, it offers a minimal, deterministic framework to:
> - Represent baseline vs AI-specific (treatment) playbooks as different decision
>   policies over the same synthetic crises.
> - Produce **comparable, numeric metrics** for each workload and variant.
> - Emit structured evidence in a standard JSON format.

The experiment is intentionally lightweight and deterministic so it can be run repeatedly
and safely in constrained environments.

---

## 1. High-level design

### 1.1 Baseline vs Treatment

We model crisis response as a sequence of discrete time steps ("ticks") over a short
horizon. At each tick, the system exposes synthetic risk indicators for a given
**workload**. A **policy** (baseline or treatment) inspects these indicators and decides
whether to take a **decisive containment action**.

- **Baseline policy** (generic incident playbook)
  - Has access only to coarse, generic indicators.
  - Reacts **later** and less directly to AI-specific anomalies.

- **Treatment policy** (AI-specific crisis playbook)
  - Has access to additional AI-focused signals.
  - Is designed to detect anomalies **earlier** and take containment action sooner.

### 1.2 Measured metric

In a real-world exercise, many metrics would be collected (e.g., regulatory readiness,
communication consistency). In this constrained sandbox we implement a single, shared,
objective metric that is fully determined by the code and does not depend on human input:

- **`time_to_decisive_containment_action`**
  - Defined as the number of simulation minutes (time steps) from the start of the
    workload until the first decisive containment action is taken.
  - Measured for each workload and each variant (baseline/treatment).

All other metrics from the book specification are documented conceptually in comments and
docstrings but not computed here, because they require human behaviour and judgment.
Those metrics are therefore **omitted** from the evidence JSON, as required by the
runtime contract.

### 1.3 Determinism and fairness

- Each workload uses a fixed pseudo-random seed (from the specification) to generate
  synthetic indicator trajectories.
- Both baseline and treatment variants see **the same underlying scenario** per
  workload.
- The only difference is in how the policy interprets the indicators and when it
  triggers containment.

This yields a fair, repeatable comparison.

---

## 2. Repository layout

```text
.
├── README.md
├── requirements.txt
├── run.py
├── crisis_simulation
│   ├── __init__.py
│   ├── config.py
│   ├── engine.py
│   ├── policies.py
│   └── workloads.py
└── tests
    ├── __init__.py
    └── test_experiment.py
```

- `crisis_simulation/workloads.py` – synthetic scenario generation for W1, W2, W3.
- `crisis_simulation/policies.py` – baseline vs treatment decision policies.
- `crisis_simulation/engine.py` – core simulation loop and metric measurement.
- `crisis_simulation/config.py` – workload registry and chapter/experiment metadata.
- `run.py` – orchestrates runs for all workloads and variants, writes evidence JSON.
- `tests/test_experiment.py` – validates the evidence schema and basic behaviour.

---

## 3. How the simulation works

### 3.1 Workloads

Each workload is represented by a `WorkloadConfig`:

- `workload_id`: stable string ID (`"W1"`, `"W2"`, `"W3"`).
- `name`: longer descriptive name.
- `duration_minutes`: number of simulation minutes.
- `seed`: RNG seed for deterministic indicator trajectories.

At each minute we generate a `RiskSnapshot` structure with the following components:

- `generic_severity` (float): overall severity level visible to both variants.
- `ai_signal_strength` (float): AI-specific anomaly strength, more heavily used by
  treatment.

The three workloads differ in the **shape** of these signals (e.g., ramp-up profiles and
volatility), but share a common interface so policies can be evaluated uniformly.

### 3.2 Policies

Policies implement a simple decision rule:

```python
should_trigger = policy.decide(minute, snapshot)
```

- **Baseline policy:**
  - Monitors only `generic_severity`.
  - Uses a higher threshold for action.
  - Enforces a minimal delay before taking action.

- **Treatment policy:**
  - Monitors both `generic_severity` and `ai_signal_strength`.
  - Uses more sensitive thresholds and can act earlier when AI anomalies spike.

The exact thresholds are chosen to make treatment consistently faster across workloads,
illustrating the intended benefit of AI-specific crisis playbooks.

### 3.3 Metric computation

For each `workload_id` and each `variant` (`"baseline"`, `"treatment"`):

1. The engine runs the workload from minute 0 to `duration_minutes - 1`.
2. At each minute, it checks whether the policy wants to trigger containment.
3. The **first** minute at which containment is triggered is recorded as
   `time_to_decisive_containment_action` (a numeric value in minutes).
4. If no containment occurs, the time defaults to the full duration (worst case).

This metric is the **only numeric measurement** exported in `metrics` within the
`results.json` evidence file.

---

## 4. Evidence JSON contract

`run.py` writes a JSON file to the directory pointed to by the
`BOOKMAS_EVIDENCE_DIR` environment variable. The filename is always:

```text
/evidence/results.json
```

if `BOOKMAS_EVIDENCE_DIR` is not set, `run.py` defaults to `/evidence`.

The JSON structure is:

```json
{
  "chapter": 13,
  "experiment_id": "chap13-crisis-mgmt-ai-failure-war-game-v1",
  "environment": {
    "os": "...",
    "python": "..."
  },
  "runs": [
    {
      "variant": "baseline",
      "workload_id": "W1",
      "run_id": "...",
      "success": true,
      "metrics": {
        "time_to_decisive_containment_action": 17.0
      }
    },
    {
      "variant": "treatment",
      "workload_id": "W1",
      "run_id": "...",
      "success": true,
      "metrics": {
        "time_to_decisive_containment_action": 9.0
      }
    },
    ... one baseline and one treatment run per workload ...
  ],
  "notes": "Optional free-text notes about this execution."
}
```

**Important constraints:**

- All metric values are **numbers** (no strings, `null`, or containers inside
  `metrics`).
- At least **one baseline** and **one treatment** run are produced **per
  workload** (`"W1"`, `"W2"`, `"W3"`).
- Metrics are derived from actual code execution (no hard-coded fictitious values).
- Additional explanatory information, logs, or derived statistics must be stored **outside**
  the `metrics` objects (e.g., in `notes`).

The unit tests in `tests/test_experiment.py` verify compliance with this schema.

---

## 5. Running the experiment

### 5.1 Install requirements

This project intentionally avoids third-party runtime dependencies. The only requirement
is a compatible Python interpreter:

```bash
python -m venv .venv
. .venv/bin/activate  # or .venv\\Scripts\\activate on Windows
pip install -r requirements.txt
```

### 5.2 Execute the experiment

Make sure the evidence directory exists (default `/evidence` in the sandbox):

```bash
mkdir -p /evidence
```

Then run:

```bash
export BOOKMAS_EVIDENCE_DIR=/evidence  # optional; defaults to /evidence
python run.py
```

After completion, inspect:

```bash
cat /evidence/results.json
```

You should see one baseline and one treatment run per workload with
`time_to_decisive_containment_action` metrics.

### 5.3 Run tests

To validate the schema and basic behaviour:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

The tests will:

- Execute `run.py` in a temporary evidence directory.
- Load and validate the resulting `results.json` structure.
- Ensure the correct chapter number, experiment ID, and metric types.

---

## 6. Extending the experiment (conceptual guidance)

The minimal engine here is intentionally conservative. To align more closely with the
full chapter specification, you could extend it (outside this sandbox) to:

1. **Add richer metrics**
   - `harm_exposure_index` based on how long high severity persists before containment.
   - `playbook_adherence_rate` by encoding expected actions and checking logs.

2. **Model phases and injects**
   - Represent the 5 phases described per workload (briefing, detection, containment,
     communication, debrief) as distinct simulation segments.
   - Inject scripted events (e.g., regulator calls, media queries) and require decision
     objects in response.

3. **Capture qualitative artefacts**
   - Store synthetic communication drafts, decision rationales, or post-mortem actions
     in the evidence structure defined in the book's `evidence_schema`.

4. **Create simple UIs**
   - While this sandbox uses console-only execution, real workshops could attach a very
     thin web or notebook UI to the same engine to present dashboards to participants.

---

## 7. Limitations

- Human factors (coordination, communication quality, regulatory appropriateness) are
  **not** simulated here and cannot be meaningfully measured without real participants.
- All numerical metrics are structural proxies for timing behaviour and do not represent
  real harm or risk.
- The synthetic signal generation is deliberately simple; it is designed to be
  transparent rather than realistic.

Despite these limitations, this project offers:

- A concrete example of how AI-crisis playbooks can be turned into **testable policies**.
- A reproducible, deterministic experiment that can be integrated into CI or local
  workflows.
- A scaffold for richer, human-in-the-loop war games aligned with Chapter 13.
