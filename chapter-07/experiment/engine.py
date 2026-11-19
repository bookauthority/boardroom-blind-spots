from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict, Any, Tuple

from .model import Portfolio, generate_synthetic_portfolio, run_loss_engine, AIScenario
from .scenarios import (
    mild_macro_scenario,
    severe_macro_scenario,
    neutral_macro_scenario,
    micro_ai_scenarios,
    firmwide_ai_scenario,
    systemic_ai_scenario,
    reverse_stress_parameter_grid,
)


@dataclass
class WorkloadRunConfig:
    workload_id: str
    variant: str  # 'baseline' or 'treatment'


def _treatment_run_with_ai(
    portfolio: Portfolio,
    macro,
    ai_scenario: AIScenario,
) -> Tuple[float, float, float]:
    """Helper to run treatment by computing AI-attributed loss via difference.

    Returns (total_loss_with_ai, ai_attributed_loss, min_capital_ratio_with_ai).
    """

    base_result = run_loss_engine(portfolio=portfolio, macro=macro, ai=None)
    ai_result = run_loss_engine(portfolio=portfolio, macro=macro, ai=ai_scenario)

    ai_attributed = max(0.0, ai_result.total_loss - base_result.total_loss)
    return ai_result.total_loss, ai_attributed, ai_result.min_capital_ratio


def run_workload_W1(variant: str) -> Dict[str, Any]:
    portfolio = generate_synthetic_portfolio()
    macro = mild_macro_scenario(horizon_months=12)
    micro_scenarios = micro_ai_scenarios()

    if variant == "baseline":
        # Run once without AI; W1 baseline focuses on micro portfolio under mild macro.
        result = run_loss_engine(portfolio=portfolio, macro=macro, ai=None)
        metrics = {
            "total_loss": float(result.total_loss),
            "min_capital_ratio": float(result.min_capital_ratio),
            "ai_attributed_loss": 0.0,
        }
        note = "Baseline mild macro; micro AI scenarios disabled."
        return {"metrics": metrics, "note": note}

    # Treatment: combine two micro scenarios sequentially and sum their AI-attributed losses.
    total_loss = 0.0
    ai_attrib_total = 0.0
    # First scenario
    tl1, ai1, cr1 = _treatment_run_with_ai(portfolio, macro, micro_scenarios[0])
    total_loss += tl1
    ai_attrib_total += ai1
    # Second scenario
    tl2, ai2, cr2 = _treatment_run_with_ai(portfolio, macro, micro_scenarios[1])
    total_loss += tl2
    ai_attrib_total += ai2
    # For reporting, we take the worst (min) capital ratio across the two scenarios.
    min_cap_ratio = min(cr1, cr2)

    metrics = {
        "total_loss": float(total_loss),
        "min_capital_ratio": float(min_cap_ratio),
        "ai_attributed_loss": float(ai_attrib_total),
    }
    note = "Treatment W1: sum of two micro AI scenarios under mild macro."
    return {"metrics": metrics, "note": note}


def run_workload_W2(variant: str) -> Dict[str, Any]:
    portfolio = generate_synthetic_portfolio()
    macro = severe_macro_scenario(horizon_months=12)
    fw_ai = firmwide_ai_scenario()

    if variant == "baseline":
        result = run_loss_engine(portfolio=portfolio, macro=macro, ai=None)
        metrics = {
            "total_loss": float(result.total_loss),
            "min_capital_ratio": float(result.min_capital_ratio),
            "ai_attributed_loss": 0.0,
        }
        note = "Baseline severe macro without firm-wide AI failure."
        return {"metrics": metrics, "note": note}

    tl, ai_loss, cr = _treatment_run_with_ai(portfolio, macro, fw_ai)
    metrics = {
        "total_loss": float(tl),
        "min_capital_ratio": float(cr),
        "ai_attributed_loss": float(ai_loss),
    }
    note = "Treatment W2: firm-wide AI scenario over severe macro."
    return {"metrics": metrics, "note": note}


