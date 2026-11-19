import json
import os
import sys
import platform
from typing import List, Dict, Any

from experiment.baseline_runner import run_baseline_wl1, run_baseline_wl2
from experiment.treatment_runner import run_treatment_wl1, run_treatment_wl2


CHAPTER_NUMBER = 12
EXPERIMENT_ID = "exp-12-model-validation-reimagined-v1"


def get_environment_info() -> Dict[str, Any]:
    return {
        "os": os.name,
        "python": platform.python_version(),
    }


def main() -> None:
    # Orchestrate baseline and treatment for both workloads.
    runs: List[Dict[str, Any]] = []

    # WL1 - tabular credit scoring pipeline
    wl1_baseline = run_baseline_wl1()
    runs.append({
        "variant": "baseline",
        "workload_id": "WL1-tabular-credit-scoring-pipeline",
        "run_id": "baseline-WL1",
        "success": wl1_baseline["success"],
        "metrics": wl1_baseline["metrics"],
    })

    wl1_treatment = run_treatment_wl1()
    runs.append({
        "variant": "treatment",
        "workload_id": "WL1-tabular-credit-scoring-pipeline",
        "run_id": "treatment-WL1",
        "success": wl1_treatment["success"],
        "metrics": wl1_treatment["metrics"],
    })

    # WL2 - optional LLM assistant subcomponent (simulated)
    wl2_baseline = run_baseline_wl2()
    runs.append({
        "variant": "baseline",
        "workload_id": "WL2-llm-assistant-subcomponent-optional",
        "run_id": "baseline-WL2",
        "success": wl2_baseline["success"],
        "metrics": wl2_baseline["metrics"],
    })

    wl2_treatment = run_treatment_wl2()
    runs.append({
        "variant": "treatment",
        "workload_id": "WL2-llm-assistant-subcomponent-optional",
        "run_id": "treatment-WL2",
        "success": wl2_treatment["success"],
        "metrics": wl2_treatment["metrics"],
    })

    evidence = {
        "chapter": CHAPTER_NUMBER,
        "experiment_id": EXPERIMENT_ID,
        "environment": get_environment_info(),
        "runs": runs,
        "notes": (
            "Synthetic, deterministic offline experiment demonstrating baseline vs. "
            "treatment validation harness for tabular credit scoring (WL1) and a "
            "simulated LLM explanation component (WL2). All metrics are computed "
            "from actual executed code in this sandbox; no external data or APIs are used."
        ),
    }

    evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    os.makedirs(evidence_dir, exist_ok=True)
    evidence_path = os.path.join(evidence_dir, "results.json")

    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=False)

    # Also print a short message to stdout to help manual debugging if needed.
    sys.stdout.write(f"Evidence written to {evidence_path}\n")


if __name__ == "__main__":
    main()
