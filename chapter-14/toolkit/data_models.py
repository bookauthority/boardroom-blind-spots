from __future__ import annotations

from dataclasses import dataclass
from typing import List


@dataclass
class AISystem:
    system_id: str
    business_line: str
    product: str
    ai_type: str
    autonomy_level: int
    criticality_tier: int
    financial_exposure: float
    systemic_pathways: str
    vendor_flag: bool
    geography: str
    validation_status: str


@dataclass
class Incident:
    incident_id: str
    severity: int
    business_impact: float
    root_cause: str
    remediation_status: str


@dataclass
class InventorySummary:
    total_systems: int
    high_criticality_systems: int
    vendor_systems: int
    average_autonomy: float


@dataclass
class IncidentSummary:
    total_incidents: int
    average_severity: float
    open_incidents: int


@dataclass
class BoardPackArtifacts:
    """Lightweight representation of the board pack components.

    The actual text/visual content is not material for the numeric metrics;
    we record counts to mimic num_artifacts-like behavior conceptually, but we
    do not store that as a metric to avoid fabricating human evaluations.
    """

    inventory_summary: InventorySummary
    incident_summary: IncidentSummary
    dashboard_sections: List[str]
    policy_templates: List[str]
    question_guides: List[str]
    incident_templates: List[str]