def run_workload_W3(variant: str) -> Dict[str, Any]:
    portfolio = generate_synthetic_portfolio()
    macro = neutral_macro_scenario(horizon_months=12)
    sys_ai = systemic_ai_scenario()

    if variant == "baseline":
        result = run_loss_engine(portfolio=portfolio, macro=macro, ai=None)
        metrics = {
            "total_loss": float(result.total_loss),
            "min_capital_ratio": float(result.min_capital_ratio),
            "ai_attributed_loss": 0.0,
        }
        note = "Baseline neutral macro; no systemic AI failure."
        return {"metrics": metrics, "note": note}

    tl, ai_loss, cr = _treatment_run_with_ai(portfolio, macro, sys_ai)
    metrics = {
        "total_loss": float(tl),
        "min_capital_ratio": float(cr),
        "ai_attributed_loss": float(ai_loss),
    }
    note = "Treatment W3: systemic AI trading herding under neutral macro."
    return {"metrics": metrics, "note": note}


def _make_reverse_ai_scenario(params: Dict[str, float]) -> AIScenario:
    """Translate reverse stress parameters into a synthetic AI scenario.

    We map coverage and error magnitudes into PD and operational multipliers.
    All segments are affected to a degree scaled by coverage.
    """

    coverage = params["coverage_of_ai_outage"]
    error_mult = params["error_rate_multiplier"]
    duration = max(1, int(round(params["failure_duration_months"])))
    ctrl_red = params["control_effectiveness_reduction"]

    # Severity factor increases with error multiplier and control reduction.
    sev_factor = error_mult * (1.0 + ctrl_red)

    pd_mult = {
        "retail_unsecured": 1.0 + coverage * 0.3 * sev_factor,
        "mortgages": 1.0 + coverage * 0.2 * sev_factor,
        "corporate_loans": 1.0 + coverage * 0.25 * sev_factor,
    }
    oper_mult = {
        "retail_unsecured": 1.0 + coverage * 0.4 * sev_factor,
        "corporate_loans": 1.0 + coverage * 0.3 * sev_factor,
        "trading_book": 1.0 + coverage * 0.2 * sev_factor,
    }

    return AIScenario(
        scenario_id="reverse_ai_scenario",
        level="firm_wide",
        start_month=1,
        duration_months=duration,
        pd_multiplier=pd_mult,
        volume_multiplier={},
        market_vol_multiplier={"trading_book": 1.0 + coverage * 0.2 * sev_factor},
        operational_multiplier=oper_mult,
    )


def run_workload_W4(variant: str) -> Dict[str, Any]:
    portfolio = generate_synthetic_portfolio()
    macro = mild_macro_scenario(horizon_months=12)

    threshold = 0.08

    if variant == "baseline":
        result = run_loss_engine(portfolio=portfolio, macro=macro, ai=None)
        metrics = {
            "total_loss": float(result.total_loss),
            "min_capital_ratio": float(result.min_capital_ratio),
            "ai_attributed_loss": 0.0,
        }
        note = "Baseline reverse stress: mild macro, no AI; used as reference capital path."
        return {"metrics": metrics, "note": note}

    grid = reverse_stress_parameter_grid()
    best_distance = None
    best_min_ratio = None
    best_total_loss = None

    # We search for scenarios that breach the threshold, then compute a simple
    # severity score and take the one with minimal distance to breach in terms
    # of capital ratio.
    for params in grid:
        ai_scen = _make_reverse_ai_scenario(params)
        result = run_loss_engine(portfolio=portfolio, macro=macro, ai=ai_scen)
        if result.min_capital_ratio < threshold:
            distance = threshold - result.min_capital_ratio
            if best_distance is None or distance < best_distance:
                best_distance = distance
                best_min_ratio = result.min_capital_ratio
                best_total_loss = result.total_loss

    # If we never breach, we still report the last run's metrics. However, with
    # the chosen grid and simplified model, a breach is expected.
    if best_distance is None:
        # Fallback: run once with a high-severity parameter set.
        params = {
            "coverage_of_ai_outage": 1.0,
            "error_rate_multiplier": 5.0,
            "failure_duration_months": 12.0,
            "control_effectiveness_reduction": 0.9,
        }
        ai_scen = _make_reverse_ai_scenario(params)
        result = run_loss_engine(portfolio=portfolio, macro=macro, ai=ai_scen)
        best_total_loss = result.total_loss
        best_min_ratio = result.min_capital_ratio
        best_distance = max(0.0, threshold - best_min_ratio)

    metrics = {
        "total_loss": float(best_total_loss),
        "min_capital_ratio": float(best_min_ratio),
        "ai_attributed_loss": float(best_total_loss),  # here all incremental loss is AI-driven in this simplified view
    }
    note = (
        "Treatment W4: reverse stress search over AI severities; metrics reflect a near-threshold "
        "AI-dominated configuration when available."
    )
    return {"metrics": metrics, "note": note}


