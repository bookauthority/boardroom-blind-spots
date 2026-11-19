from typing import Dict

from .baseline import (
    run_concentration_baseline,
    run_decision_chain_baseline,
    run_inventory_baseline,
)
from .treatment import (
    run_concentration_treatment,
    run_decision_chain_treatment,
    run_inventory_treatment,
)


def run_workload_1_baseline() -> Dict[str, float]:
    return run_inventory_baseline()


def run_workload_1_treatment() -> Dict[str, float]:
    return run_inventory_treatment()


def run_workload_2_baseline() -> Dict[str, float]:
    return run_decision_chain_baseline()


def run_workload_2_treatment() -> Dict[str, float]:
    return run_decision_chain_treatment()


def run_workload_3_baseline() -> Dict[str, float]:
    return run_concentration_baseline()


def run_workload_3_treatment() -> Dict[str, float]:
    return run_concentration_treatment()
