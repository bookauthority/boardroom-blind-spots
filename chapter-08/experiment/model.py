from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Dict


@dataclass
class ModelInput:
    """Simple representation of a financial transaction or application.

    Fields are deliberately minimal but sufficient to drive different risk
    levels under different workloads.
    """

    amount: float
    customer_age: int
    customer_tenure_years: float
    is_new_customer: bool
    geo_risk: float  # 0 (low) .. 1 (high)
    channel_risk: float  # 0 (low) .. 1 (high)


class SimpleRiskModel:
    """Deterministic toy risk model.

    Produces a risk score between 0 and 1. Higher is riskier.
    """

    def predict_risk(self, features: ModelInput) -> float:
        # Basic linear combination with some nonlinearity
        amt_component = min(features.amount / 10000.0, 5.0)
        tenure_component = -0.3 * min(features.customer_tenure_years, 20.0)
        age_component = -0.01 * max(min(features.customer_age, 90), 18)
        geo_component = 2.0 * features.geo_risk
        channel_component = 1.5 * features.channel_risk
        new_cust_component = 1.0 if features.is_new_customer else -0.2

        raw_score = (
            0.6 * amt_component
            + 0.4 * geo_component
            + 0.3 * channel_component
            + 0.2 * new_cust_component
            + 0.1 * tenure_component
            + 0.1 * age_component
        )

        # Squash to 0..1 with logistic
        score = 1.0 / (1.0 + math.exp(-raw_score))
        return float(score)


def input_from_dict(d: Dict[str, float | int | bool]) -> ModelInput:
    return ModelInput(
        amount=float(d["amount"]),
        customer_age=int(d["customer_age"]),
        customer_tenure_years=float(d["customer_tenure_years"]),
        is_new_customer=bool(d["is_new_customer"]),
        geo_risk=float(d["geo_risk"]),
        channel_risk=float(d["channel_risk"]),
    )
