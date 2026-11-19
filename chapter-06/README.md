# Chapter 6 Experiment – Metrics that Matter: AI Risk Indicators for the Board

This project is a **self‑contained, pure‑Python** experiment for:

> **experiment_id:** `ch6-metrics-that-matter-ai-risk-indicators-v1`

It simulates a small AI model portfolio for a universal bank, computes both
traditional KPI/KRI metrics and AI‑specific risk indicators, and compares a
**baseline dashboard** (traditional metrics only) to a **treatment dashboard**
(AI risk metrics + governance logic).

The code is designed for **offline, deterministic execution** in restrictive
sandboxes – it uses only the Python standard library (no external packages).

Key elements implemented:

- Synthetic portfolio generation (8 models × 24 monthly periods)
- Embedded stress scenarios:
  - Scenario A – gradual drift for a high‑criticality credit model
  - Scenario B – fairness deterioration for a protected group
  - Scenario C – correlation spike across trading models
- Baseline metrics (business KPIs / KRIs) and treatment metrics (drift,
  fairness, stability proxy, autonomy, and a simple composite risk score)
- Simple thresholds and rule‑based triggers for the treatment condition
- Scenario replay and comparative evaluation
- Evidence output in the minimal runtime format requested by BOOKMAS

> **Important:** This is a **didactic reference implementation**, not a
> production risk engine. It uses simplified formulas for metrics like drift
> and fairness to stay lightweight and transparent.

---

## Project layout

```
experiments/ch6_metrics_that_matter/
├── README.md
├── requirements.txt
├── run.py
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── synthetic_portfolio.py
│   ├── metrics_engine.py
│   ├── governance.py
│   ├── scenarios.py
│   └── evaluation.py
└── tests/
    ├── __init__.py
    └── test_experiment.py
```

Only the files under this directory are needed to run the experiment.

---

## Requirements

The code targets **Python 3.11+** and deliberately avoids third‑party
libraries. The `requirements.txt` file is therefore minimal and documents that
no additional runtime dependencies are needed.

- Python ≥ 3.11
- Standard library only (no `pip install` required for core execution)

---

## How to run

From the root of this experiment directory
`experiments/ch6_metrics_that_matter/`:

```bash
# (Optional) create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# No extra deps are required, but you can still run:
pip install -r requirements.txt

# Run the full experiment and write evidence
python run.py
```

### Evidence output contract

The runner writes a JSON file to the directory specified by the
`BOOKMAS_EVIDENCE_DIR` environment variable. In typical BOOKMAS execution this
is `/evidence`.

The file path and JSON envelope are:

- Path: `${BOOKMAS_EVIDENCE_DIR:-/evidence}/results.json`
- Contents:

```json
{
  "chapter": 6,
  "experiment_id": "ch6-metrics-that-matter-ai-risk-indicators-v1",
  "environment": {
    "os": "...",
    "python": "..."
  },
  "runs": [
    {
      "variant": "baseline",
      "workload_id": "workload_1_synthetic_portfolio_generation",
      "run_id": "...",
      "success": true,
      "metrics": {
        "runtime_seconds": 0.0123
      }
    },
    {
      "variant": "treatment",
      "workload_id": "workload_1_synthetic_portfolio_generation",
      "run_id": "...",
      "success": true,
      "metrics": {
        "runtime_seconds": 0.0111
      }
    },
    ...
  ],
  "notes": "... optional free‑text notes ..."
}
```

**Constraints implemented:**

- At least **one baseline and one treatment run per workload**.
- Every metric value is a **finite JSON number** (no strings, objects,
  booleans, or nulls within `metrics`).
- Additional details (e.g. textual descriptions, environment metadata beyond
  `os`/`python`, risk‑indicator summaries) are stored **outside** the
  `metrics` map (e.g. in `notes`).
- All numeric metrics recorded are derived from **actual instrumented
  execution times** measured with `time.perf_counter()`.

The runner covers all conceptual workloads from the specification via four
internal phases:

1. `workload_1_synthetic_portfolio_generation`
2. `workload_2_metric_computation_engine`
3. `workload_3_dashboard_and_heatmap_generation`
4. `workload_4_thresholds_triggers_and_escalation_rules_and_workload_5_scenario_replay`

Each phase is executed separately for **baseline** and **treatment** variants
where meaningful, and timing metrics are recorded.

---

## What the code actually simulates

### Synthetic portfolio

