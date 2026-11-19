from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable


def _write_csv(path: Path, headers: Iterable[str], rows: Iterable[Iterable[object]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(list(headers))
        for row in rows:
            writer.writerow(list(row))


def _generate_inventory(num_systems: int, seed_prefix: str) -> list[list[object]]:
    rows = []
    for i in range(1, num_systems + 1):
        system_id = f"{seed_prefix}-SYS-{i:03d}"
        business_line = "Retail" if i % 3 == 0 else ("Markets" if i % 3 == 1 else "Risk")
        product = "Loans" if i % 2 == 0 else "Deposits"
        ai_type = "ML" if i % 2 == 0 else "Rules"
        autonomy_level = (i % 5) + 1
        criticality_tier = (i % 3) + 1
        financial_exposure = float(1000000 + i * 10000)
        systemic_pathways = "credit" if i % 2 == 0 else "liquidity"
        vendor_flag = (i % 4 == 0)
        geography = "EU" if i % 2 == 0 else "US"
        validation_status = "approved" if i % 4 != 0 else "pending"
        rows.append(
            [
                system_id,
                business_line,
                product,
                ai_type,
                autonomy_level,
                criticality_tier,
                financial_exposure,
                systemic_pathways,
                int(vendor_flag),
                geography,
                validation_status,
            ]
        )
    return rows


def _generate_incidents(num_incidents: int, seed_prefix: str) -> list[list[object]]:
    rows = []
    for i in range(1, num_incidents + 1):
        incident_id = f"{seed_prefix}-INC-{i:03d}"
        severity = (i % 5) + 1
        business_impact = float(10000 + i * 500)
        root_cause = "model_drift" if i % 2 == 0 else "data_issue"
        remediation_status = "open" if i % 3 == 0 else "closed"
        rows.append([incident_id, severity, business_impact, root_cause, remediation_status])
    return rows


def ensure_synthetic_data(base_dir: Path) -> None:
    """Create synthetic CSV inputs if they do not already exist.

    This function is deterministic: for a given workload id and requested
    numbers of systems/incidents, it produces the same data on every run.
    """

    workloads = {
        "W1-universal-bank-quarterly-pack": (30, 18),
        "W2-digital-bank-monthly-ops-review": (15, 10),
        "W3-asset-manager-annual-board-strategy": (20, 12),
    }

    for workload_id, (num_systems, num_incidents) in workloads.items():
        w_dir = base_dir / workload_id
        inventory_csv = w_dir / "ai_inventory.csv"
        incidents_csv = w_dir / "incidents.csv"

        if not inventory_csv.exists():
            inv_rows = _generate_inventory(num_systems, seed_prefix=workload_id)
            _write_csv(
                inventory_csv,
                [
                    "system_id",
                    "business_line",
                    "product",
                    "AI_type",
                    "autonomy_level",
                    "criticality_tier",
                    "financial_exposure",
                    "systemic_pathways",
                    "vendor_flag",
                    "geography",
                    "validation_status",
                ],
                inv_rows,
            )

        if not incidents_csv.exists():
            inc_rows = _generate_incidents(num_incidents, seed_prefix=workload_id)
            _write_csv(
                incidents_csv,
                [
                    "incident_id",
                    "severity",
                    "business_impact",
                    "root_cause",
                    "remediation_status",
                ],
                inc_rows,
            )
