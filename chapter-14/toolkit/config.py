from __future__ import annotations

from dataclasses import dataclass


@dataclass
class WorkloadConfig:
    """Configuration knobs representing archetype and geography.

    This is intentionally simple and used to slightly vary behavior or labels
    in the treatment toolkit, reflecting the customization profiles described
    in Section 14.8.
    """

    workload_id: str
    archetype: str
    geography: str


def get_workload_config(workload_id: str) -> WorkloadConfig:
    """Return a simple config for the given workload.

    The mapping is deterministic and hard-coded for this experiment.
    """

    if workload_id == "W1-universal-bank-quarterly-pack":
        return WorkloadConfig(
            workload_id=workload_id,
            archetype="universal_bank",
            geography="EU+US",
        )
    if workload_id == "W2-digital-bank-monthly-ops-review":
        return WorkloadConfig(
            workload_id=workload_id,
            archetype="digital_bank",
            geography="single_jurisdiction",
        )
    if workload_id == "W3-asset-manager-annual-board-strategy":
        return WorkloadConfig(
            workload_id=workload_id,
            archetype="asset_manager_insurer",
            geography="regional",
        )
    # Default fallback
    return WorkloadConfig(
        workload_id=workload_id,
        archetype="generic",
        geography="unknown",
    )
