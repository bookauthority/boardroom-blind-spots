from typing import Dict, List

from .core import (
    ModelRecord,
    count_ai_assets,
    count_models_with_decision_chain,
    count_unique_dependencies,
    load_data_pipelines,
    load_decision_chains_mapping,
    load_materiality_config,
    load_concentration_dimensions,
    load_model_registry,
    load_vendor_models,
)


def _build_treatment_models() -> List[ModelRecord]:
    # In treatment, we treat the model registry as the authoritative list.
    return load_model_registry()


def _build_treatment_dependencies() -> List:
    deps = []
    deps.extend(load_data_pipelines())
    deps.extend(load_vendor_models())
    return deps


def run_inventory_treatment() -> Dict[str, float]:
    models = _build_treatment_models()
    deps = _build_treatment_dependencies()
    ai_count = count_ai_assets(models)
    dep_count = count_unique_dependencies(deps)
    return {
        "ai_asset_coverage_count": float(ai_count),
        "dependency_coverage_count": float(dep_count),
    }


def run_decision_chain_treatment() -> Dict[str, float]:
    models = _build_treatment_models()
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


def run_concentration_treatment() -> Dict[str, float]:
    models = _build_treatment_models()
    ai_models = [m for m in models if m.is_ai]

    # Simple proxies for concentration/materiality coverage:
    tiers = load_materiality_config()
    dims = load_concentration_dimensions()

    # We define materiality_coverage_count as number of AI models times
    # number of tiers defined (a proxy for tier assignment opportunities)
    # and dimension_coverage_count as number of distinct aggregation
    # dimensions configured.
    materiality_coverage = len(ai_models) * max(len(tiers), 1)
    dimension_coverage = len(dims)

    return {
        "materiality_coverage_count": float(materiality_coverage),
        "dimension_coverage_count": float(dimension_coverage),
    }
