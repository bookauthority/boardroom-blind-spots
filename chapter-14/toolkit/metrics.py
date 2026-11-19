from __future__ import annotations

from typing import Iterable, Dict

from .data_models import AISystem, Incident, InventorySummary, IncidentSummary


def build_inventory_summary(systems: Iterable[AISystem]) -> InventorySummary:
    systems_list = list(systems)
    total = len(systems_list)
    high_criticality = sum(1 for s in systems_list if s.criticality_tier >= 3)
    vendor_systems = sum(1 for s in systems_list if s.vendor_flag)
    if total:
        avg_autonomy = sum(float(s.autonomy_level) for s in systems_list) / float(total)
    else:
        avg_autonomy = 0.0
    return InventorySummary(
        total_systems=total,
        high_criticality_systems=high_criticality,
        vendor_systems=vendor_systems,
        average_autonomy=avg_autonomy,
    )


def build_incident_summary(incidents: Iterable[Incident]) -> IncidentSummary:
    incidents_list = list(incidents)
    total = len(incidents_list)
    if total:
        avg_severity = sum(float(i.severity) for i in incidents_list) / float(total)
    else:
        avg_severity = 0.0
    open_count = sum(1 for i in incidents_list if i.remediation_status == "open")
    return IncidentSummary(
        total_incidents=total,
        average_severity=avg_severity,
        open_incidents=open_count,
    )


def core_numeric_metrics(
    inventory_summary: InventorySummary, incident_summary: IncidentSummary
) -> Dict[str, float]:
    """Return the core numeric metrics to be logged in the evidence file.

    These metrics are computable entirely from the synthetic data and are
    shared between baseline and treatment to ensure a fair comparison.
    """

    return {
        "num_systems": float(inventory_summary.total_systems),
        "num_incidents": float(incident_summary.total_incidents),
        "num_high_criticality_systems": float(
            inventory_summary.high_criticality_systems
        ),
        "avg_incident_severity": float(incident_summary.average_severity),
    }
