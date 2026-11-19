from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Any, Dict

from .guardrails import (
    AccessControl,
    CircuitBreaker,
    GuardrailMetricsCounters,
    KillSwitch,
    OversightOrchestrator,
    RateLimiter,
    StructuredLogger,
    TreatmentGuardrailFramework,
    VirtualHumanReviewer,
)
from .model import SimpleRiskModel
from .policy import RISK_APPETITE, action_engine_decision_from_risk, is_policy_unsafe
from .workloads import generate_workload


@dataclass
class ExperimentRunner:
    chapter: int
    experiment_id: str

    def run_workload(self, variant: str, workload_id: str) -> Dict[str, Any]:
        """Run a single workload for a given variant and return run record.

        Metrics:
          - unsafe_decision_rate
          - decision_throughput (decisions per second)
          - guardrail_activation_rate (events per request)
        """

        if variant not in ("baseline", "treatment"):
            raise ValueError("variant must be 'baseline' or 'treatment'")

        # Fixed number of requests per workload for bounded runtime
        n_requests = 500

        # Seed ensures deterministic inputs per (variant, workload)
        base_seed = 12345
        variant_offset = 0 if variant == "baseline" else 100000
        seed = base_seed + variant_offset

        inputs, used_seed = generate_workload(workload_id, seed, n_requests)

        model = SimpleRiskModel()

        unsafe_count = 0
        total = 0

        guardrail_counters = GuardrailMetricsCounters()

        # Treatment framework setup (ignored for baseline in practice)
        framework = None
        if variant == "treatment":
            framework = TreatmentGuardrailFramework(
                appetite=RISK_APPETITE,
                rate_limiter=RateLimiter(max_requests=200, window_seconds=1.0),
                circuit_breaker=CircuitBreaker(error_threshold=10, window_size=50),
                kill_switch=KillSwitch(active=False),
                oversight=OversightOrchestrator(
                    medium_risk_threshold=0.3, high_risk_threshold=0.7
                ),
                reviewer=VirtualHumanReviewer(),
                access=AccessControl(allowed_roles=("client",)),
                logger=StructuredLogger(),
                metrics=guardrail_counters,
            )

            # For WL5, activate kill switch partway through the run
            if workload_id == "WL5_kill_switch_operational_test":
                framework.kill_switch.enable()

        start = time.perf_counter()

        for features in inputs:
            risk = model.predict_risk(features)
            if variant == "baseline":
                decision = action_engine_decision_from_risk(risk, RISK_APPETITE)
            else:
                assert framework is not None
                decision = framework.handle_request(features, risk, client_role="client")

            if is_policy_unsafe(features, decision, risk):
                unsafe_count += 1
            total += 1

        duration = time.perf_counter() - start
        duration = max(duration, 1e-9)

        unsafe_rate = unsafe_count / float(total) if total else 0.0
        throughput = total / duration

        if variant == "treatment":
            ga = guardrail_counters.guardrail_activations / float(
                guardrail_counters.total_requests or 1
            )
        else:
            ga = 0.0

        metrics: Dict[str, float] = {
            "unsafe_decision_rate": float(unsafe_rate),
            "decision_throughput": float(throughput),
            "guardrail_activation_rate": float(ga),
        }

        run_record: Dict[str, Any] = {
            "variant": variant,
            "workload_id": workload_id,
            "run_id": f"{variant}-{workload_id}-seed{used_seed}",
            "success": True,
            "metrics": metrics,
        }

        return run_record
