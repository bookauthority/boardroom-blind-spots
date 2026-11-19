# Chapter 2 Experiment: Mapping Your AI Attack Surface

This repository implements a **self-contained, offline Python 3.11+ experiment** for:

> **Chapter 2 – Mapping Your AI Attack Surface: Where Systemic Risk Can Hide**  
> Experiment ID: `ch02-ai-attack-surface-mapping-v1`

The goal is to compare a **manual baseline** vs a **scripted treatment** for building an AI risk inventory and attack-surface map over synthetic data.

## Overview

The experiment implements three workloads:

1. **workload-1-ai-inventory-pipeline**  
   Build an AI inventory and dependency list.

2. **workload-2-decision-chain-and-exposure-mapping**  
   Link AI assets to decision chains and exposures (simplified numeric coverage).

3. **workload-3-concentration-and-materiality-heatmaps**  
   Compute simple concentration / materiality coverage counts.

Each workload has a **baseline** and **treatment** variant. Both operate over the same synthetic CSV/YAML data but use different levels of structure:

- Baseline: emulates manual spreadsheets with missing/duplicated information.
- Treatment: uses scripted parsing with a more complete, standardized schema.

The code is designed for **safe, deterministic execution** with the Python standard library only.

## Key Files

- `run.py` – orchestrates the experiment, runs all workloads, and writes evidence.
- `experiment/core.py` – core data models, loaders, and metric helpers.
- `experiment/baseline.py` – baseline pipeline implementations.
- `experiment/treatment.py` – treatment pipeline implementations.
- `experiment/workloads.py` – workload runners that call baseline/treatment.
- `data/` – synthetic CSV and Excel-like (CSV) source data.
- `config/` – simple YAML configs for schema and mappings.
- `schemas/` – placeholder schema file referenced by the spec.
- `tests/test_experiment.py` – unit tests ensuring evidence schema compliance.

## Dependencies

The experiment uses **only the Python standard library**. `requirements.txt` is empty to comply with the sandbox constraints.

```bash
python -m venv .venv
source .venv/bin/activate  # on Windows: .venv\Scripts\activate
pip install -r requirements.txt  # no-op, but keeps workflow consistent
```

## Running Tests

From the project root:

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Running the Experiment

The harness that evaluates this project will set `BOOKMAS_EVIDENCE_DIR`. You can run manually as:

```bash
export BOOKMAS_EVIDENCE_DIR=/evidence  # or another writable path
mkdir -p "$BOOKMAS_EVIDENCE_DIR"
python run.py
```

This will create `${BOOKMAS_EVIDENCE_DIR}/results.json` with the following schema:

```json
{
  "chapter": 2,
  "experiment_id": "ch02-ai-attack-surface-mapping-v1",
  "environment": {"os": "...", "python": "..."},
  "runs": [
    {
      "variant": "baseline",  // or "treatment"
      "workload_id": "workload-1-ai-inventory-pipeline",
      "run_id": "...",        // unique within workload+variant
      "success": true,
      "metrics": {
        "ai_asset_coverage_count": 5.0,
        "dependency_coverage_count": 7.0
      }
    }
    // ... more runs for all workloads and variants
  ],
  "notes": "optional free-text"
}
```

**Important:**

- At least **one baseline and one treatment run per workload** are recorded.
- All metric values are **numbers** (no strings, objects, or nulls).
- Only metrics that are actually computed in this sandbox are included.
  - Here we compute `ai_asset_coverage_count` and `dependency_coverage_count` for relevant workloads.
- Other metrics from the chapter spec (e.g., board_readiness_score) are **not fabricated** and thus omitted from `metrics`.

## Synthetic Data Design

The synthetic CSV files encode:

- A model registry with both AI and non-AI assets and metadata.
- Data pipelines and their upstream/downstream links.
- Vendor-provided AI services.
- A manual, noisy baseline inventory.
- Decision chains mapping models to exposures.
- Financial exposure reference data.

The treatment pipeline reads from the source-of-truth style tables, while the baseline pipeline reads only from the manual baseline file, mimicking the chapter narrative.

## Limitations

- No external libraries (pandas, matplotlib, etc.) are used; CSV/YAML parsing and simple analytics are implemented with the standard library.
- Visualizations (graphs, heatmaps) are **not generated**; we focus on numeric coverage metrics to remain lightweight and deterministic.
- Many rich metrics from the conceptual spec cannot be meaningfully measured offline and so are not reported.

These limitations are documented in `run.py` under the `notes` field of the evidence output.
