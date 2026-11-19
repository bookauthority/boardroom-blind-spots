from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Generator

from .config import WorkloadConfig


@dataclass
class RiskSnapshot:
    """Synthetic risk indicators at a given time.

    Attributes:
        minute: Simulation minute.
        generic_severity: Overall severity level in [0, 1], visible to
            both baseline and treatment policies.
        ai_signal_strength: AI-specific anomaly strength in [0, 1]. In
        
            the real world this might represent model drift, correlated
            AI errors, or anomalous outputs.
        rolling_avg_generic: Rolling average of generic severity over a
            short window, used as a proxy for persistence.
    """

    minute: int
    generic_severity: float
    ai_signal_strength: float
    rolling_avg_generic: float


def _generate_profile(duration: int, pattern: str, rng: random.Random) -> list[float]:
    """Generate a simple severity profile.

    Patterns:
        - "slow_ramp": monotonic ramp-up with mild noise.
        - "fast_spike": rapid spike then plateau.
        - "oscillate": oscillating severity with upward drift.
    """

    values: list[float] = []
    for t in range(duration):
        if pattern == "slow_ramp":
            base = t / max(1, duration - 1)
        elif pattern == "fast_spike":
            midpoint = duration / 3
            if t < midpoint:
                base = (t / max(1.0, midpoint)) * 1.0
            else:
                base = 0.85
        elif pattern == "oscillate":
            # Sinusoidal oscillation with slight upward trend
            base = 0.4 + 0.2 * math.sin(t / 3.0) + 0.4 * (t / max(1, duration - 1))
        else:
            base = 0.5
        noise = rng.uniform(-0.05, 0.05)
        value = min(1.0, max(0.0, base + noise))
        values.append(value)
    return values


def generate_signal_stream(workload: WorkloadConfig) -> Generator[RiskSnapshot, None, None]:
    """Yield a deterministic stream of RiskSnapshot objects for a workload.

    The three workloads share structure but differ in chosen patterns for
    generic and AI-specific signals, and in their seeds.
    """

    rng = random.Random(workload.seed)
    duration = workload.duration_minutes

    if workload.workload_id == "W1":  # Credit approvals
        generic_profile = _generate_profile(duration, "slow_ramp", rng)
        ai_profile = _generate_profile(duration, "fast_spike", rng)
    elif workload.workload_id == "W2":  # Trading algo feedback loop
        generic_profile = _generate_profile(duration, "oscillate", rng)
        ai_profile = _generate_profile(duration, "fast_spike", rng)
    elif workload.workload_id == "W3":  # Generative AI misconduct
        generic_profile = _generate_profile(duration, "slow_ramp", rng)
        ai_profile = _generate_profile(duration, "oscillate", rng)
    else:  # Fallback: generic slow ramp
        generic_profile = _generate_profile(duration, "slow_ramp", rng)
        ai_profile = _generate_profile(duration, "slow_ramp", rng)

    window = 5
    for t in range(duration):
        start = max(0, t - window + 1)
        window_vals = generic_profile[start : t + 1]
        rolling_avg = sum(window_vals) / len(window_vals)
        yield RiskSnapshot(
            minute=t,
            generic_severity=generic_profile[t],
            ai_signal_strength=ai_profile[t],
            rolling_avg_generic=rolling_avg,
        )


# Workload factories -------------------------------------------------------


def make_workload_w1() -> WorkloadConfig:
    """Retail/SME credit approval spiral.

    - synthetic_portfolio_size: 100000 (conceptual, not used directly here)
    - incident_seed: 42
    - time_horizon_minutes: 120
    """

    return WorkloadConfig(
        workload_id="W1",
        name="W1-credit-approval-spiral",
        duration_minutes=120,
        seed=42,
    )


def make_workload_w2() -> WorkloadConfig:
    """Trading algo feedback loop.

    - synthetic_market_venues: 3 (conceptual)
    - incident_seed: 99
    - time_horizon_minutes: 90
    """

    return WorkloadConfig(
        workload_id="W2",
        name="W2-trading-algo-feedback-loop",
        duration_minutes=90,
        seed=99,
    )


def make_workload_w3() -> WorkloadConfig:
    """Generative AI misconduct.

    - synthetic_customer_interactions: 50000 (conceptual)
    - incident_seed: 7
    - time_horizon_minutes: 100
    """

    return WorkloadConfig(
        workload_id="W3",
        name="W3-generative-ai-misconduct",
        duration_minutes=100,
        seed=7,
    )