`src/synthetic_portfolio.py` creates a deterministic portfolio with a fixed
random seed so that repeated runs are reproducible:

- **Models (8 total):**
  - `retail_credit_scoring`
  - `sme_credit_scoring`
  - `market_making_agent`
  - `aml_transaction_monitoring`
  - `card_fraud_detection`
  - `marketing_next_best_action`
  - `llm_customer_service_assistant`
  - `algo_execution_router`

For each model and period we simulate:

- metadata: business line, model type, criticality tier, auto‑decision share
- volume of decisions
- outcomes: approval rate, default / fraud rate, PnL proxy
- conduct: complaints per 10k customers
- autonomy: override rate, escalation rate to humans
- simplified features and outputs (used for drift and fairness proxies)

### Embedded scenarios

`src/scenarios.py` injects three overlapping structural patterns into the
synthetic data after generation:

- **Scenario A (gradual drift)** – monotonic drift in approval and default
  behaviour for `retail_credit_scoring` starting around month 8.
- **Scenario B (fairness shift)** – growing fairness gap in approval rates
  for a protected group within `sme_credit_scoring` starting around month 10.
- **Scenario C (correlation spike)** – increasing output correlation between
  `market_making_agent` and `algo_execution_router` starting around month 12.

The ground‑truth change and loss times are fixed in the code and reused for
baseline vs treatment comparison.

### Metric computation

`src/metrics_engine.py` implements two layers of metrics:

- **Baseline metrics (per model × period):**
  - `approval_rate`
  - `default_rate` (or analogous loss proxy)
  - `fraud_detected_rate` (for relevant models, zero for others)
  - `pnl_contribution`
  - `complaint_rate_per_10k_customers`

- **AI‑specific metrics (treatment only):**
  - `input_data_drift_score` – simple bounded shift measure between current
    and baseline distribution proxies
  - `prediction_drift_score` – shift in approval rate vs historical baseline
  - `stability_index` – similarity of successive periods (1 – change rate)
  - `fairness_gap` – difference in approval proxies between two groups
  - `explainability_coverage_pct` – synthetic but structured by model type
  - `auto_decision_share_pct` and `override_rate_by_humans`
  - `surprise_index` – non‑stationarity proxy for the LLM assistant
  - `composite_risk_score` – simple aggregation of normalized risk signals

Portfolio‑level indicators (e.g. count of models above drift threshold,
correlation spike proxies) are also computed but are not all recorded as
runtime metrics in `results.json` to comply with the minimal evidence schema
requirements.

### Governance, thresholds, and triggers

`src/governance.py` defines:

- Threshold bands (green/amber/red) for drift, fairness gap, autonomy, etc.
- A rule engine that:
  - maps raw metrics → risk bands → governance actions
  - produces a list of trigger events (model, time, trigger type, severity)

`src/evaluation.py` compares baseline vs treatment:

- Detection times based on:
  - Baseline: when lagging KPIs exceed bands (default rate, complaints, PnL)
  - Treatment: when AI risk metrics trigger amber/red actions
- Lead‑time gains and basic early‑warning measures are computed internally.

For the global `results.json` we **only record timing metrics** (runtime per
workload × variant) to satisfy the evidence contract. Richer evaluation
artifacts (lead times, trigger histories) could be extended into separate
JSON or CSV files if desired, but are not required by the current spec.

---

## Testing

From the experiment root directory:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

Tests ensure that:

- `run.py` can be imported and executed without raising exceptions.
- The evidence file `/evidence/results.json` (or its configured equivalent)
  is created.
- The JSON envelope matches the required schema:
  - top‑level keys `chapter`, `experiment_id`, `environment`, `runs` exist
  - at least one baseline and one treatment run per workload id
  - each `metrics` map contains only numbers

The tests use only the standard library (e.g. `unittest`, `json`, `os`).

---

## Extensibility

The structure is intentionally simple but can be
extended to more sophisticated experiments:

- Swap the synthetic portfolio generator for real (de‑identified) data
  loaders while preserving the metric computation and governance layers.
- Add richer metrics (e.g. JS divergence, PSI, SHAP‑based complexity) once
  additional libraries are allowed.
- Export full per‑model, per‑period time series following the rich
  `evidence_schema` in the chapter spec.

This reference implementation focuses on **reproducibility, determinism, and
schema correctness** to support technical readers experimenting with AI risk
indicators in constrained environments.
