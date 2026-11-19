# Boardroom Toolkits Experiment (Chapter 14)

This project is a self-contained Python 3.11+ experiment for:

- **Chapter**: 14 – *"Boardroom Toolkits: Dashboards, Templates, and Checklists"*
- **Experiment ID**: `exp-ch14-boardroom-toolkits-v1`

It simulates baseline vs. treatment generation of AI oversight materials for three workloads (institution archetypes) using deterministic synthetic data. It then records numeric metrics in a reproducible way, following the required evidence schema.

The implementation is intentionally minimal and uses **only the Python standard library** so it can run in restricted, offline environments.

## Project Structure

```text
.
├── README.md
├── requirements.txt
├── run.py
├── data
│   └── synthetic
│       ├── W1-universal-bank-quarterly-pack
│       │   ├── ai_inventory.csv
│       │   └── incidents.csv
│       ├── W2-digital-bank-monthly-ops-review
│       │   ├── ai_inventory.csv
│       │   └── incidents.csv
│       └── W3-asset-manager-annual-board-strategy
│           ├── ai_inventory.csv
│           └── incidents.csv
├── toolkit
│   ├── __init__.py
│   ├── config.py
│   ├── data_models.py
│   ├── synthetic_data.py
│   ├── baseline.py
│   ├── treatment.py
│   ├── metrics.py
│   └── board_pack_templates.py
└── tests
    ├── __init__.py
    └── test_experiment.py
```

## What the Code Does

- Creates **synthetic AI inventory and incident datasets** for three workloads:
  - `W1-universal-bank-quarterly-pack`
  - `W2-digital-bank-monthly-ops-review`
  - `W3-asset-manager-annual-board-strategy`
- Implements:
  - A **baseline generator** that counts and groups data in a simple way.
  - A **treatment toolkit** with:
    - Basic AI inventory summaries and synthetic heatmap-like aggregations.
    - Simple incident statistics and structured representations.
    - Lightweight representations of dashboards, policies, question guides, and incident reports.
- Measures simple, deterministic metrics for each workload and variant:
  - `num_systems`: number of AI systems in the inventory.
  - `num_incidents`: number of incidents.
  - `num_high_criticality_systems`: number of systems with criticality above a threshold.
  - `avg_incident_severity`: average numeric incident severity.
- Writes a single evidence file at the path specified by the `BOOKMAS_EVIDENCE_DIR` environment variable:

```json
{
  "chapter": 14,
  "experiment_id": "exp-ch14-boardroom-toolkits-v1",
  "environment": {"os": "...", "python": "..."},
  "runs": [
    {
      "variant": "baseline",
      "workload_id": "W1-universal-bank-quarterly-pack",
      "run_id": "baseline-W1-universal-bank-quarterly-pack-1",
      "success": true,
      "metrics": {
        "num_systems": 30,
        "num_incidents": 15,
        "num_high_criticality_systems": 10,
        "avg_incident_severity": 2.6
      }
    },
    {
      "variant": "treatment",
      "workload_id": "W1-universal-bank-quarterly-pack",
      "run_id": "treatment-W1-universal-bank-quarterly-pack-1",
      "success": true,
      "metrics": {
        "num_systems": 30,
        "num_incidents": 15,
        "num_high_criticality_systems": 10,
        "avg_incident_severity": 2.6
      }
    }
    // ... analogous entries for W2 and W3 ...
  ],
  "notes": "..."
}
```

The metrics are computed from the same underlying datasets for both baseline and treatment to ensure a fair comparison. Because this sandbox cannot measure real-world board prep time or human survey scores, those metrics are **not included**. This limitation is documented in the `notes` field of the evidence.

## How to Run the Experiment

1. **Install requirements** (standard library only, but included for completeness):

   ```bash
   python -m pip install -r requirements.txt
   ```

2. **Set the evidence directory** (the harness will usually do this). If running manually:

   ```bash
   export BOOKMAS_EVIDENCE_DIR="/evidence"
   mkdir -p "$BOOKMAS_EVIDENCE_DIR"
   ```

3. **Run the experiment**:

   ```bash
   python run.py
   ```

4. After running, the evidence file should be at:

   ```text
   /evidence/results.json
   ```

## Running Tests

Tests use the Python standard library `unittest` module and validate:

- The evidence file schema and required keys.
- Presence of at least one baseline and one treatment run per workload.
- Metric values are finite numbers, not strings or nulls.

Run tests with:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Notes on Limitations

- This experiment **does not** attempt to measure real preparation time, clarity scores, or actionability scores. Those require human participants.
- Instead, it focuses on building a reproducible pipeline and logging numeric metrics that can be computed in this offline environment.
- The synthetic toolkits (dashboards, policies, question lists) are simplified but reflect the structure of Chapter 14’s proposed toolkit: inventory views, heatmaps, dashboards, policies, challenge guides, incident reports, and configuration-driven customization.
