from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from .config import WorkloadConfig
from .workloads import RiskSnapshot, generate_signal_stream


class Policy(Protocol):
    """Protocol for decision policies.

    Both baseline and treatment policies implement this interface so the
    engine can evaluate them uniformly.
    """

    workload_id: str

    def decide(self, minute: int, snapshot: RiskSnapshot) -> bool:  # pragma: no cover - interface
        """Return True if decisive containment action should be taken now."""


@dataclass
class RunResult:
    """Result of a single policy run on a workload."""

    time_to_decisive_containment_action: float


class CrisisEngine:
    """Core simulation engine.

    The engine steps through time for a given workload and policy, and
    records the earliest minute in which the policy opts to take a
    decisive containment action.
    """

    def run(self, workload: WorkloadConfig, policy: Policy) -> RunResult:
        stream = generate_signal_stream(workload)

        containment_minute: int | None = None

        for minute, snapshot in enumerate(stream):
            if policy.decide(minute, snapshot):
                containment_minute = minute
                break

        if containment_minute is None:
            # Worst case: no containment; treat as taking the full duration.
            containment_minute = workload.duration_minutes

        return RunResult(time_to_decisive_containment_action=float(containment_minute))
