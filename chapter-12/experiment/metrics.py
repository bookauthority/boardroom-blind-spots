from __future__ import annotations

import math
from typing import List, Dict, Tuple


def auc_roc(y_true: List[int], y_score: List[float]) -> float:
    """Compute AUC ROC using the trapezoidal rule.

    This implementation assumes binary labels {0,1} and finite scores.
    """

    assert len(y_true) == len(y_score)
    n = len(y_true)
    # sort by score descending
    paired = sorted(zip(y_score, y_true), key=lambda x: x[0], reverse=True)
    P = sum(1 for _, y in paired if y == 1)
    N = n - P
    if P == 0 or N == 0:
        return 0.5

    tp = 0.0
    fp = 0.0
    prev_score = None
    tpr_fpr: List[Tuple[float, float]] = []

    for score, label in paired:
        if prev_score is None or score != prev_score:
            tpr = tp / P
            fpr = fp / N
            tpr_fpr.append((tpr, fpr))
            prev_score = score
        if label == 1:
            tp += 1.0
        else:
            fp += 1.0
    tpr = tp / P
    fpr = fp / N
    tpr_fpr.append((tpr, fpr))

    # sort by FPR ascending
    tpr_fpr.sort(key=lambda x: x[1])
    auc = 0.0
    prev_fpr = 0.0
    prev_tpr = 0.0
    for tpr, fpr in tpr_fpr:
        auc += (fpr - prev_fpr) * (tpr + prev_tpr) / 2.0
        prev_fpr = fpr
        prev_tpr = tpr
    return max(0.0, min(1.0, auc))


def accuracy(y_true: List[int], y_pred: List[int]) -> float:
    assert len(y_true) == len(y_pred)
    if not y_true:
        return 0.0
    correct = sum(1 for yt, yp in zip(y_true, y_pred) if yt == yp)
    return correct / len(y_true)


def psi(expected: List[float], actual: List[float], n_bins: int = 10) -> float:
    """Compute a simple Population Stability Index between two numeric lists.

    Both lists are binned using the expected distribution quantiles.
    """

    if not expected or not actual:
        return 0.0
    sorted_exp = sorted(expected)
    # compute bin edges on expected
    edges = [sorted_exp[int(len(sorted_exp) * b / n_bins)] for b in range(n_bins)]
    edges.append(sorted_exp[-1] + 1e-9)

    def counts(values: List[float]) -> List[int]:
        c = [0 for _ in range(n_bins)]
        for v in values:
            for i in range(n_bins):
                if v <= edges[i + 1]:
                    c[i] += 1
                    break
        return c

    exp_counts = counts(expected)
    act_counts = counts(actual)
    total_exp = float(len(expected))
    total_act = float(len(actual))
    psi_val = 0.0
    for e, a in zip(exp_counts, act_counts):
        pe = max(e / total_exp, 1e-6)
        pa = max(a / total_act, 1e-6)
        psi_val += (pa - pe) * math.log(pa / pe)
    return psi_val


def decision_volatility_rate(
    base_probs: List[float],
    perturbed_probs: List[float],
    threshold: float = 0.5,
) -> float:
    """Compute fraction of instances where decision flips under perturbation."""

    assert len(base_probs) == len(perturbed_probs)
    if not base_probs:
        return 0.0
    flips = 0
    for p0, p1 in zip(base_probs, perturbed_probs):
        d0 = 1 if p0 >= threshold else 0
        d1 = 1 if p1 >= threshold else 0
        if d0 != d1:
            flips += 1
    return flips / len(base_probs)


def monotonicity_violation_rate(
    x_values: List[float],
    probs: List[float],
    expectation: str = "increasing",
) -> float:
    """Given a trajectory of a single feature and predictions, compute violation rate.

    expectation: "increasing" or "decreasing".
    Returns fraction of consecutive pairs that violate the expectation.
    """

    assert len(x_values) == len(probs)
    if len(x_values) < 2:
        return 0.0
    violations = 0
    total_pairs = 0
    for i in range(1, len(x_values)):
        x_prev, x_curr = x_values[i - 1], x_values[i]
        p_prev, p_curr = probs[i - 1], probs[i]
        if expectation == "increasing" and x_curr > x_prev and p_curr < p_prev:
            violations += 1
        elif expectation == "decreasing" and x_curr > x_prev and p_curr > p_prev:
            violations += 1
        total_pairs += 1
    if total_pairs == 0:
        return 0.0
    return violations / total_pairs


def adversarial_vulnerability_rate(failures: int, attempts: int) -> float:
    if attempts <= 0:
        return 0.0
    return failures / attempts


def fairness_group_metrics(
    decisions: List[int], groups: List[int]
) -> Dict[str, float]:
    """Compute simple group-level fairness metrics using decisions and group labels.

    Returns:
      - fairness_dp_difference: abs difference in approval rate between group 0 and 1
      - disparate_impact_ratio: min(p0, p1) / max(p0, p1) (0 if one group has 0 approvals)
    """

    assert len(decisions) == len(groups)
    if not decisions:
        return {"fairness_dp_difference": 0.0, "disparate_impact_ratio": 1.0}

    counts = {0: {"total": 0, "approved": 0}, 1: {"total": 0, "approved": 0}}
    for d, g in zip(decisions, groups):
        if g not in counts:
            counts[g] = {"total": 0, "approved": 0}
        counts[g]["total"] += 1
        if d == 1:
            counts[g]["approved"] += 1

    rates: Dict[int, float] = {}
    for g, stat in counts.items():
        if stat["total"] == 0:
            rates[g] = 0.0
        else:
            rates[g] = stat["approved"] / stat["total"]

    p0 = rates.get(0, 0.0)
    p1 = rates.get(1, 0.0)
    dp = abs(p0 - p1)
    mx = max(p0, p1)
    mn = min(p0, p1)
    if mx == 0.0:
        di = 0.0
    else:
        di = mn / mx
    return {
        "fairness_dp_difference": dp,
        "disparate_impact_ratio": di,
    }
