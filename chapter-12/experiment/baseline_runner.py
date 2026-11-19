from __future__ import annotations

from typing import Dict, Any

from .core import SyntheticCreditDataGenerator, LinearLogisticModel, SimulatedLLM
from .metrics import auc_roc, accuracy, psi


def run_baseline_wl1() -> Dict[str, Any]:
    """Baseline validation for WL1: simple model-centric check.

    Returns a dict with keys: success (bool), metrics (dict of numeric metrics).
    """

    gen = SyntheticCreditDataGenerator(seed=123, n_samples=4000)
    data = gen.generate()

    model = LinearLogisticModel(n_features=len(data.feature_names), lr=1e-8, n_iter=150)
    model.fit(data.X_train, data.y_train)

    probs_test = model.predict_proba(data.X_test)
    preds_test = model.predict(data.X_test, threshold=0.5)

    auc = auc_roc(data.y_test, probs_test)
    acc = accuracy(data.y_test, preds_test)

    # simple stress: add a fixed offset to income to simulate macro change
    stressed_income = [row[0] * 0.9 for row in data.X_test]
    base_income = [row[0] for row in data.X_train]
    psi_income = psi(base_income, stressed_income, n_bins=10)

    metrics = {
        "auc_roc": float(auc),
        "accuracy": float(acc),
        "psi_mean": float(psi_income),  # representative PSI for one key feature
    }

    return {"success": True, "metrics": metrics}


def run_baseline_wl2() -> Dict[str, Any]:
    """Baseline for WL2: traditional validation ignores LLM safety, so we only
    provide a constant trivial metric (e.g., number of prompts tested) and no
    policy-violation rate.
    """

    llm = SimulatedLLM()
    prompts = [
        "How to get approved for a credit card?",
        "Why was I declined?",
    ]
    count = 0
    for p in prompts:
        _ = llm.generate(p)
        count += 1

    metrics = {
        # placeholder numeric metric that is actually measured: number of prompts seen
        "prompt_count": float(count),
    }

    return {"success": True, "metrics": metrics}
