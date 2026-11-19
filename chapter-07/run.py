import json
import os
import sys
import platform
from datetime import datetime
from typing import List, Dict, Any

from experiment.engine import run_all_workloads


def main() -> None:
    chapter_number = 7
    experiment_id = "ch7-scenario-ai-model-collapse-stresstest-v1"

    start_time = datetime.utcnow()

    # Run all workloads under both baseline and treatment.
    runs: List[Dict[str, Any]] = []
    notes_parts: List[str] = []

    results = run_all_workloads()

    for entry in results:
        runs.append(
            {
                "variant": entry["variant"],
                "workload_id": entry["workload_id"],
                "run_id": entry["run_id"],
                "success": bool(entry["success"]),
                "metrics": entry["metrics"],
            }
        )
        if entry.get("note"):
            notes_parts.append(f"{entry['workload_id']}[{entry['variant']}]: {entry['note']}")

    end_time = datetime.utcnow()

    env_info = {
        "os": platform.platform(),
        "python": sys.version.split()[0],
    }

    evidence: Dict[str, Any] = {
        "chapter": chapter_number,
        "experiment_id": experiment_id,
        "environment": env_info,
        "runs": runs,
    }

    if notes_parts:
        elapsed = (end_time - start_time).total_seconds()
        notes_parts.append(f"Total wall-clock runtime (s): {elapsed:.6f}")
        evidence["notes"] = " | ".join(notes_parts)

    evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    os.makedirs(evidence_dir, exist_ok=True)
    evidence_path = os.path.join(evidence_dir, "results.json")

    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
