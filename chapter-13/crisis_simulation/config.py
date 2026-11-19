from __future__ import annotations

from dataclasses import dataclass
from typing import List

# Import workload factories without creating a circular type dependency.
# WorkloadConfig is defined in this module and used in workloads.py
# only for type checking, not at import time.

CHAPTER_NUMBER = 13
EXPERIMENT_ID = "chap13-crisis-mgmt-ai-failure-war-game-v1"


@dataclass(frozen=True)
class WorkloadConfig:
    """Configuration for a single workload.

    Fields:
        workload_id: Short, stable identifier (e.g., "W1").
        name: Human-readable name of the workload.
        duration_minutes: Simulation horizon in minutes.
        seed: RNG seed for deterministic synthetic signals.
    """

    workload_id: str
    name: str
    duration_minutes: int
    seed: int


def get_all_workloads() -> List[WorkloadConfig]:
    """Return all workload configurations used in the experiment.

    Each workload is aligned with a conceptual scenario from the chapter,
    but the simulation itself only uses a handful of numeric parameters.
    """

    # Import here to avoid circular dependency during module initialization.
    from .workloads import make_workload_w1, make_workload_w2, make_workload_w3

    return [
        make_workload_w1(),
        make_workload_w2(),
        make_workload_w3(),
    ]
