from __future__ import annotations

import math
from dataclasses import dataclass
from typing import List, Sequence


@dataclass
class LinearCreditModel:
    """Deterministic linear model for credit approval.

    This is intentionally simple: a fixed-weight linear score over features,
    followed by a logistic transform to obtain an approval probability.
    """

    coefficients: Sequence[float]
    bias: float

    def score(self, features: Sequence[float]) -> float:
        if len(features) != len(self.coefficients):
            raise ValueError("Feature length and coefficient length must match")
        s = self.bias
        for w, x in zip(self.coefficients, features):
            s += w * x
        return s

    def prob_approve(self, features: Sequence[float]) -> float:
        s = self.score(features)
        # logistic
        return 1.0 / (1.0 + math.exp(-s))

    def approve(self, features: Sequence[float]) -> int:
        return 1 if self.prob_approve(features) >= 0.5 else 0


def champion_model() -> LinearCreditModel:
    """Return a fixed, well-behaved model.

    Coefficients are chosen to produce reasonable variation in approvals.
    """

    # income (scaled), debt_to_income, credit_utilization
    return LinearCreditModel(coefficients=[1.5, -2.0, -1.0], bias=0.0)


def corrupted_model() -> LinearCreditModel:
    """Return a deliberately degraded/corrupted model.

    We flip some coefficient signs and alter magnitudes to simulate
    catastrophic degradation while remaining deterministic.
    """

    return LinearCreditModel(coefficients=[-0.5, 0.5, 0.2], bias=0.0)


def batch_approve(model: LinearCreditModel, X: List[Sequence[float]]) -> List[int]:
    return [model.approve(x) for x in X]


def batch_prob_approve(model: LinearCreditModel, X: List[Sequence[float]]) -> List[float]:
    return [model.prob_approve(x) for x in X]
