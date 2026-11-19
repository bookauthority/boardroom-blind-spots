from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

from .model import ModelInput

Decision = Literal["approve", "manual_review", "decline"]


@dataclass
class RiskAppetite:
    """Simple centralised risk appetite configuration.

    Values here are intentionally fixed for reproducibility. In a real
    implementation they would be read from versioned policy files.
    """

    max_auto_approve_risk: float = 0.25
    max_auto_review_risk: float = 0.6


RISK_APPETITE = RiskAppetite()


def action_engine_decision_from_risk(score: float, appetite: RiskAppetite) -> Decision:
    """Map a risk score into a decision for the action engine.

    Baseline and treatment both use this mapping, but in treatment additional
    guardrails may override or escalate.
    """

    if score <= appetite.max_auto_approve_risk:
        return "approve"
    if score <= appetite.max_auto_review_risk:
        return "manual_review"
    return "decline"


def is_policy_unsafe(features: ModelInput, decision: Decision, risk_score: float) -> bool:
    """Ex-post safety/policy evaluation for metrics.

    This is a simplified check:
      * High risk transactions that are approved are unsafe.
      * Medium risk transactions for very new customers may be unsafe.
      * Very high amounts with anything but decline are unsafe.
    """

    # Unsafe if huge amount and not decline
    if features.amount >= 20000 and decision != "decline":
        return True

    # Unsafe if risk is very high but not declined
    if risk_score >= 0.8 and decision != "decline":
        return True

    # Medium-high risk for new customers should be at least manual review
    if features.is_new_customer and risk_score >= 0.5 and decision == "approve":
        return True

    return False
