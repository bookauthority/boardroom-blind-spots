from __future__ import annotations

from typing import Dict, List, Tuple


def _group_by_model(rows: List[Dict]) -> Dict[str, List[Dict]]:
    grouped: Dict[str, List[Dict]] = {}
    for row in rows:
        grouped.setdefault(row["model_id"], []).append(row)
    # Ensure sorted by period
    for model_id in grouped:
        grouped[model_id].sort(key=lambda r: r["period"])
    return grouped


def compute_baseline_metrics(rows: List[Dict]) -> Tuple[List[Dict], Dict]:
    """Compute baseline KPIs for each row.

    Returns (metrics, meta) where metrics is a list of per-model-period
    dicts and meta contains simple aggregate information.
    """

    metrics: List[Dict] = []
    grouped = _group_by_model(rows)

    for model_id, series in grouped.items():
        for row in series:
            m = {
                "model_id": model_id,
                "period": row["period"],
                "criticality_tier": row["criticality_tier"],
                "approval_rate": float(row["approval_rate"]),
                "default_rate": float(row["default_rate"]),
                "fraud_detected_rate": float(row["fraud_detected_rate"]),
                "pnl_contribution": float(row["pnl_contribution"]),
                "complaint_rate_per_10k_customers": float(
                    row["complaint_rate_per_10k_customers"]
                ),
            }
            metrics.append(m)

    meta = {
        "n_models": len(grouped),
        "n_rows": len(metrics),
    }
    return metrics, meta


def compute_treatment_metrics(rows: List[Dict]) -> Tuple[List[Dict], Dict]:
    """Compute AI-specific risk metrics in addition to baseline metrics.

    For simplicity, this function recomputes baseline-like fields and augments
    each record with drift, fairness, autonomy, and a composite risk score.
    """

    grouped = _group_by_model(rows)
    metrics: List[Dict] = []

    for model_id, series in grouped.items():
        # Baseline period for drift calculations: first period
        base = series[0]
        base_approval = float(base["approval_rate"])
        base_feature_mean = float(base["feature_mean"])

        prev_approval = base_approval
        for row in series:
            period = row["period"]

            approval_rate = float(row["approval_rate"])
            feature_mean = float(row["feature_mean"])

            # Simple bounded drift metrics in [0, 1]
            input_drift = min(1.0, abs(feature_mean - base_feature_mean) / 1.0)
            prediction_drift = min(1.0, abs(approval_rate - base_approval) / 0.5)

            # Stability index: 1 - change vs previous period
            if period == 0:
                stability_index = 1.0
            else:
                delta = abs(approval_rate - prev_approval)
                stability_index = max(0.0, 1.0 - min(1.0, delta / 0.2))

            prev_approval = approval_rate

            # Fairness gap: difference in approval between groups A and B in percentage points
            fairness_gap = 100.0 * abs(
                float(row["group_a_approval"]) - float(row["group_b_approval"])
            )

            # Explainability coverage: simple proxy by model type and criticality
            model_type = row["model_type"]
            criticality = row["criticality_tier"]
            if model_type == "gradient_boosting":
                explain_cov = 95.0 if criticality == 1 else 90.0
            elif model_type == "deep_neural_net":
                explain_cov = 80.0 if criticality == 1 else 75.0
            elif model_type == "rl_policy":
                explain_cov = 70.0
            else:  # llm
                explain_cov = 60.0

            auto_share = float(row["auto_decision_share_pct"])
            override_rate = float(row["override_rate_by_humans"])

            # Surprise index: non-stationarity proxy higher for LLM and RL agent
            surprise_index = 0.1
            if model_type == "llm":
                surprise_index = 0.4 + 0.02 * period
            elif model_type == "rl_policy":
                surprise_index = 0.25 + 0.01 * period

            # Composite risk score: basic aggregation of normalized components
            comp = 0.0
            comp += prediction_drift
            comp += input_drift
            comp += min(1.0, fairness_gap / 10.0)
            comp += 1.0 - stability_index
            comp += surprise_index
            comp += max(0.0, (auto_share - 50.0) / 50.0)
            composite_risk_score = min(5.0, comp)

            m = {
                "model_id": model_id,
                "period": period,
                "criticality_tier": criticality,
                # Baseline-like KPIs
                "approval_rate": approval_rate,
                "default_rate": float(row["default_rate"]),
                "fraud_detected_rate": float(row["fraud_detected_rate"]),
                "pnl_contribution": float(row["pnl_contribution"]),
                "complaint_rate_per_10k_customers": float(
                    row["complaint_rate_per_10k_customers"]
                ),
                # AI risk metrics
                "input_data_drift_score": input_drift,
                "prediction_drift_score": prediction_drift,
                "stability_index": stability_index,
                "fairness_gap": fairness_gap,
                "explainability_coverage_pct": explain_cov,
                "auto_decision_share_pct": auto_share,
                "override_rate_by_humans": override_rate,
                "surprise_index": surprise_index,
                "composite_risk_score": composite_risk_score,
            }
            metrics.append(m)

    meta = {
        "n_models": len(grouped),
        "n_rows": len(metrics),
    }
    return metrics, meta
