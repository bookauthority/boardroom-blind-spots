from __future__ import annotations

"""Lightweight configuration for the Chapter 6 experiment.

The real book specification mentions external YAML configs; here we embed
minimal configuration directly in Python to keep the project self-contained
and avoid external dependencies.
"""


def get_portfolio_config() -> dict:
    """Return static configuration for the synthetic portfolio.

    The configuration defines:
    - models and their metadata
    - number of time periods

    This function is deterministic and contains no randomness.
    """

    models = [
        {
            "model_id": "retail_credit_scoring",
            "business_line": "Retail Banking",
            "product_type": "Unsecured Loans",
            "model_type": "gradient_boosting",
            "criticality_tier": 1,
            "auto_decision_share_pct": 40.0,
        },
        {
            "model_id": "sme_credit_scoring",
            "business_line": "SME Banking",
            "product_type": "Term Loans",
            "model_type": "gradient_boosting",
            "criticality_tier": 1,
            "auto_decision_share_pct": 30.0,
        },
        {
            "model_id": "market_making_agent",
            "business_line": "Markets",
            "product_type": "Equities",
            "model_type": "rl_policy",
            "criticality_tier": 1,
            "auto_decision_share_pct": 90.0,
        },
        {
            "model_id": "aml_transaction_monitoring",
            "business_line": "Compliance",
            "product_type": "Payments",
            "model_type": "deep_neural_net",
            "criticality_tier": 2,
            "auto_decision_share_pct": 10.0,
        },
        {
            "model_id": "card_fraud_detection",
            "business_line": "Retail Banking",
            "product_type": "Cards",
            "model_type": "deep_neural_net",
            "criticality_tier": 1,
            "auto_decision_share_pct": 85.0,
        },
        {
            "model_id": "marketing_next_best_action",
            "business_line": "Retail Banking",
            "product_type": "Cross-sell",
            "model_type": "gradient_boosting",
            "criticality_tier": 3,
            "auto_decision_share_pct": 70.0,
        },
        {
            "model_id": "llm_customer_service_assistant",
            "business_line": "Service",
            "product_type": "Contact Centre",
            "model_type": "llm",
            "criticality_tier": 2,
            "auto_decision_share_pct": 20.0,
        },
        {
            "model_id": "algo_execution_router",
            "business_line": "Markets",
            "product_type": "Execution",
            "model_type": "rl_policy",
            "criticality_tier": 1,
            "auto_decision_share_pct": 95.0,
        },
    ]

    config = {
        "models": models,
        # We use 24 monthly periods to align with the spec (12–24 months)
        "n_periods": 24,
        # Fixed seed for all random draws in this module
        "random_seed": 12345,
    }
    return config


def get_governance_thresholds() -> dict:
    """Return bands for AI risk metrics used by the simple rules engine.

    Thresholds are aligned roughly with the values mentioned in the
    specification but simplified for this experiment.
    """

    return {
        "drift_score": {"green": 0.2, "amber": 0.4},
        # fairness_gap in percentage points (0–100 scale implied here)
        "fairness_gap": {"green": 3.0, "amber": 5.0},
        "robustness_score": {"amber": 0.9, "red": 0.8},
        "explainability_coverage_pct": {"amber": 70.0, "red": 90.0},
        "auto_decision_share_pct_tier1": {"green": 50.0, "amber": 80.0},
        "cross_model_output_correlation": {"green": 0.5, "amber": 0.8},
    }
