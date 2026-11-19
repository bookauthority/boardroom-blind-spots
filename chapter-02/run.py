import json
import os
import platform
import time
from typing import Any, Dict, List

from experiment.workloads import (
    run_workload_1_baseline,
    run_workload_1_treatment,
    run_workload_2_baseline,
    run_workload_2_treatment,
    run_workload_3_baseline,
    run_workload_3_treatment,
)


CHAPTER_NUMBER = 2
EXPERIMENT_ID = "ch02-ai-attack-surface-mapping-v1"


def _now_ns() -> int:
    return time.time_ns()


def main() -> None:
    evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", ".")
    os.makedirs(evidence_dir, exist_ok=True)
    results_path = os.path.join(evidence_dir, "results.json")

    env_info = {
        "os": platform.platform(),
        "python": platform.python_version(),
    }

    runs: List[Dict[str, Any]] = []

    # Workload 1: AI inventory and dependency mapping
    start = _now_ns()
    try:
        metrics_b1 = run_workload_1_baseline()
        success_b1 = True
    except Exception:
        metrics_b1 = {}
        success_b1 = False
    duration_b1 = (time.time_ns() - start) / 1e9
    if success_b1:
        metrics_b1.setdefault("execution_time_seconds", float(duration_b1))
    runs.append(
        {
            "variant": "baseline",
            "workload_id": "workload-1-ai-inventory-pipeline",
            "run_id": f"baseline-{_now_ns()}",
            "success": bool(success_b1),
            "metrics": {k: float(v) for k, v in metrics_b1.items()},
        }
    )

    start = _now_ns()
    try:
        metrics_t1 = run_workload_1_treatment()
        success_t1 = True
    except Exception:
        metrics_t1 = {}
        success_t1 = False
    duration_t1 = (time.time_ns() - start) / 1e9
    if success_t1:
        metrics_t1.setdefault("execution_time_seconds", float(duration_t1))
    runs.append(
        {
            "variant": "treatment",
            "workload_id": "workload-1-ai-inventory-pipeline",
            "run_id": f"treatment-{_now_ns()}",
            "success": bool(success_t1),
            "metrics": {k: float(v) for k, v in metrics_t1.items()},
        }
    )

    # Workload 2: Decision chains and exposure mapping
    start = _now_ns()
    try:
        metrics_b2 = run_workload_2_baseline()
        success_b2 = True
    except Exception:
        metrics_b2 = {}
        success_b2 = False
    duration_b2 = (time.time_ns() - start) / 1e9
    if success_b2:
        metrics_b2.setdefault("execution_time_seconds", float(duration_b2))
    runs.append(
        {
            "variant": "baseline",
            "workload_id": "workload-2-decision-chain-and-exposure-mapping",
            "run_id": f"baseline-{_now_ns()}",
            "success": bool(success_b2),
            "metrics": {k: float(v) for k, v in metrics_b2.items()},
        }
    )

    start = _now_ns()
    try:
        metrics_t2 = run_workload_2_treatment()
        success_t2 = True
    except Exception:
        metrics_t2 = {}
        success_t2 = False
    duration_t2 = (time.time_ns() - start) / 1e9
    if success_t2:
        metrics_t2.setdefault("execution_time_seconds", float(duration_t2))
    runs.append(
        {
            "variant": "treatment",
            "workload_id": "workload-2-decision-chain-and-exposure-mapping",
            "run_id": f"treatment-{_now_ns()}",
            "success": bool(success_t2),
            "metrics": {k: float(v) for k, v in metrics_t2.items()},
        }
    )

    # Workload 3: Concentration and materiality heatmaps (simplified coverage)
    start = _now_ns()
    try:
        metrics_b3 = run_workload_3_baseline()
        success_b3 = True
    except Exception:
        metrics_b3 = {}
        success_b3 = False
    duration_b3 = (time.time_ns() - start) / 1e9
    if success_b3:
        metrics_b3.setdefault("execution_time_seconds", float(duration_b3))
    runs.append(
        {
            "variant": "baseline",
            "workload_id": "workload-3-concentration-and-materiality-heatmaps",
            "run_id": f"baseline-{_now_ns()}",
            "success": bool(success_b3),
            "metrics": {k: float(v) for k, v in metrics_b3.items()},
        }
    )

    start = _now_ns()
    try:
        metrics_t3 = run_workload_3_treatment()
        success_t3 = True
    except Exception:
        metrics_t3 = {}
        success_t3 = False
    duration_t3 = (time.time_ns() - start) / 1e9
    if success_t3:
        metrics_t3.setdefault("execution_time_seconds", float(duration_t3))
    runs.append(
        {
            "variant": "treatment",
            "workload_id": "workload-3-concentration-and-materiality-heatmaps",
            "run_id": f"treatment-{_now_ns()}",
            "success": bool(success_t3),
            "metrics": {k: float(v) for k, v in metrics_t3.items()},
        }
    )

    evidence: Dict[str, Any] = {
        "chapter": CHAPTER_NUMBER,
        "experiment_id": EXPERIMENT_ID,
        "environment": env_info,
        "runs": runs,
        "notes": (
            "Metrics are limited to counts and execution times that can be "
            "reliably measured in this offline sandbox. Richer chapter "
            "metrics (e.g., board_readiness_score, reproducibility across "
            "independent human runs, visual quality) are intentionally not "
            "reported to avoid fabrication."
        ),
    }

    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2, sort_keys=True)


if __name__ == "__main__":
    main()
