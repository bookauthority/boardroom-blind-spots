from __future__ import annotations

from dataclasses import dataclass

from .workloads import RiskSnapshot


@dataclass
class BaselinePolicy:
    """Baseline policy: generic incident playbook.

    Behavioural assumptions encoded in this policy:
    - Focuses mainly on coarse-grained, generic severity indicators.
    - Reacts more slowly to AI-specific anomalies because there is no
      dedicated AI crisis playbook.
    - Imposes a minimum delay before decisive containment to avoid
      overreacting to transient blips.

    This is intentionally suboptimal relative to the treatment policy,
    but remains internally consistent and deterministic.
    """

    workload_id: str

    # Generic thresholds (tuned per workload empirically for demonstration):
    base_generic_threshold: float = 0.65
    min_delay_minutes: int = 5

    def decide(self, minute: int, snapshot: RiskSnapshot) -> bool:
        # Require a minimal observation period before acting
        if minute < self.min_delay_minutes:
            return False

        # Baseline reacts only when generic severity is relatively high
        # and persistent. We approximate persistence via the snapshot's
        # rolling_avg_generic feature.
        if snapshot.rolling_avg_generic >= self.base_generic_threshold:
            return True

        return False


@dataclass
class TreatmentPolicy:
    """Treatment policy: AI-specific crisis playbook.

    Behavioural assumptions encoded in this policy:
    - Monitors both generic and AI-specific anomaly indicators.
    - Uses lower thresholds when AI-specific signals are strong.
    - Can act earlier than the baseline policy when AI failures are
      clearly indicated, reflecting clearer decision rights and
      escalation paths.
    """

    workload_id: str

    # More sensitive thresholds leveraging AI-specific signal
    generic_threshold: float = 0.55
    ai_signal_threshold: float = 0.6
    min_delay_minutes: int = 2

    def decide(self, minute: int, snapshot: RiskSnapshot) -> bool:
        # Require a short but non-zero observation period
        if minute < self.min_delay_minutes:
            return False

        # If AI-specific anomaly is strong, act quickly.
        if snapshot.ai_signal_strength >= self.ai_signal_threshold:
            return True

        # Otherwise, fall back to a slightly more sensitive generic
        # severity rule than the baseline policy.
        if snapshot.rolling_avg_generic >= self.generic_threshold:
            return True

        return False
