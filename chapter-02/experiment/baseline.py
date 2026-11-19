from typing import Dict

from .core import (
    count_ai_assets,
    count_models_with_decision_chain,
    count_unique_dependencies,
    load_decision_chains_mapping,
    load_manual_inventory_baseline,
)


def run_inventory_baseline() -> Dict[str, float]:
    models, deps = load_manual_inventory_baseline()
    ai_count = count_ai_assets(models)
    dep_count = count_unique_dependencies(deps)
    return {
        "ai_asset_coverage_count": float(ai_count),
        "dependency_coverage_count": float(dep_count),
    }


def run_decision_chain_baseline() -> Dict[str, float]:
    # Baseline only uses manual inventory narrative; we emulate this by
    # reading the same decision chain mapping but filtering to models
    # present in the manual inventory to keep it conservative.
    models, _ = load_manual_inventory_baseline()
    model_ids = {m.model_id for m in models if m.is_ai}
    chains = [
        c
        for c in load_decision_chains_mapping()
        if c.model_id in model_ids
    ]
    covered = count_models_with_decision_chain(chains)
    return {
        "decision_chain_coverage_count": float(covered),
    }


def run_concentration_baseline() -> Dict[str, float]:
    # Very simple stand-in metric: number of AI models in manual inventory.
    models, _ = load_manual_inventory_baseline()
    ai_count = count_ai_assets(models)
    return {
        "materiality_coverage_count": float(ai_count),
    }
