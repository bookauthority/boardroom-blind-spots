from __future__ import annotations

from typing import Dict, List


def apply_scenarios(rows: List[Dict]) -> List[Dict]:
    """Inject structural patterns for drift, fairness shift, and correlation.

    This function operates deterministically on the input list and returns a
    modified list with embedded scenarios:

    - Scenario A: gradual drift in default_rate and approval_rate for
      `retail_credit_scoring` beginning around period 8.
    - Scenario B: fairness deterioration in `sme_credit_scoring` beginning
      around period 10 (group B approval worsens).
    - Scenario C: output correlation spike between `market_making_agent` and
      `algo_execution_router` beginning around period 12.
    """

    # Build index by model_id and period for in-place adjustments
    index: Dict[tuple, Dict] = {}
    for row in rows:
        key = (row["model_id"], row["period"])
        index[key] = row

    # Scenario A: gradual drift for retail_credit_scoring
    for (mid, period), row in index.items():
        if mid == "retail_credit_scoring" and period >= 8:
            # Increase default_rate slowly, decrease approval_rate
            drift_factor = (period - 8) / 16.0  # from 0 to 1 by period 24
            row["default_rate"] = row["default_rate"] * (1.0 + 1.5 * drift_factor)
            row["approval_rate"] = max(0.01, row["approval_rate"] * (1.0 - 0.4 * drift_factor))

    # Scenario B: fairness deterioration for sme_credit_scoring
    for (mid, period), row in index.items():
        if mid == "sme_credit_scoring" and period >= 10:
            fairness_factor = (period - 10) / 14.0
            # Group B approval worsens relative to group A
            row["group_b_approval"] = max(
                0.01,
                row["group_b_approval"] * (1.0 - 0.5 * fairness_factor),
            )
            row["group_a_approval"] = min(
                0.99,
                row["group_a_approval"] * (1.0 + 0.1 * fairness_factor),
            )

    # Scenario C: correlation spike between market_making_agent and algo_execution_router
    for period in range(max(r["period"] for r in rows) + 1):
        if period < 12:
            continue
        # Align approval_rate and pnl_contribution patterns more closely
        mma = index.get(("market_making_agent", period))
        aer = index.get(("algo_execution_router", period))
        if mma and aer:
            # Set algo_execution_router metrics closer to market_making_agent
            aer["approval_rate"] = 0.7 * aer["approval_rate"] + 0.3 * mma["approval_rate"]
            aer["pnl_contribution"] = 0.7 * aer["pnl_contribution"] + 0.3 * mma["pnl_contribution"]

    return rows
