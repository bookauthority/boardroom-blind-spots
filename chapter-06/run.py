import json
import os
import sys
import time
import uuid
import platform

from src.synthetic_portfolio import generate_portfolio
from src.metrics_engine import compute_baseline_metrics, compute_treatment_metrics
from src.governance import apply_governance
from src.evaluation import run_evaluation


CHAPTER_NUMBER = 6
EXPERIMENT_ID = "ch6-metrics-that-matter-ai-risk-indicators-v1"


def _time_it(func, *args, **kwargs):
    start = time.perf_counter()
    result = func(*args, **kwargs)
    end = time.perf_counter()
    runtime = end - start
    return result, runtime


def main() -> None:
    # Determine evidence directory
    evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
    os.makedirs(evidence_dir, exist_ok=True)
    evidence_path = os.path.join(evidence_dir, "results.json")

    runs = []

    # Workload 1: synthetic portfolio generation (same portfolio for both variants)
    # We still record separate timing runs to keep symmetry.
    workload_id_1 = "workload_1_synthetic_portfolio_generation"

    # Baseline variant
    portfolio_baseline, rt = _time_it(generate_portfolio)
    runs.append(
        {
            "variant": "baseline",
            "workload_id": workload_id_1,
            "run_id": str(uuid.uuid4()),
            "success": True,
            "metrics": {
                "runtime_seconds": float(rt)
            },
        }
    )

    # Treatment variant uses the exact same portfolio object to honour controls
    # but we still account for a logical run and its (near-zero) runtime.
    start_t = time.perf_counter()
    portfolio_treatment = portfolio_baseline
    rt_t = time.perf_counter() - start_t
    runs.append(
        {
            "variant": "treatment",
            "workload_id": workload_id_1,
            "run_id": str(uuid.uuid4()),
            "success": True,
            "metrics": {
                "runtime_seconds": float(rt_t)
            },
        }
    )

    # Workload 2: metric computation engine
    workload_id_2 = "workload_2_metric_computation_engine"

    # Baseline metrics
    (baseline_metrics, _), rt2b = _time_it(compute_baseline_metrics, portfolio_baseline)
    runs.append(
        {
            "variant": "baseline",
            "workload_id": workload_id_2,
            "run_id": str(uuid.uuid4()),
            "success": True,
            "metrics": {
                "runtime_seconds": float(rt2b)
            },
        }
    )

    # Treatment metrics (includes baseline plus AI-specific)
    (treatment_metrics, _), rt2t = _time_it(compute_treatment_metrics, portfolio_treatment)
    runs.append(
        {
            "variant": "treatment",
            "workload_id": workload_id_2,
            "run_id": str(uuid.uuid4()),
            "success": True,
            "metrics": {
                "runtime_seconds": float(rt2t)
            },
        }
    )

    # Workload 3: dashboard and heatmap generation (simulated, no plotting libs)
    # We emulate the computations a dashboard would need: grouping and summary.
    workload_id_3 = "workload_3_dashboard_and_heatmap_generation"

    def _simulate_dashboard(metrics):
        # Simple summarisation by model and time; returns a small structure.
        summary = {}
        for row in metrics:
            model = row["model_id"]
            summary.setdefault(model, 0)
            summary[model] += 1
        return summary

    # Baseline
    dashboard_baseline, rt3b = _time_it(_simulate_dashboard, baseline_metrics)
    # Treatment
    dashboard_treatment, rt3t = _time_it(_simulate_dashboard, treatment_metrics)

    runs.append(
        {
            "variant": "baseline",
            "workload_id": workload_id_3,
            "run_id": str(uuid.uuid4()),
            "success": True,
            "metrics": {
                "runtime_seconds": float(rt3b)
            },
        }
    )
    runs.append(
        {
            "variant": "treatment",
            "workload_id": workload_id_3,
            "run_id": str(uuid.uuid4()),
            "success": True,
            "metrics": {
                "runtime_seconds": float(rt3t)
            },
        }
    )

    # Workload 4 + 5: thresholds, triggers, escalation rules, scenario replay
    workload_id_4 = (
        "workload_4_thresholds_triggers_and_escalation_rules_"
        "and_workload_5_scenario_replay_and_comparative_evaluation"
    )

    # Baseline variant: evaluation using only baseline metrics
    def _baseline_eval():
        return run_evaluation(
            portfolio_baseline,
            baseline_metrics,
            treatment_metrics=None,
            apply_governance_fn=None,
        )

    eval_baseline, rt4b = _time_it(_baseline_eval)
    runs.append(
        {
            "variant": "baseline",
            "workload_id": workload_id_4,
            "run_id": str(uuid.uuid4()),
            "success": True,
            "metrics": {
                "runtime_seconds": float(rt4b)
            },
        }
    )

    # Treatment variant: evaluation using AI risk metrics and governance
    def _treatment_eval():
        return run_evaluation(
            portfolio_treatment,
            baseline_metrics,
            treatment_metrics=treatment_metrics,
            apply_governance_fn=apply_governance,
        )

    eval_treatment, rt4t = _time_it(_treatment_eval)
    runs.append(
        {
            "variant": "treatment",
            "workload_id": workload_id_4,
            "run_id": str(uuid.uuid4()),
            "success": True,
            "metrics": {
                "runtime_seconds": float(rt4t)
            },
        }
    )

    # Compose evidence structure
    environment = {
        "os": platform.platform(),
        "python": sys.version.split()[0],
    }

    evidence = {
        "chapter": CHAPTER_NUMBER,
        "experiment_id": EXPERIMENT_ID,
        "environment": environment,
        "runs": runs,
        "notes": (
            "Runtime metrics only; richer AI risk indicators and scenario "
            "comparisons are computed internally but not exposed as numeric "
            "evidence fields in this minimal results.json envelope."
        ),
    }

    with open(evidence_path, "w", encoding="utf-8") as f:
        json.dump(evidence, f, indent=2)


if __name__ == "__main__":
    main()
