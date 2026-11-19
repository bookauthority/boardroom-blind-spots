from __future__ import annotations

from typing import Iterable, Sequence


def mean(values: Iterable[float]) -> float:
    total = 0.0
    count = 0
    for v in values:
        total += float(v)
        count += 1
    if count == 0:
        return 0.0
    return total / count


def approval_rate(approvals: Sequence[int]) -> float:
    if not approvals:
        return 0.0
    return mean(approvals)


def average_feature_vector(samples: Sequence[Sequence[float]]) -> Sequence[float]:
    if not samples:
        return []
    dim = len(samples[0])
    sums = [0.0] * dim
    for s in samples:
        for i, v in enumerate(s):
            sums[i] += float(v)
    n = float(len(samples))
    return [s / n for s in sums]


def l1_distance(a: Sequence[float], b: Sequence[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Vectors must have same length for L1 distance")
    return float(sum(abs(x - y) for x, y in zip(a, b)))


def disagreement_rate(a: Sequence[int], b: Sequence[int]) -> float:
    if len(a) != len(b) or not a:
        return 0.0
    disagreements = sum(1 for x, y in zip(a, b) if x != y)
    return disagreements / float(len(a))
