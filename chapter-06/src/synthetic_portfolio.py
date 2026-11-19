from __future__ import annotations

import math
import random
from typing import Dict, List

from .config import get_portfolio_config
from .scenarios import apply_scenarios


def _base_random(seed: int) -> random.Random:
    r = random.Random()
    r.seed(seed)
    return r


def generate_portfolio() -> List[Dict]:
    """Generate a synthetic AI model portfolio time-series dataset.

    Returns a list of rows; each row is a dict with keys including:
    - model_id, period (int)
    - metadata: business_line, product_type, model_type, criticality_tier
    - business metrics: volume, approval_rate, default_rate, pnl, complaints
    - autonomy metrics: auto_decision_share_pct, override_rate, escalation_rate
    - simple feature proxies for group A/B to support fairness metrics

    The function is deterministic given the embedded seed.
    """

    cfg = get_portfolio_config()
    r = _base_random(cfg["random_seed"])
    models = cfg["models"]
    n_periods = cfg["n_periods"]

    rows: List[Dict] = []

    for m in models:
        model_id = m["model_id"]
        base_volume = 10_000 if m["criticality_tier"] == 1 else 5_000
        base_approval = 0.6 if "credit" in model_id else 0.8
        base_default = 0.02 if "credit" in model_id else 0.0
        base_pnl = 1.0 if m["business_line"] == "Markets" else 0.2
        base_complaints = 5.0

        for t in range(n_periods):
            # Seasonal component to introduce some structure
            season = 0.05 * math.sin(2 * math.pi * t / 12.0)

            volume = int(base_volume * (1.0 + 0.1 * season) * (0.9 + 0.2 * r.random()))
            approval_rate = min(
                0.99,
                max(0.01, base_approval + 0.05 * season + 0.02 * (r.random() - 0.5)),
            )

            default_rate = base_default
            if "credit_scoring" in model_id:
                default_rate = max(
                    0.001,
                    base_default + 0.01 * season + 0.01 * (r.random() - 0.5),
                )

            pnl_contribution = base_pnl * (1.0 + 0.5 * season) * (0.8 + 0.4 * r.random())

            complaint_rate_per_10k_customers = max(
                0.0,
                base_complaints
                * (1.0 + 0.2 * (r.random() - 0.5))
                * (1.0 - 0.3 * season),
            )

            auto_share = m["auto_decision_share_pct"]
            # allow gradual growth in auto-decision share
            auto_share = min(100.0, auto_share + t * 0.5)
            override_rate = max(0.0, 10.0 - 0.2 * t + 5.0 * (r.random() - 0.5))
            escalation_rate = max(0.0, 3.0 + 3.0 * (r.random() - 0.5))

            # fairness feature proxies: group A vs B approval tendencies
            group_a_share = 0.6 + 0.1 * (r.random() - 0.5)
            group_b_share = 1.0 - group_a_share
            group_a_approval = approval_rate + 0.02 * (r.random() - 0.5)
            group_b_approval = approval_rate + 0.02 * (r.random() - 0.5)

            # simple numeric input feature distributions
            feature_mean = 0.0 + 0.3 * season
            feature_std = 1.0

            row = {
                "model_id": model_id,
                "period": t,
                "business_line": m["business_line"],
                "product_type": m["product_type"],
                "model_type": m["model_type"],
                "criticality_tier": m["criticality_tier"],
                "volume": volume,
                "approval_rate": approval_rate,
                "default_rate": default_rate,
                "fraud_detected_rate": 0.02 if "fraud" in model_id else 0.0,
                "pnl_contribution": pnl_contribution,
                "complaint_rate_per_10k_customers": complaint_rate_per_10k_customers,
                "auto_decision_share_pct": auto_share,
                "override_rate_by_humans": override_rate,
                "escalation_rate_to_humans": escalation_rate,
                "group_a_share": group_a_share,
                "group_b_share": group_b_share,
                "group_a_approval": group_a_approval,
                "group_b_approval": group_b_approval,
                "feature_mean": feature_mean,
                "feature_std": feature_std,
            }
            rows.append(row)

    # Inject structured scenarios (drift, fairness shift, correlation spike)
    rows = apply_scenarios(rows)
    return rows
