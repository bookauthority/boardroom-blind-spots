import json
import os
import sys
import platform
from pathlib import Path

from toolkit.synthetic_data import ensure_synthetic_data
from toolkit.baseline import run_baseline_for_workload
from toolkit.treatment import run_treatment_for_workload


CHAPTER_NUMBER = 14
EXPERIMENT_ID = "exp-ch14-boardroom-toolkits-v1"


def main() -> None:
    # Determine evidence output directory
    evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    evidence_path = Path(evidence_dir)
    evidence_path.mkdir(parents=True, exist_ok=True)
    results_file = evidence_path / "results.json"

    # Ensure synthetic input data exists
    base_data_dir = Path("data") / "synthetic"
    ensure_synthetic_data(base_data_dir)

    workloads = [
        "W1-universal-bank-quarterly-pack",
        "W2-digital-bank-monthly-ops-review",
        "W3-asset-manager-annual-board-strategy",
    ]

    runs = []
    notes_parts = []

    for workload_id in workloads:
        workload_dir = base_data_dir / workload_id
        inventory_path = workload_dir / "ai_inventory.csv"
        incidents_path = workload_dir / "incidents.csv"

        # Baseline run
        baseline_success, baseline_metrics, baseline_note = run_baseline_for_workload(
            workload_id, inventory_path, incidents_path
        )
        runs.append(
            {
                "variant": "baseline",
                "workload_id": workload_id,
                "run_id": f"baseline-{workload_id}-1",
                "success": bool(baseline_success),
                "metrics": baseline_metrics,
            }
        )
        if baseline_note:
            notes_parts.append(f"{workload_id} baseline: {baseline_note}")

        # Treatment run
        treatment_success, treatment_metrics, treatment_note = run_treatment_for_workload(
            workload_id, inventory_path, incidents_path
        )
        runs.append(
            {
                "variant": "treatment",
                "workload_id": workload_id,
                "run_id": f"treatment-{workload_id}-1",
                "success": bool(treatment_success),
                "metrics": treatment_metrics,
            }
        )
        if treatment_note:
            notes_parts.append(f"{workload_id} treatment: {treatment_note}")

    environment = {
        "os": platform.platform(),
        "python": sys.version.split()[0],
    }

    notes_text = (
        "; ".join(notes_parts)
        if notes_parts
        else (
            "Metrics are limited to numeric quantities derivable from synthetic "
            "inventory and incident data (e.g., counts and averages). "
            "Human-elicited metrics like prep_time_hours, clarity_score, or "
            "actionability_score cannot be measured in this offline sandbox "
            "and are therefore omitted from the metrics objects."
        )
    )

    evidence = {
        "chapter": CHAPTER_NUMBER,
        "experiment_id": EXPERIMENT_ID,
        "environment": environment,
        "runs": runs,
        "notes": notes_text,
    }

    with results_file.open("w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
