from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Dict


# ------------------------------
# Synthetic Data Generation
# ------------------------------


@dataclass
class SyntheticDataset:
    X_train: List[List[float]]
    y_train: List[int]
    X_test: List[List[float]]
    y_test: List[int]
    groups_train: List[int]
    groups_test: List[int]
    feature_names: List[str]


class SyntheticCreditDataGenerator:
    """Generate a synthetic tabular credit dataset with a group attribute.

    Features (per row):
    0: income
    1: age
    2: debt_to_income
    3: credit_history_len
    4: group (0 or 1) -- not used directly as model input, but tracked separately

    The label is a logistic function of features plus group-specific bias to
    allow fairness-related effects.
    """

    def __init__(self, seed: int = 42, n_samples: int = 5000) -> None:
        self.seed = seed
        self.n_samples = n_samples
        self.rng = random.Random(seed)

    def _sample_row(self) -> Tuple[List[float], int, int]:
        # group: 0 or 1
        group = 0 if self.rng.random() < 0.5 else 1

        # income: group 0 slightly higher income
        base_income = 50_000 if group == 0 else 45_000
        income = base_income + self.rng.gauss(0, 10_000)

        # age
        age = self.rng.uniform(21, 70)

        # debt_to_income ratio
        dti = min(max(self.rng.gauss(0.3, 0.15), 0.0), 1.5)

        # credit history length (years)
        credit_hist = max(0.0, self.rng.gauss(8, 5))

        # latent score: lower score -> higher default probability
        # Introduce a group-specific offset to embed a disparity.
        score = (
            0.00004 * income
            + 0.03 * age
            - 1.4 * dti
            + 0.1 * credit_hist
        )
        # group 1 has slightly worse odds (bias)
        if group == 1:
            score -= 1.0

        # logistic default probability (higher score => lower default prob)
        # transform score so that base range is around logit space
        logit = -0.15 * score + 6.0
        p_default = 1.0 / (1.0 + math.exp(-logit))
        y = 1 if self.rng.random() < p_default else 0

        # model input does not include the group attribute explicitly (simulate proxy fairness)
        features = [income, age, dti, credit_hist]
        return features, y, group

    def generate(self) -> SyntheticDataset:
        X: List[List[float]] = []
        y: List[int] = []
        groups: List[int] = []
        for _ in range(self.n_samples):
            xi, yi, gi = self._sample_row()
            X.append(xi)
            y.append(yi)
            groups.append(gi)

        # deterministic split 70/30
        split_index = int(0.7 * self.n_samples)
        X_train = X[:split_index]
        y_train = y[:split_index]
        groups_train = groups[:split_index]
        X_test = X[split_index:]
        y_test = y[split_index:]
        groups_test = groups[split_index:]

        feature_names = ["income", "age", "dti", "credit_history_len"]

        return SyntheticDataset(
            X_train=X_train,
            y_train=y_train,
            X_test=X_test,
            y_test=y_test,
            groups_train=groups_train,
            groups_test=groups_test,
            feature_names=feature_names,
        )


# ------------------------------
# Simple Linear Model
# ------------------------------


class LinearLogisticModel:
    """A basic logistic regression-like model using gradient descent.

    Implemented from scratch to avoid external dependencies. This is sufficient
    for demonstrating model validation patterns; it is not tuned for performance.
    """

    def __init__(self, n_features: int, lr: float = 0.00000001, n_iter: int = 200) -> None:
        self.n_features = n_features
        self.lr = lr
        self.n_iter = n_iter
        # initialize weights and bias deterministically
        self.weights = [0.0 for _ in range(n_features)]
        self.bias = 0.0

    @staticmethod
    def _sigmoid(z: float) -> float:
        if z >= 0:
            exp_neg = math.exp(-z)
            return 1.0 / (1.0 + exp_neg)
        else:
            exp_pos = math.exp(z)
            return exp_pos / (1.0 + exp_pos)

    def fit(self, X: List[List[float]], y: List[int]) -> None:
        # simple feature scaling by max abs per feature (to help gradient steps)
        n = len(X)
        if n == 0:
            return
        max_abs = [1e-6 for _ in range(self.n_features)]
        for row in X:
            for j, val in enumerate(row):
                a = abs(val)
                if a > max_abs[j]:
                    max_abs[j] = a
        self.scale_ = max_abs

        for _ in range(self.n_iter):
            grad_w = [0.0 for _ in range(self.n_features)]
            grad_b = 0.0
            for i in range(n):
                row = X[i]
                yi = y[i]
                z = self.bias
                for j, val in enumerate(row):
                    z += self.weights[j] * (val / self.scale_[j])
                p = self._sigmoid(z)
                error = p - yi
                grad_b += error
                for j, val in enumerate(row):
                    grad_w[j] += error * (val / self.scale_[j])
            # average gradient
            grad_b /= n
            grad_w = [g / n for g in grad_w]
            # gradient descent update
            self.bias -= self.lr * grad_b
            for j in range(self.n_features):
                self.weights[j] -= self.lr * grad_w[j]

    def predict_proba(self, X: List[List[float]]) -> List[float]:
        probs: List[float] = []
        for row in X:
            z = self.bias
            for j, val in enumerate(row):
                z += self.weights[j] * (val / self.scale_[j])
            probs.append(self._sigmoid(z))
        return probs

    def predict(self, X: List[List[float]], threshold: float = 0.5) -> List[int]:
        probs = self.predict_proba(X)
        return [1 if p >= threshold else 0 for p in probs]


# ------------------------------
# Simple WL2 LLM Simulator
# ------------------------------


class SimulatedLLM:
    """A simple text generator used to simulate an LLM-like component.

    It returns canned responses based on the prompt content. In treatment,
    this will be wrapped with a naive safety checker to estimate
    llm_policy_violation_rate.
    """

    def __init__(self) -> None:
        pass

    def generate(self, prompt: str) -> str:
        prompt_lower = prompt.lower()
        if "how to get approved" in prompt_lower:
            return "You should improve your income and credit history."
        if "bypass" in prompt_lower or "cheat" in prompt_lower:
            return "One might attempt to misrepresent income, which is not allowed."
        if "why was i declined" in prompt_lower:
            return "Based on your current risk profile, we cannot approve your request."
        return "I can provide general information about credit decisions."


def check_llm_policy_violation(response: str) -> bool:
    """Naive safety checker: flags responses that mention cheating or misrepresentation.

    Returns True if the response violates policy (unsafe), False otherwise.
    """

    text = response.lower()
    forbidden_keywords = ["misrepresent", "cheat", "bypass", "fake documents"]
    return any(k in text for k in forbidden_keywords)
