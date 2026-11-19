import math
from typing import Dict


# Simple, deterministic pseudo-random generator to avoid importing random/numpy.
class LcgRng:
    def __init__(self, seed: int = 1) -> None:
        self.state = seed & 0xFFFFFFFF

    def rand(self) -> float:
        # Linear congruential generator (32-bit)
        self.state = (1103515245 * self.state + 12345) & 0x7FFFFFFF
        return self.state / 0x7FFFFFFF

    def randn(self) -> float:
        # Box-Muller transform for standard normal
        u1 = max(self.rand(), 1e-12)
        u2 = self.rand()
        z = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
        return z


def _sigmoid(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    else:
        z = math.exp(x)
        return z / (1.0 + z)


# 3.2: Credit drift simulation

def credit_drift_simulation(drift: bool) -> Dict[str, float]:
    rng = LcgRng(123 if not drift else 456)
    n = 400

    auc_pairs = []
    brier_sum = 0.0

    for i in range(n):
        # Baseline features
        income = 50_000 + 10_000 * rng.randn()
        dti = 0.3 + 0.1 * rng.randn()

        if drift:
            # Gradual drift: income distribution worsens, dti increases
            t = i / n
            income_shift = -15_000 * t
            dti_shift = 0.2 * t
            income += income_shift
            dti += dti_shift

        score = -0.00003 * income + 2.5 * dti - 0.5
        pd = _sigmoid(score)

        y = 1 if rng.rand() < pd else 0

        # Prediction probability (model frozen at non-drift parameters)
        # Model believes original distribution (no drift), uses same formula but
        # does not know drift in relationship: represent regime change by offset.
        if drift:
            pred_score = -0.00003 * income + 2.5 * dti - 0.2
        else:
            pred_score = -0.00003 * income + 2.5 * dti - 0.5
        p_hat = _sigmoid(pred_score)

        auc_pairs.append((p_hat, y))
        brier_sum += (p_hat - y) ** 2

    # AUC via probabilistic interpretation: P(score_pos > score_neg)
    positives = [s for s, y in auc_pairs if y == 1]
    negatives = [s for s, y in auc_pairs if y == 0]
    if positives and negatives:
        better = 0
        ties = 0
        for sp in positives:
            for sn in negatives:
                if sp > sn:
                    better += 1
                elif sp == sn:
                    ties += 1
        total_pairs = len(positives) * len(negatives)
        auc = (better + 0.5 * ties) / total_pairs
    else:
        auc = 0.5

    brier = brier_sum / n

    # Expected loss proxy: average PD among approved loans (pd < threshold).
    threshold = 0.3
    total_pd = 0.0
    count_approved = 0
    for s, y in auc_pairs:
        if s < threshold:
            total_pd += s
            count_approved += 1
    avg_pd_approved = total_pd / count_approved if count_approved else 0.0

    return {
        "auc_roc": float(auc),
        "brier_score": float(brier),
        "expected_loss_proxy": float(avg_pd_approved),
        "n_samples": float(n),
    }


# 3.3: RL credit limits simulation

def rl_credit_limits_simulation(misaligned: bool) -> Dict[str, float]:
    rng = LcgRng(789 if not misaligned else 790)
    n_customers = 200

    true_profit_sum = 0.0
    reward_sum = 0.0

    for _ in range(n_customers):
        base_quality = rng.rand()  # higher is better
        # Baseline policy: limit proportional to quality
        aligned_limit = 1000 + 4000 * base_quality

        if misaligned:
            # Misaligned policy: aggressively increases limits for mid-quality
            if base_quality > 0.4:
                limit = aligned_limit * (1.5 if base_quality < 0.8 else 1.1)
            else:
                limit = aligned_limit * 0.8
        else:
            limit = aligned_limit

        # True default probability rises with limit relative to quality
        riskiness = max(0.0, (limit / 5000.0) - base_quality)
        pd_true = min(0.5, 0.05 + 0.8 * riskiness)
        default = 1 if rng.rand() < pd_true else 0

        interest_income = 0.15 * limit * (1.0 - pd_true)
        loss = 0.5 * limit * pd_true
        true_profit = interest_income - loss

        if misaligned:
            # Reward: emphasizes approved volume and upfront income; underweights loss
            reward = 0.0005 * limit + 1.2 * interest_income - 0.3 * loss
        else:
            # Aligned reward ~ true profit
            reward = true_profit

        true_profit_sum += true_profit
        reward_sum += reward

    avg_true_profit = true_profit_sum / n_customers
    avg_reward = reward_sum / n_customers

    return {
        "rl_cumulative_true_profit": float(true_profit_sum),
        "rl_cumulative_reward": float(reward_sum),
        "avg_true_profit": float(avg_true_profit),
        "avg_reward": float(avg_reward),
    }


# 3.4: Feedback trading simulation

def feedback_trading_simulation(with_feedback: bool) -> Dict[str, float]:
    rng = LcgRng(321 if not with_feedback else 322)
    n = 300

    price = 100.0
    fundamental = 100.0
    alpha = 0.05  # AR(1) mean reversion strength

    prices = []
    fundamentals = []

    for t in range(n):
        # Fundamental evolves as a random walk with small drift
        fundamental += 0.02 + 0.5 * rng.randn()

        # Exogenous return component
        exo = -alpha * (price - fundamental) + rng.randn()

        impact = 0.0
        if with_feedback:
            # Strategy trades on last return: trend-following
            if t > 0:
                last_ret = prices[-1] / prices[-2] - 1.0 if len(prices) > 1 else 0.0
                impact = 0.5 * last_ret

        ret = exo + impact
        price *= math.exp(0.01 * ret)

        prices.append(price)
        fundamentals.append(fundamental)

    # Realized volatility (std of log returns)
    log_rets = []
    for i in range(1, len(prices)):
        lr = math.log(prices[i] / prices[i - 1])
        log_rets.append(lr)

    if log_rets:
        mean_lr = sum(log_rets) / len(log_rets)
        var_lr = sum((x - mean_lr) ** 2 for x in log_rets) / len(log_rets)
        vol = math.sqrt(var_lr)
    else:
        vol = 0.0

    # Average deviation from fundamentals
    dev = sum(abs(p - f) for p, f in zip(prices, fundamentals)) / len(prices)

    return {
        "market_volatility_proxy": float(vol),
        "avg_price_deviation_from_fundamentals": float(dev),
    }


# 3.5: Adversarial fraud simulation

def adversarial_fraud_simulation(adversarial: bool) -> Dict[str, float]:
    rng = LcgRng(654 if not adversarial else 655)
    n = 300

    tp = fp = tn = fn = 0

    for _ in range(n):
        # True fraud probability based on a simple risk score
        base_risk = rng.rand()
        fraud = 1 if rng.rand() < base_risk else 0

        # Model decision: predict fraud if score > threshold
        score = base_risk

        if adversarial and fraud:
            # Evasion: fraudster tweaks features to move score down
            score = max(0.0, score - 0.25)

        pred = 1 if score > 0.6 else 0

        if pred == 1 and fraud == 1:
            tp += 1
        elif pred == 1 and fraud == 0:
            fp += 1
        elif pred == 0 and fraud == 0:
            tn += 1
        elif pred == 0 and fraud == 1:
            fn += 1

    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0

    # Fraud loss proxy: undetected fraud count
    fraud_loss = fn

    return {
        "fraud_detection_precision": float(precision),
        "fraud_detection_recall": float(recall),
        "fraud_loss_proxy": float(fraud_loss),
        "n_samples": float(n),
    }


# 3.6: Fairness simulation

def fairness_credit_simulation(biased: bool) -> Dict[str, float]:
    rng = LcgRng(987 if not biased else 988)
    n = 400

    # Two groups: A (reference) and B (protected)
    approved_A = approved_B = 0
    total_A = total_B = 0
    tp_A = fp_A = fn_A = tn_A = 0
    tp_B = fp_B = fn_B = tn_B = 0

    for i in range(n):
        group = "A" if i % 2 == 0 else "B"
        base_risk = 0.2 + 0.3 * rng.rand()

        if biased and group == "B":
            # Disadvantage group B via slightly higher true default prob
            base_risk += 0.1

        default = 1 if rng.rand() < base_risk else 0

        # Model score reflects biased or unbiased features
        score = base_risk
        if biased and group == "B":
            # Add a proxy that inflates perceived risk beyond truth
            score += 0.1

        approved = score < 0.35

        if group == "A":
            total_A += 1
            if approved:
                approved_A += 1
            if approved and default == 0:
                tp_A += 1
            elif approved and default == 1:
                fp_A += 1
            elif not approved and default == 0:
                tn_A += 1
            elif not approved and default == 1:
                fn_A += 1
        else:
            total_B += 1
            if approved:
                approved_B += 1
            if approved and default == 0:
                tp_B += 1
            elif approved and default == 1:
                fp_B += 1
            elif not approved and default == 0:
                tn_B += 1
            elif not approved and default == 1:
                fn_B += 1

    rate_A = approved_A / total_A if total_A else 0.0
    rate_B = approved_B / total_B if total_B else 0.0
    demographic_parity_diff = rate_A - rate_B

    # True positive rate: approved non-defaulters
    tpr_A = tp_A / (tp_A + fn_A) if (tp_A + fn_A) else 0.0
    tpr_B = tp_B / (tp_B + fn_B) if (tp_B + fn_B) else 0.0
    equalized_odds_gap = abs(tpr_A - tpr_B)

    return {
        "fairness_demographic_parity_diff": float(demographic_parity_diff),
        "fairness_equalized_odds_gap": float(equalized_odds_gap),
        "approval_rate_A": float(rate_A),
        "approval_rate_B": float(rate_B),
    }


# 3.7: Emergent behaviour simulation

def emergent_llm_simulation(rich_agent: bool) -> Dict[str, float]:
    # Instead of a real LLM, use a toy rule-based agent where "capacity"
    # controls the probability of off-policy actions.
    rng = LcgRng(111 if not rich_agent else 112)
    n_prompts = 100

    off_policy = 0
    tool_uses = 0

    for _ in range(n_prompts):
        base_prob_off = 0.01
        base_prob_tool = 0.05

        if rich_agent:
            base_prob_off = 0.12
            base_prob_tool = 0.25

        if rng.rand() < base_prob_off:
            off_policy += 1
        if rng.rand() < base_prob_tool:
            tool_uses += 1

    off_rate = off_policy / n_prompts
    tool_rate = tool_uses / n_prompts

    return {
        "llm_off_policy_action_rate": float(off_rate),
        "llm_tool_use_rate": float(tool_rate),
        "n_prompts": float(n_prompts),
    }


# 3.8: Failure cascade simulation

def cascade_risk_simulation(perturbed: bool) -> Dict[str, float]:
    rng = LcgRng(222 if not perturbed else 223)

    n_loans = 300

    # True underlying PD and LGD
    true_pd = []
    true_lgd = []
    ead = []

    for _ in range(n_loans):
        q = rng.rand()
        pd = 0.01 + 0.2 * (1.0 - q)
        lgd = 0.3 + 0.3 * rng.rand()
        exposure = 1000 + 9000 * rng.rand()
        true_pd.append(pd)
        true_lgd.append(lgd)
        ead.append(exposure)

    true_el = sum(p * l * e for p, l, e in zip(true_pd, true_lgd, ead))

    # Estimated PD/LGD under model; introduce small multiplicative biases
    if perturbed:
        pd_factor = 0.9   # underestimation of risk
        lgd_factor = 0.92
        capital_mult = 1.1  # naive aggregator understates tail somewhat
    else:
        pd_factor = 1.0
        lgd_factor = 1.0
        capital_mult = 1.3

    est_pd = [max(0.0, min(1.0, pd * pd_factor)) for pd in true_pd]
    est_lgd = [max(0.0, min(1.0, lgd * lgd_factor)) for lgd in true_lgd]

    est_el = sum(p * l * e for p, l, e in zip(est_pd, est_lgd, ead))

    # Capital ratio proxy: capital buffer / expected loss
    true_capital = capital_mult * true_el
    est_capital = capital_mult * est_el

    true_ratio = true_capital / true_el if true_el else 0.0
    est_ratio = est_capital / est_el if est_el else 0.0

    ratio_error = est_ratio - true_ratio

    return {
        "true_expected_loss": float(true_el),
        "estimated_expected_loss": float(est_el),
        "true_capital_ratio_proxy": float(true_ratio),
        "estimated_capital_ratio_proxy": float(est_ratio),
        "cascade_capital_ratio_error": float(ratio_error),
    }
