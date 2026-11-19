from typing import Dict, Any, List, Tuple

from experiments import simulations


def _run_template(workload_id: str, baseline_func, treatment_func) -> Tuple[List[Dict[str, Any]], str]:
    runs: List[Dict[str, Any]] = []

    baseline_metrics = baseline_func()
    treatment_metrics = treatment_func()

    runs.append(
        {
            "variant": "baseline",
            "workload_id": workload_id,
            "run_id": f"{workload_id}-baseline-1",
            "success": True,
            "metrics": baseline_metrics,
        }
    )

    runs.append(
        {
            "variant": "treatment",
            "workload_id": workload_id,
            "run_id": f"{workload_id}-treatment-1",
            "success": True,
            "metrics": treatment_metrics,
        }
    )

    note = f"Executed baseline and treatment for {workload_id}."
    return runs, note


def run_wl_3_2() -> Tuple[List[Dict[str, Any]], str]:
    """3.2 Drift and regime change: credit default classifier."""

    def baseline() -> Dict[str, float]:
        return simulations.credit_drift_simulation(drift=False)

    def treatment() -> Dict[str, float]:
        return simulations.credit_drift_simulation(drift=True)

    return _run_template("wl-3.2-drift-credit-risk", baseline, treatment)


def run_wl_3_3() -> Tuple[List[Dict[str, Any]], str]:
    """3.3 RL misaligned optimization: credit limits."""

    def baseline() -> Dict[str, float]:
        return simulations.rl_credit_limits_simulation(misaligned=False)

    def treatment() -> Dict[str, float]:
        return simulations.rl_credit_limits_simulation(misaligned=True)

    return _run_template("wl-3.3-rl-credit-limits", baseline, treatment)


def run_wl_3_4() -> Tuple[List[Dict[str, Any]], str]:
    """3.4 Feedback loops: trading reflexivity."""

    def baseline() -> Dict[str, float]:
        return simulations.feedback_trading_simulation(with_feedback=False)

    def treatment() -> Dict[str, float]:
        return simulations.feedback_trading_simulation(with_feedback=True)

    return _run_template("wl-3.4-feedback-loop-trading", baseline, treatment)


def run_wl_3_5() -> Tuple[List[Dict[str, Any]], str]:
    """3.5 Adversarial fraud detection."""

    def baseline() -> Dict[str, float]:
        return simulations.adversarial_fraud_simulation(adversarial=False)

    def treatment() -> Dict[str, float]:
        return simulations.adversarial_fraud_simulation(adversarial=True)

    return _run_template("wl-3.5-adversarial-fraud-and-llm", baseline, treatment)


def run_wl_3_6() -> Tuple[List[Dict[str, Any]], str]:
    """3.6 Fairness and bias in credit approvals."""

    def baseline() -> Dict[str, float]:
        return simulations.fairness_credit_simulation(biased=False)

    def treatment() -> Dict[str, float]:
        return simulations.fairness_credit_simulation(biased=True)

    return _run_template("wl-3.6-fairness-credit-approvals", baseline, treatment)


def run_wl_3_7() -> Tuple[List[Dict[str, Any]], str]:
    """3.7 Emergent behaviour in a toy LLM agent."""

    def baseline() -> Dict[str, float]:
        return simulations.emergent_llm_simulation(rich_agent=False)

    def treatment() -> Dict[str, float]:
        return simulations.emergent_llm_simulation(rich_agent=True)

    return _run_template("wl-3.7-emergent-llm-agent-behaviour", baseline, treatment)


def run_wl_3_8() -> Tuple[List[Dict[str, Any]], str]:
    """3.8 Failure cascade in a small risk pipeline."""

    def baseline() -> Dict[str, float]:
        return simulations.cascade_risk_simulation(perturbed=False)

    def treatment() -> Dict[str, float]:
        return simulations.cascade_risk_simulation(perturbed=True)

    return _run_template("wl-3.8-multi-stage-failure-cascade", baseline, treatment)
