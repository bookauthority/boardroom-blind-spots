import json
import os
import platform
from typing import Dict, Any, List

from experiments.workloads import (
    run_wl_3_2,
    run_wl_3_3,
    run_wl_3_4,
    run_wl_3_5,
    run_wl_3_6,
    run_wl_3_7,
    run_wl_3_8,
)


CHAPTER_NUMBER = 3
EXPERIMENT_ID = "ch3-failure-modes-of-autonomous-ai-in-finance"


def ensure_evidence_dir() -> str:
    base = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    os.makedirs(base, exist_ok=True)
    return base


def build_environment_metadata() -> Dict[str, str]:
    return {
        "os": platform.platform(),
        "python": platform.python_version(),
    }


def main() -> None:
    evidence_dir = ensure_evidence_dir()

    all_runs: List[Dict[str, Any]] = []
    notes_parts: List[str] = []

    # Each workload runner returns a list of run dicts compliant with the schema.
    workload_fns = [
        run_wl_3_2,
        run_wl_3_3,
        run_wl_3_4,
        run_wl_3_5,
        run_wl_3_6,
        run_wl_3_7,
        run_wl_3_8,
    ]

    for fn in workload_fns:
        runs, note = fn()
        all_runs.extend(runs)
        if note:
            notes_parts.append(note)

    evidence: Dict[str, Any] = {
        "chapter": CHAPTER_NUMBER,
        "experiment_id": EXPERIMENT_ID,
        "environment": build_environment_metadata(),
        "runs": all_runs,
    }

    if notes_parts:
        evidence["notes"] = " | ".join(notes_parts)

    out_path = os.path.join(evidence_dir, "results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
