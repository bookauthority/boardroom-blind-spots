from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Dict, List, Literal, Tuple

from .model import ModelInput
from .policy import Decision, RiskAppetite, action_engine_decision_from_risk

OversightMode = Literal["auto", "human_in_loop", "human_on_loop"]


@dataclass
class GuardrailMetricsCounters:
    total_requests: int = 0
    guardrail_activations: int = 0


@dataclass
class RateLimiter:
    max_requests: int
    window_seconds: float
    allowance: float = 0.0
    last_check: float = field(default_factory=time.monotonic)

    def allow(self) -> bool:
        now = time.monotonic()
        time_passed = now - self.last_check
        self.last_check = now
        self.allowance += time_passed * (self.max_requests / self.window_seconds)
        if self.allowance > self.max_requests:
            self.allowance = float(self.max_requests)
        if self.allowance < 1.0:
            return False
        self.allowance -= 1.0
        return True


@dataclass
class CircuitBreaker:
    error_threshold: int
    window_size: int
    state: Literal["closed", "open"] = "closed"
    recent_errors: List[bool] = field(default_factory=list)

    def record(self, error: bool) -> None:
        if self.state == "open":
            return
        self.recent_errors.append(error)
        if len(self.recent_errors) > self.window_size:
            self.recent_errors.pop(0)
        if sum(self.recent_errors) >= self.error_threshold:
            self.state = "open"

    def allow(self) -> bool:
        return self.state == "closed"


@dataclass
class KillSwitch:
    active: bool = False

    def enable(self) -> None:
        self.active = True

    def disable(self) -> None:
        self.active = False


@dataclass
class OversightOrchestrator:
    medium_risk_threshold: float
    high_risk_threshold: float

    def select_mode(self, risk_score: float) -> OversightMode:
        if risk_score <= self.medium_risk_threshold:
            return "auto"
        if risk_score <= self.high_risk_threshold:
            return "human_on_loop"
        return "human_in_loop"


@dataclass
class VirtualHumanReviewer:
    """Deterministic 'human' for repeatability.

    - For high-risk recommendations, tends to decline.
    - For medium risk, tends to accept or move to manual_review.
    """

    def review(self, proposed: Decision, risk_score: float) -> Decision:
        if risk_score >= 0.8:
            return "decline"
        if risk_score >= 0.5:
            if proposed == "approve":
                return "manual_review"
            return proposed
        return proposed


@dataclass
class AccessControl:
    allowed_roles: Tuple[str, ...] = ("client",)

    def is_allowed(self, role: str) -> bool:
        return role in self.allowed_roles


@dataclass
class StructuredLogger:
    records: List[Dict] = field(default_factory=list)

    def log(self, record: Dict) -> None:
        # Append-only in-memory log; could be extended to hash-chaining.
        self.records.append(record)


@dataclass
class TreatmentGuardrailFramework:
    appetite: RiskAppetite
    rate_limiter: RateLimiter
    circuit_breaker: CircuitBreaker
    kill_switch: KillSwitch
    oversight: OversightOrchestrator
    reviewer: VirtualHumanReviewer
    access: AccessControl
    logger: StructuredLogger
    metrics: GuardrailMetricsCounters

    def handle_request(
        self,
        features: ModelInput,
        risk_score: float,
        client_role: str,
    ) -> Decision:
        self.metrics.total_requests += 1

        # Access control
        if not self.access.is_allowed(client_role):
            self.metrics.guardrail_activations += 1
            self.logger.log({"event": "access_denied", "role": client_role})
            return "decline"

        # Kill switch: divert to conservative rule (always decline high amount)
        if self.kill_switch.active:
            self.metrics.guardrail_activations += 1
            decision = "decline" if features.amount >= 1000 else "manual_review"
            self.logger.log({"event": "kill_switch_active", "decision": decision})
            return decision

        # Rate limiting
        if not self.rate_limiter.allow():
            self.metrics.guardrail_activations += 1
            self.logger.log({"event": "rate_limited"})
            return "manual_review"

        # Circuit breaker
        if not self.circuit_breaker.allow():
            self.metrics.guardrail_activations += 1
            self.logger.log({"event": "circuit_open"})
            return "manual_review"

        # Normal decision path with oversight
        base_decision = action_engine_decision_from_risk(risk_score, self.appetite)
        mode = self.oversight.select_mode(risk_score)

        if mode == "auto":
            final_decision = base_decision
        elif mode == "human_on_loop":
            # In this toy example, human_on_loop observes but does not change decision
            final_decision = base_decision
            self.metrics.guardrail_activations += 1
            self.logger.log({"event": "human_on_loop_observe", "decision": final_decision})
        else:  # human_in_loop
            self.metrics.guardrail_activations += 1
            final_decision = self.reviewer.review(base_decision, risk_score)
            self.logger.log(
                {
                    "event": "human_in_loop_review",
                    "proposed": base_decision,
                    "final": final_decision,
                }
            )

        return final_decision
