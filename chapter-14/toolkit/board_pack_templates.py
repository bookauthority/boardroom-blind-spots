from __future__ import annotations

from typing import List

from .config import WorkloadConfig


def dashboard_sections_for(config: WorkloadConfig) -> List[str]:
    base = [
        "AI inventory overview",
        "High criticality systems heatmap",
        "Incident trends",
    ]
    if config.archetype == "universal_bank":
        base.append("Cross-border AI deployment overview")
    elif config.archetype == "digital_bank":
        base.append("Real-time onboarding & fraud AI metrics")
    elif config.archetype == "asset_manager_insurer":
        base.append("Portfolio & solvency AI risk lenses")
    return base


def policy_templates_for(config: WorkloadConfig) -> List[str]:
    templates = [
        f"AI Use Policy ({config.archetype})",
        f"AI Risk Appetite Statement ({config.geography})",
        "AI Escalation Protocol",
    ]
    return templates


def question_guides_for(config: WorkloadConfig) -> List[str]:
    guides = [
        "Board challenge questions: inventory & governance",
        "Risk committee deep-dive: incidents & near-misses",
    ]
    if config.archetype == "universal_bank":
        guides.append("Markets & trading AI challenge guide")
    elif config.archetype == "digital_bank":
        guides.append("Ops committee: onboarding & fraud AI")
    elif config.archetype == "asset_manager_insurer":
        guides.append("Investment committee: AI in portfolios & pricing")
    return guides


def incident_templates_for(config: WorkloadConfig) -> List[str]:
    return [
        "Incident report template: root cause & controls",
        "Near-miss template: systemic pathways & escalation",
    ]
