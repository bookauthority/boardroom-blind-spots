from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Dict, List, Sequence

from .model import (
    batch_approve,
    batch_prob_approve,
    champion_model,
    corrupted_model,
)
from .metrics import (
    approval_rate,
    average_feature_vector,
    disagreement_rate,
    l1_distance,
)


@dataclass
class SyntheticApplication:
    features: Sequence[float]


def generate_synthetic_applications(n: int, seed: int) -> List[SyntheticApplication]:
    """Generate deterministic synthetic credit applications.

    Feature semantics (rough):
    - income_scaled: uniform in [0.0, 1.0]
    - debt_to_income: uniform in [0.0, 1.0]
    - credit_utilization: uniform in [0.0, 1.0]
    """

    rng = random.Random(seed)
    apps: List[SyntheticApplication] = []
    for _ in range(n):
        income_scaled = rng.uniform(0.0, 1.0)
        debt_to_income = rng.uniform(0.0, 1.0)
        credit_utilization = rng.uniform(0.0, 1.0)
        apps.append(
            SyntheticApplication(
                features=[income_scaled, debt_to_income, credit_utilization]
            )
        )
    return apps


def _base_seed_for_workload(workload_id: str) -> int:
    # Simple deterministic mapping from workload_id to base seed.
    return abs(hash(workload_id)) % (2**31)


def _seed_for_variant(workload_id: str, variant: str) -> int:
    # Ensure baseline and treatment see identical data by construction:
    # both map to the same derived seed from the workload_id alone.
    del variant  # not used intentionally
    return _base_seed_for_workload(workload_id)


def run_wl1_normal_operations(variant: str) -> Dict:
    """Simulate WL1_normal_operations.

    Both baseline and treatment generate an identical synthetic batch and
    evaluate approval rate. Treatment additionally computes a simple input
    drift magnitude metric between the first and second half of the batch
    to emulate AI-specific early warning metrics.
    """

    workload_id = "WL1_normal_operations"
    run_id = f"{workload_id}-{variant}"

    seed = _seed_for_variant(workload_id, variant)
    n_samples = 400
    applications = generate_synthetic_applications(n_samples, seed)
    model = champion_model()

    features = [app.features for app in applications]
    approvals = batch_approve(model, features)
    probs = batch_prob_approve(model, features)

    metrics: Dict[str, float] = {}
    metrics["approval_rate"] = float(approval_rate(approvals))
    metrics["avg_approval_probability"] = float(sum(probs) / len(probs))

    # Treatment has an additional metric that approximates input drift between
    # first and second half of the batch.
    if variant == "treatment":
        mid = n_samples // 2
        first_half = features[:mid]
        second_half = features[mid:]
        avg_first = average_feature_vector(first_half)
        avg_second = average_feature_vector(second_half)
        drift_mag = l1_distance(avg_first, avg_second)
        metrics["drift_magnitude"] = float(drift_mag)

    success = True

    return {
        "variant": variant,
        "workload_id": workload_id,
        "run_id": run_id,
        "success": success,
        "metrics": metrics,
    }


def run_wl3_abrupt_model_corruption(variant: str) -> Dict:
    """Simulate WL3_abrupt_model_corruption.

    We model a sudden corruption at halfway point in the request stream:
    - First half scored with champion model.
    - Second half scored with corrupted model.

    Baseline only observes approval rates before and after corruption.
    Treatment additionally computes a disagreement rate between the champion
    and corrupted models on the post-corruption segment, which emulates
    AI-specific meta-monitoring.
    """

    workload_id = "WL3_abrupt_model_corruption"
    run_id = f"{workload_id}-{variant}"

    seed = _seed_for_variant(workload_id, variant)
    n_samples = 400
    applications = generate_synthetic_applications(n_samples, seed)
    features = [app.features for app in applications]

    champ = champion_model()
    corrupt = corrupted_model()

    mid = n_samples // 2
    first_half = features[:mid]
    second_half = features[mid:]

    approvals_first = batch_approve(champ, first_half)
    approvals_second_champ = batch_approve(champ, second_half)
    approvals_second_corrupt = batch_approve(corrupt, second_half)

    approvals_full_baseline = approvals_first + approvals_second_corrupt
    overall_approval_rate = approval_rate(approvals_full_baseline)
    post_corruption_approval = approval_rate(approvals_second_corrupt)

    metrics: Dict[str, float] = {
        "overall_approval_rate": float(overall_approval_rate),
        "post_corruption_approval_rate": float(post_corruption_approval),
    }

    if variant == "treatment":
        # AI-aware meta-monitoring: compare champion vs corrupted outputs
        # for the second half to emulate champion-shadow disagreement.
        disagree = disagreement_rate(approvals_second_champ, approvals_second_corrupt)
        metrics["disagreement_rate"] = float(disagree)

    success = True

    return {
        "variant": variant,
        "workload_id": workload_id,
        "run_id": run_id,
        "success": success,
        "metrics": metrics,
    }
