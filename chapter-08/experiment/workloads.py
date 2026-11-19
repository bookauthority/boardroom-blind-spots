from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Generator, Iterable, List, Tuple

from .model import ModelInput


@dataclass
class WorkloadConfig:
    name: str
    n_requests: int


def _base_sample(rng: random.Random) -> ModelInput:
    amount = rng.uniform(10, 15000)
    age = rng.randint(21, 75)
    tenure = rng.uniform(0, 15)
    is_new = tenure < 1.0
    geo_risk = rng.uniform(0.0, 0.6)
    channel_risk = rng.uniform(0.0, 0.6)
    return ModelInput(
        amount=amount,
        customer_age=age,
        customer_tenure_years=tenure,
        is_new_customer=is_new,
        geo_risk=geo_risk,
        channel_risk=channel_risk,
    )


def workload_WL1(rng: random.Random, n: int) -> Iterable[ModelInput]:
    for _ in range(n):
        yield _base_sample(rng)


def workload_WL2(rng: random.Random, n: int) -> Iterable[ModelInput]:
    for i in range(n):
        base = _base_sample(rng)
        # Gradual drift: increase amount and geo_risk over time
        drift_factor = i / max(n - 1, 1)
        base.amount *= 1.0 + 0.2 * drift_factor
        base.geo_risk = min(1.0, base.geo_risk + 0.3 * drift_factor)
        yield base


def workload_WL3(rng: random.Random, n: int) -> Iterable[ModelInput]:
    for i in range(n):
        base = _base_sample(rng)
        # Inject some high-risk policy-violating patterns
        if i % 10 == 0:
            base.amount = rng.uniform(20000, 50000)
            base.geo_risk = 1.0
            base.channel_risk = 1.0
        yield base


def workload_WL4(rng: random.Random, n: int) -> Iterable[ModelInput]:
    # First third calm, next third shock, final third aftermath
    shock_start = n // 3
    shock_end = 2 * n // 3
    for i in range(n):
        base = _base_sample(rng)
        if shock_start <= i < shock_end:
            base.amount = rng.uniform(5000, 30000)
            base.geo_risk = rng.uniform(0.6, 1.0)
            base.channel_risk = rng.uniform(0.6, 1.0)
        elif i >= shock_end:
            base.amount *= 1.2
            base.geo_risk = min(1.0, base.geo_risk + 0.2)
        yield base


def workload_WL5(rng: random.Random, n: int) -> Iterable[ModelInput]:
    # Mostly normal, with a small fraction of obviously unsafe cases
    for i in range(n):
        base = _base_sample(rng)
        if i % 50 == 0:
            base.amount = rng.uniform(30000, 60000)
            base.geo_risk = 1.0
            base.channel_risk = 1.0
        yield base


WORKLOAD_GENERATORS = {
    "WL1_normal_traffic": workload_WL1,
    "WL2_data_drift_and_model_stress": workload_WL2,
    "WL3_policy_violation_and_misuse_attempts": workload_WL3,
    "WL4_adverse_event_and_feedback_loop_spike": workload_WL4,
    "WL5_kill_switch_operational_test": workload_WL5,
}


def generate_workload(name: str, seed: int, n_requests: int) -> Tuple[List[ModelInput], int]:
    if name not in WORKLOAD_GENERATORS:
        raise ValueError(f"Unknown workload: {name}")
    rng = random.Random(seed)
    gen = WORKLOAD_GENERATORS[name]
    return list(gen(rng, n_requests)), seed
