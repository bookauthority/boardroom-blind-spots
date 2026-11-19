from __future__ import annotations

from dataclasses import dataclass
from typing import List, Dict


@dataclass
class MacroScenario:
    name: str
    horizon_months: int
    # Simple macro severity index per month (0 = neutral; >0 = stress)
    severity_path: List[float]


@dataclass
class PortfolioSegment:
    name: str
    exposure: float  # total exposure
    base_pd: float  # base probability of default per year
    lgd: float  # loss given default
    # non-credit loss sensitivities (per unit exposure per macro severity unit)
    base_market_sens: float
    base_operational_sens: float


@dataclass
class Portfolio:
    segments: List[PortfolioSegment]

    def total_exposure(self) -> float:
        return sum(s.exposure for s in self.segments)


@dataclass
class AIScenario:
    scenario_id: str
    level: str  # 'micro', 'firm_wide', 'systemic'
    start_month: int  # 1-based
    duration_months: int
    # Per-segment parameters keyed by segment name. Missing keys => no AI shock.
    pd_multiplier: Dict[str, float]
    volume_multiplier: Dict[str, float]
    market_vol_multiplier: Dict[str, float]
    operational_multiplier: Dict[str, float]


@dataclass
class RunResult:
    total_loss: float
    ai_attributed_loss: float
    min_capital_ratio: float


def generate_synthetic_portfolio() -> Portfolio:
    """Generate a simple synthetic portfolio with a few segments.

    The quantitative values are arbitrary but consistent and deterministic.
    """

    segments = [
        PortfolioSegment(
            name="retail_unsecured",
            exposure=1_000_000.0,
            base_pd=0.03,
            lgd=0.5,
            base_market_sens=0.0,
            base_operational_sens=10.0,
        ),
        PortfolioSegment(
            name="mortgages",
            exposure=2_000_000.0,
            base_pd=0.01,
            lgd=0.3,
            base_market_sens=0.0,
            base_operational_sens=6.0,
        ),
        PortfolioSegment(
            name="corporate_loans",
            exposure=1_500_000.0,
            base_pd=0.02,
            lgd=0.4,
            base_market_sens=15.0,
            base_operational_sens=8.0,
        ),
        PortfolioSegment(
            name="trading_book",
            exposure=500_000.0,
            base_pd=0.0,
            lgd=0.0,
            base_market_sens=40.0,
            base_operational_sens=4.0,
        ),
    ]
    return Portfolio(segments=segments)


def simple_capital_ratio(initial_capital: float, risk_weighted_assets: float, total_loss: float) -> float:
    """Compute a basic capital ratio after losses.

    Capital ratio = max(0, (capital - loss) / RWA).
    We assume a fixed RWA for the run.
    """

    remaining = max(0.0, initial_capital - total_loss)
    if risk_weighted_assets <= 0.0:
        return 0.0
    return remaining / risk_weighted_assets


def run_loss_engine(
    portfolio: Portfolio,
    macro: MacroScenario,
    ai: AIScenario | None,
    initial_capital: float = 500_000.0,
    risk_weighted_assets: float = 4_000_000.0,
) -> RunResult:
    """Run a very simple multi-period loss engine.

    - Credit losses scale with macro severity and PD multipliers.
    - Market losses scale with macro severity and market volatility multipliers.
    - Operational losses scale with macro severity and AI operational multipliers.
    - AI-attributed loss is the incremental loss over a counterfactual with no AI shock
      but *same* macro path.

    For treatment runs we call this twice: once with AI and once with ai=None to
    compute AI-attributed loss as a deterministic difference.
    """

    horizon = macro.horizon_months
    total_loss = 0.0

    for month_idx in range(horizon):
        sev = macro.severity_path[month_idx]
        month_credit = 0.0
        month_market = 0.0
        month_oper = 0.0

        for seg in portfolio.segments:
            # macro credit pd adjustment: (1 + 0.5 * sev) on annual PD.
            macro_pd_mult = 1.0 + 0.5 * sev
            pd_mult = macro_pd_mult
            vol_mult = 1.0 + 0.5 * sev
            oper_mult = 1.0 + 0.3 * sev

            # AI adjustments if in active window and parameters defined.
            if ai is not None:
                month = month_idx + 1  # 1-based
                if ai.start_month <= month < ai.start_month + ai.duration_months:
                    if seg.name in ai.pd_multiplier:
                        pd_mult *= ai.pd_multiplier[seg.name]
                    if seg.name in ai.market_vol_multiplier:
                        vol_mult *= ai.market_vol_multiplier[seg.name]
                    if seg.name in ai.operational_multiplier:
                        oper_mult *= ai.operational_multiplier[seg.name]

            # Convert annual PD to monthly default probability using linear approx
            eff_pd = seg.base_pd * pd_mult / 12.0
            credit_loss = seg.exposure * eff_pd * seg.lgd
            market_loss = seg.base_market_sens * vol_mult * abs(sev)
            oper_loss = seg.base_operational_sens * oper_mult * (1.0 + abs(sev))

            month_credit += credit_loss
            month_market += market_loss
            month_oper += oper_loss

        total_loss += month_credit + month_market + month_oper

    min_ratio = simple_capital_ratio(initial_capital=initial_capital, risk_weighted_assets=risk_weighted_assets, total_loss=total_loss)

    # AI-attributed loss is computed externally by running twice; here we return zero
    # and let the caller overwrite if appropriate.
    return RunResult(total_loss=total_loss, ai_attributed_loss=0.0, min_capital_ratio=min_ratio)
