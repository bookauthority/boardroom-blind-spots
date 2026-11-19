from __future__ import annotations

import csv
from pathlib import Path
from typing import List, Tuple

from .config import get_workload_config
from .data_models import AISystem, Incident, BoardPackArtifacts
from .metrics import build_inventory_summary, build_incident_summary, core_numeric_metrics
from .board_pack_templates import (
    dashboard_sections_for,
    policy_templates_for,
    question_guides_for,
    incident_templates_for,
)


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


def _build_board_pack(workload_id: str, systems: List[AISystem], incidents: List[Incident]) -> BoardPackArtifacts:
    config = get_workload_config(workload_id)
    inv_summary = build_inventory_summary(systems)
    inc_summary = build_incident_summary(incidents)
    dashboard_sections = dashboard_sections_for(config)
    policy_templates = policy_templates_for(config)
    question_guides = question_guides_for(config)
    incident_templates = incident_templates_for(config)
    return BoardPackArtifacts(
        inventory_summary=inv_summary,
        incident_summary=inc_summary,
        dashboard_sections=dashboard_sections,
        policy_templates=policy_templates,
        question_guides=question_guides,
        incident_templates=incident_templates,
    )


def run_treatment_for_workload(
    workload_id: str, inventory_path: Path, incidents_path: Path
) -> Tuple[bool, dict, str]:
    """Run the treatment toolkit pipeline for a workload.

    This simulates the Chapter 14 toolkit pipeline: it creates structured
    board pack components based on configuration and data, then extracts
    numeric metrics from the underlying summaries.
    """

    try:
        systems = _load_systems(inventory_path)
        incidents = _load_incidents(incidents_path)

        board_pack = _build_board_pack(workload_id, systems, incidents)

        # Metrics are derived from underlying summaries to ensure that both
        # baseline and treatment share comparable numeric measurements.
        metrics = core_numeric_metrics(
            board_pack.inventory_summary, board_pack.incident_summary
        )

        note = (
            "Treatment generated a structured AI oversight pack with "
            f"{len(board_pack.dashboard_sections)} dashboard sections, "
            f"{len(board_pack.policy_templates)} policy templates, "
            f"{len(board_pack.question_guides)} question guides, and "
            f"{len(board_pack.incident_templates)} incident templates."
        )
        return True, metrics, note
    except Exception as exc:  # pragma: no cover - defensive
        return False, {}, f"Treatment error for {workload_id}: {exc}"