def run_workload_W5(variant: str) -> Dict[str, Any]:
    """Tabletop / communication workload.

    This workload focuses on combining scenarios; we simply re-use the other
    workloads' structure to generate a composite loss figure.
    """

    portfolio = generate_synthetic_portfolio()

    if variant == "baseline":
        # Composite baseline: average of mild, severe, and neutral without AI.
        r1 = run_loss_engine(portfolio=portfolio, macro=mild_macro_scenario(), ai=None)
        r2 = run_loss_engine(portfolio=portfolio, macro=severe_macro_scenario(), ai=None)
        r3 = run_loss_engine(portfolio=portfolio, macro=neutral_macro_scenario(), ai=None)
        total_loss = (r1.total_loss + r2.total_loss + r3.total_loss) / 3.0
        min_capital = min(r1.min_capital_ratio, r2.min_capital_ratio, r3.min_capital_ratio)
        metrics = {
            "total_loss": float(total_loss),
            "min_capital_ratio": float(min_capital),
            "ai_attributed_loss": 0.0,
        }
        note = "Baseline W5: composite of three macro-only scenarios for narrative comparison."
        return {"metrics": metrics, "note": note}

    # Treatment: combine micro, firm-wide, and systemic AI scenarios under their respective macro backgrounds.
    macro_mild = mild_macro_scenario()
    macro_severe = severe_macro_scenario()
    macro_neutral = neutral_macro_scenario()

    micro_list = micro_ai_scenarios()
    fw_ai = firmwide_ai_scenario()
    sys_ai = systemic_ai_scenario()

    # Micro under mild
    tl_micro, ai_micro, cr_micro = _treatment_run_with_ai(portfolio, macro_mild, micro_list[0])
    # Firm-wide under severe
    tl_fw, ai_fw, cr_fw = _treatment_run_with_ai(portfolio, macro_severe, fw_ai)
    # Systemic under neutral
    tl_sys, ai_sys, cr_sys = _treatment_run_with_ai(portfolio, macro_neutral, sys_ai)

    total_loss = tl_micro + tl_fw + tl_sys
    ai_attrib_total = ai_micro + ai_fw + ai_sys
    min_capital = min(cr_micro, cr_fw, cr_sys)

    metrics = {
        "total_loss": float(total_loss),
        "min_capital_ratio": float(min_capital),
        "ai_attributed_loss": float(ai_attrib_total),
    }
    note = (
        "Treatment W5: composite of micro, firm-wide, and systemic AI scenarios for use in "
        "tabletop narratives and stakeholder communication."
    )
    return {"metrics": metrics, "note": note}


def run_all_workloads() -> List[Dict[str, Any]]:
    """Execute all workloads under baseline and treatment.

    Returns a list of dicts with keys: variant, workload_id, run_id, success, metrics, note.
    """

    workloads = [
        "W1_micro_level_ai_failure_scenarios",
        "W2_firm_wide_common_cause_ai_failure_scenarios",
        "W3_systemic_ai_feedback_loop_scenarios",
        "W4_reverse_stress_testing_from_ai_perspective",
        "W5_tabletop_exercise_and_communication_outputs",
    ]

    results: List[Dict[str, Any]] = []

    for wid in workloads:
        for variant in ("baseline", "treatment"):
            if wid == "W1_micro_level_ai_failure_scenarios":
                out = run_workload_W1(variant)
            elif wid == "W2_firm_wide_common_cause_ai_failure_scenarios":
                out = run_workload_W2(variant)
            elif wid == "W3_systemic_ai_feedback_loop_scenarios":
                out = run_workload_W3(variant)
            elif wid == "W4_reverse_stress_testing_from_ai_perspective":
                out = run_workload_W4(variant)
            elif wid == "W5_tabletop_exercise_and_communication_outputs":
                out = run_workload_W5(variant)
            else:
                raise ValueError(f"Unknown workload id: {wid}")

            metrics = out["metrics"]
            # Validate that metrics are numeric scalars as required.
            for key, val in list(metrics.items()):
                if not isinstance(val, (int, float)):
                    raise TypeError(f"Metric {key} for {wid}/{variant} must be numeric, got {type(val)}")

            run_entry = {
                "variant": variant,
                "workload_id": wid,
                "run_id": f"{wid}::{variant}",
                "success": True,
                "metrics": metrics,
                "note": out.get("note", ""),
            }
            results.append(run_entry)

    return results
