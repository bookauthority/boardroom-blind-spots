from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Tuple

from .data_models import AISystem, Incident
from .metrics import build_inventory_summary, build_incident_summary, core_numeric_metrics


def _load_systems(path: Path) -> List[AISystem]:
    systems: List[AISystem] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            systems.append(
                AISystem(
                    system_id=row["system_id"],
                    business_line=row["business_line"],
                    product=row["product"],
                    ai_type=row["AI_type"],
                    autonomy_level=int(row["autonomy_level"]),
                    criticality_tier=int(row["criticality_tier"]),
                    financial_exposure=float(row["financial_exposure"]),
                    systemic_pathways=row["systemic_pathways"],
                    vendor_flag=bool(int(row["vendor_flag"])),
                    geography=row["geography"],
                    validation_status=row["validation_status"],
                )
            )
    return systems


def _load_incidents(path: Path) -> List[Incident]:
    incidents: List[Incident] = []
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            incidents.append(
                Incident(
                    incident_id=row["incident_id"],
                    severity=int(row["severity"]),
                    business_impact=float(row["business_impact"]),
                    root_cause=row["root_cause"],
                    remediation_status=row["remediation_status"],
                )
            )
    return incidents


def run_baseline_for_workload(
    workload_id: str, inventory_path: Path, incidents_path: Path
) -> Tuple[bool, dict, str]:
    """Simulate the baseline preparation.

    The baseline simply loads the data, computes high-level summaries, and
    returns core numeric metrics. There is no advanced toolkit behavior here;
    it mimics manually assembled views based on the same data.
    """

    try:
        systems = _load_systems(inventory_path)
        incidents = _load_incidents(incidents_path)
        inv_summary = build_inventory_summary(systems)
        inc_summary = build_incident_summary(incidents)
        metrics = core_numeric_metrics(inv_summary, inc_summary)
        note = "Baseline used simple aggregate summaries only."
        return True, metrics, note
    except Exception as exc:  # pragma: no cover - defensive
        return False, {}, f"Baseline error for {workload_id}: {exc}"
