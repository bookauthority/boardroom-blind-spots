from __future__ import annotations

from typing import List, Dict

from .model import MacroScenario, AIScenario


def mild_macro_scenario(horizon_months: int = 12) -> MacroScenario:
    # Low-level stress: severity drifts from 0.2 to 0.4.
    path = [0.2 + (0.2 * i) / max(1, horizon_months - 1) for i in range(horizon_months)]
    return MacroScenario(name="mild_macro", horizon_months=horizon_months, severity_path=path)


def severe_macro_scenario(horizon_months: int = 12) -> MacroScenario:
    # Severe stress: severity from 0.8 to 1.2.
    path = [0.8 + (0.4 * i) / max(1, horizon_months - 1) for i in range(horizon_months)]
    return MacroScenario(name="severe_macro", horizon_months=horizon_months, severity_path=path)


def neutral_macro_scenario(horizon_months: int = 12) -> MacroScenario:
    # Neutral macro: zero severity.
    path = [0.0 for _ in range(horizon_months)]
    return MacroScenario(name="neutral_macro", horizon_months=horizon_months, severity_path=path)


def micro_ai_scenarios() -> List[AIScenario]:
    # Simplified encoding of the W1 micro scenarios.
    retail_drift = AIScenario(
        scenario_id="micro_retail_credit_drift",
        level="micro",
        start_month=3,
        duration_months=9,
        pd_multiplier={"retail_unsecured": 1.8},
        volume_multiplier={"retail_unsecured": 1.25},
        market_vol_multiplier={},
        operational_multiplier={},
    )

    call_center = AIScenario(
        scenario_id="micro_call_centre_genai_misadvice",
        level="micro",
        start_month=1,
        duration_months=6,
        pd_multiplier={},
        volume_multiplier={},
        market_vol_multiplier={},
        operational_multiplier={"retail_unsecured": 1.15},
    )

    return [retail_drift, call_center]


def firmwide_ai_scenario() -> AIScenario:
    # W2 firm-wide scenario, simplified.
    return AIScenario(
        scenario_id="firmwide_feature_store_corruption",
        level="firm_wide",
        start_month=2,
        duration_months=4,
        pd_multiplier={
            "retail_unsecured": 1.4,
            "corporate_loans": 1.3,
        },
        volume_multiplier={},
        market_vol_multiplier={
            "trading_book": 1.5,
        },
        operational_multiplier={
            "retail_unsecured": 1.35,
        },
    )


def systemic_ai_scenario() -> AIScenario:
    # W3 systemic scenario, focused on trading and market-vol/liquidity.
    return AIScenario(
        scenario_id="systemic_ai_trading_herding",
        level="systemic",
        start_month=1,
        duration_months=3,
        pd_multiplier={},
        volume_multiplier={},
        market_vol_multiplier={
            "trading_book": 2.5,
        },
        operational_multiplier={
            "trading_book": 1.5,
        },
    )


def reverse_stress_parameter_grid() -> List[Dict[str, float]]:
    """Coarse grid for W4 reverse stress testing.

    We vary three discrete levels for each parameter to stay bounded but
    still produce multiple combinations. Coverage is implicit via the
    breadth of pd/operational multipliers.
    """

    coverages = [0.3, 0.6, 1.0]
    error_multipliers = [1.5, 3.0, 4.5]
    durations = [3.0, 6.0, 9.0]
    control_reductions = [0.2, 0.5, 0.8]

    grid: List[Dict[str, float]] = []
    for cov in coverages:
        for err in error_multipliers:
            for dur in durations:
                for ctrl in control_reductions:
                    grid.append(
                        {
                            "coverage_of_ai_outage": cov,
                            "error_rate_multiplier": err,
                            "failure_duration_months": dur,
                            "control_effectiveness_reduction": ctrl,
                        }
                    )
    return grid
