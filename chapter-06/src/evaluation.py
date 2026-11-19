from __future__ import annotations

from typing import Callable, Dict, List, Optional


def _index_by_model_period(rows: List[Dict]) -> Dict[tuple, Dict]:
    idx: Dict[tuple, Dict] = {}
    for r in rows:
        idx[(r["model_id"], r["period"])] = r
    return idx


def _compute_baseline_detection_times(portfolio: List[Dict]) -> Dict[str, int]:
    """Crude baseline detection time per model using only lagging KPIs.

    We flag a model when default_rate or complaint_rate gets sufficiently bad.
    Returns a dict model_id -> detection_period (or large fallback if none).
    """

    grouped: Dict[str, List[Dict]] = {}
    for row in portfolio:
        grouped.setdefault(row["model_id"], []).append(row)
    for model_id in grouped:
        grouped[model_id].sort(key=lambda r: r["period"])

    detections: Dict[str, int] = {}
    for model_id, series in grouped.items():
        det = 10 ** 9
        for r in series:
            if r["default_rate"] > 0.05 or r["complaint_rate_per_10k_customers"] > 10.0:
                det = r["period"]
                break
        detections[model_id] = det
    return detections


def _compute_treatment_detection_times(
    flags: List[Dict],
) -> Dict[str, int]:
    """Detection times when AI-specific metrics trigger amber/red actions."""

    grouped: Dict[str, List[Dict]] = {}
    for f in flags:
        grouped.setdefault(f["model_id"], []).append(f)
    for model_id in grouped:
        grouped[model_id].sort(key=lambda r: r["period"])

    detections: Dict[str, int] = {}
    for model_id, series in grouped.items():
        det = 10 ** 9
        for f in series:
            if f["risk_band"] in ("amber", "red"):
                det = f["period"]
                break
        detections[model_id] = det
    return detections


def run_evaluation(
    portfolio: List[Dict],
    baseline_metrics: List[Dict],
    treatment_metrics: Optional[List[Dict]] = None,
    apply_governance_fn: Optional[Callable[[List[Dict]], Dict[str, List[Dict]]]] = None,
) -> Dict:
    """Evaluate lead times qualitatively (not exported as numeric evidence).

    Returns an internal dictionary with baseline vs treatment detection times
    per model. This is used to check that the pipeline behaves sensibly but
    is intentionally not written into the minimal results.json metrics.
    """

    baseline_detection = _compute_baseline_detection_times(portfolio)

    treatment_detection: Dict[str, int] = {}
    trigger_log: List[Dict] = []

    if treatment_metrics is not None and apply_governance_fn is not None:
        gov = apply_governance_fn(treatment_metrics)
        flags = gov["per_model_flags"]
        trigger_log = gov["trigger_log"]
        treatment_detection = _compute_treatment_detection_times(flags)

    evaluation = {
        "baseline_detection": baseline_detection,
        "treatment_detection": treatment_detection,
        "trigger_log": trigger_log,
    }
    return evaluation
