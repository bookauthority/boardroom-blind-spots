import csv
import os
from dataclasses import dataclass
from typing import Dict, List, Tuple


DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
CONFIG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config")


@dataclass
class ModelRecord:
    model_id: str
    name: str
    is_ai: bool
    business_line: str
    owner: str
    vendor: str


@dataclass
class DependencyRecord:
    source_model_id: str
    dependency_type: str
    dependency_name: str


@dataclass
class DecisionChainRecord:
    model_id: str
    business_process: str
    decision_type: str
    exposure_type: str
    exposure_channel: str


def _read_csv(path: str) -> List[Dict[str, str]]:
    rows: List[Dict[str, str]] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append({k: (v or "").strip() for k, v in row.items()})
    return rows


def load_model_registry() -> List[ModelRecord]:
    path = os.path.join(DATA_DIR, "sample_model_registry.csv")
    rows = _read_csv(path)
    models: List[ModelRecord] = []
    for r in rows:
        is_ai = r.get("type", "").lower() == "ai"
        models.append(
            ModelRecord(
                model_id=r.get("model_id", ""),
                name=r.get("name", ""),
                is_ai=is_ai,
                business_line=r.get("business_line", ""),
                owner=r.get("owner", ""),
                vendor=r.get("vendor", ""),
            )
        )
    return models


def load_data_pipelines() -> List[DependencyRecord]:
    path = os.path.join(DATA_DIR, "sample_data_pipelines.csv")
    rows = _read_csv(path)
    deps: List[DependencyRecord] = []
    for r in rows:
        deps.append(
            DependencyRecord(
                source_model_id=r.get("consumer_model_id", ""),
                dependency_type="data_pipeline",
                dependency_name=r.get("pipeline_id", ""),
            )
        )
    return deps


def load_vendor_models() -> List[DependencyRecord]:
    path = os.path.join(DATA_DIR, "sample_vendor_models.csv")
    rows = _read_csv(path)
    deps: List[DependencyRecord] = []
    for r in rows:
        deps.append(
            DependencyRecord(
                source_model_id=r.get("consumer_model_id", ""),
                dependency_type="vendor_service",
                dependency_name=r.get("vendor_service", ""),
            )
        )
    return deps


def load_manual_inventory_baseline() -> Tuple[List[ModelRecord], List[DependencyRecord]]:
    path = os.path.join(DATA_DIR, "manual_inventory_baseline.csv")
    rows = _read_csv(path)
    models: List[ModelRecord] = []
    deps: List[DependencyRecord] = []
    for r in rows:
        model_id = r.get("model_id", "")
        if model_id:
            models.append(
                ModelRecord(
                    model_id=model_id,
                    name=r.get("name", ""),
                    is_ai=(r.get("is_ai", "").lower() == "true"),
                    business_line=r.get("business_line", ""),
                    owner=r.get("owner", ""),
                    vendor=r.get("vendor", ""),
                )
            )
        dep_name = r.get("dependency_name", "")
        dep_type = r.get("dependency_type", "")
        if model_id and dep_name and dep_type:
            deps.append(
                DependencyRecord(
                    source_model_id=model_id,
                    dependency_type=dep_type,
                    dependency_name=dep_name,
                )
            )
    return models, deps


def load_decision_chains_mapping() -> List[DecisionChainRecord]:
    path = os.path.join(DATA_DIR, "sample_decision_chains.csv")
    rows = _read_csv(path)
    chains: List[DecisionChainRecord] = []
    for r in rows:
        chains.append(
            DecisionChainRecord(
                model_id=r.get("model_id", ""),
                business_process=r.get("business_process", ""),
                decision_type=r.get("decision_type", ""),
                exposure_type=r.get("exposure_type", ""),
                exposure_channel=r.get("exposure_channel", ""),
            )
        )
    return chains


def count_ai_assets(models: List[ModelRecord]) -> int:
    return sum(1 for m in models if m.is_ai and m.model_id)


def count_unique_dependencies(deps: List[DependencyRecord]) -> int:
    seen = set()
    for d in deps:
        if not d.source_model_id or not d.dependency_name:
            continue
        seen.add((d.source_model_id, d.dependency_type, d.dependency_name))
    return len(seen)


def count_models_with_decision_chain(chains: List[DecisionChainRecord]) -> int:
    return len({c.model_id for c in chains if c.model_id})


def load_materiality_config() -> Dict[str, str]:
    """Load a very small YAML-like config (key: value per line)."""
    path = os.path.join(CONFIG_DIR, "materiality_tiers.yaml")
    tiers: Dict[str, str] = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if ":" in line:
                k, v = line.split(":", 1)
                tiers[k.strip()] = v.strip()
    return tiers


def load_concentration_dimensions() -> List[str]:
    path = os.path.join(CONFIG_DIR, "concentration_dimensions.yaml")
    dims: List[str] = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#"):
                continue
            if line.startswith("-"):
                dims.append(line.lstrip("- ").strip())
    return dims
