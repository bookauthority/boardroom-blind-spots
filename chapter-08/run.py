import json
import os
import platform
import sys
from typing import Any, Dict, List

from experiment.runner import ExperimentRunner


CHAPTER_NUMBER = 8
EXPERIMENT_ID = "exp-8-guardrails-controls-training-deployment-autonomy"


def main() -> None:
    evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    os.makedirs(evidence_dir, exist_ok=True)
    evidence_path = os.path.join(evidence_dir, "results.json")

    runner = ExperimentRunner(
        chapter=CHAPTER_NUMBER,
        experiment_id=EXPERIMENT_ID,
    )

    runs: List[Dict[str, Any]] = []

    # Workload IDs as defined in the specification
    workload_ids = [
        "WL1_normal_traffic",
        "WL2_data_drift_and_model_stress",
        "WL3_policy_violation_and_misuse_attempts",
        "WL4_adverse_event_and_feedback_loop_spike",
        "WL5_kill_switch_operational_test",
    ]

    # For each workload, run baseline and treatment once
    for workload_id in workload_ids:
        # Baseline
        baseline_run = runner.run_workload(
            variant="baseline",
            workload_id=workload_id,
        )
        runs.append(baseline_run)

        # Treatment
        treatment_run = runner.run_workload(
            variant="treatment",
            workload_id=workload_id,
        )
        runs.append(treatment_run)

    evidence: Dict[str, Any] = {
        "chapter": CHAPTER_NUMBER,
        "experiment_id": EXPERIMENT_ID,
        "environment": {
            "os": platform.platform(),
            "python": sys.version.split()[0],
        },
        "runs": runs,
        "notes": (
            "Toy implementation running deterministic synthetic workloads for "
            "baseline vs treatment guardrail comparison. Metrics are limited "
            "to those directly measurable in this offline sandbox."
        ),
    }

    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
