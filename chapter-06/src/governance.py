from __future__ import annotations

from typing import Dict, List, Optional

from .config import get_governance_thresholds


def _band_from_thresholds(value: float, thresholds: Dict[str, float]) -> str:
    """Return risk band (green/amber/red) given a metric value and thresholds.

    For a metric like drift, thresholds is expected to have keys:
    - "green": upper bound for green band
    - "amber": upper bound for amber band
    Values above `amber` are treated as red.
    """

    if value <= thresholds["green"]:
        return "green"
    if value <= thresholds["amber"]:
        return "amber"
    return "red"


def apply_governance(
    treatment_metrics: List[Dict],
) -> Dict[str, List[Dict]]:
    """Apply simple rule-based governance to treatment metrics.

    Returns a dict with keys:
    - "per_model_flags": list of {model_id, period, risk_band, triggered_actions}
    - "trigger_log": list of {model_id, period, trigger_type, severity}
    """

    thresholds = get_governance_thresholds()
    per_model_flags: List[Dict] = []
    trigger_log: List[Dict] = []

    for row in treatment_metrics:
        model_id = row["model_id"]
        period = row["period"]
        tier = row["criticality_tier"]
        drift = float(row["prediction_drift_score"])
        fairness_gap = float(row["fairness_gap"])
        auto_share = float(row["auto_decision_share_pct"])

        drift_band = _band_from_thresholds(drift, thresholds["drift_score"])
        fairness_band = _band_from_thresholds(fairness_gap, thresholds["fairness_gap"])

        # Auto-decision thresholds only meaningful for Tier 1
        if tier == 1:
            if auto_share <= thresholds["auto_decision_share_pct_tier1"]["green"]:
                auto_band = "green"
            elif auto_share <= thresholds["auto_decision_share_pct_tier1"]["amber"]:
                auto_band = "amber"
            else:
                auto_band = "red"
        else:
            auto_band = "green"

        # Determine most severe band
        bands = [drift_band, fairness_band, auto_band]
        if "red" in bands:
            overall_band = "red"
        elif "amber" in bands:
            overall_band = "amber"
        else:
            overall_band = "green"

        actions: List[str] = []
        if overall_band == "red":
            actions.append("heightened_monitoring")
            if tier == 1:
                actions.append("mandatory_management_review")
        elif overall_band == "amber":
            actions.append("increased_sampling")

        per_model_flags.append(
            {
                "model_id": model_id,
                "period": period,
                "risk_band": overall_band,
                "triggered_actions": actions,
            }
        )

        if overall_band in ("amber", "red"):
            trigger_log.append(
                {
                    "model_id": model_id,
                    "period": period,
                    "trigger_type": "ai_risk_metric_breach",
                    "severity": overall_band,
                }
            )

    return {"per_model_flags": per_model_flags, "trigger_log": trigger_log}
