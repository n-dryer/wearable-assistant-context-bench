"""Statistical utilities for the Wearable Assistant Context Benchmark.

Provides Wilson score confidence intervals, McNemar's paired comparison
test, per-shift-type breakdowns, and empirical difficulty grounding.

Design choices follow Bowyer et al. (2025, arxiv:2503.01747):
Wilson intervals instead of CLT-based CIs for binary outcomes with
small N. McNemar's test for paired model comparison on the same
scenario set.
"""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from typing import Any


@dataclass
class WilsonCI:
    """Wilson score confidence interval for a binary proportion.

    Attributes:
        proportion: Point estimate (successes / total).
        lower: Lower bound of the CI.
        upper: Upper bound of the CI.
        n: Total observations.
        k: Number of successes.
        confidence: Confidence level (default 0.95).
    """

    proportion: float
    lower: float
    upper: float
    n: int
    k: int
    confidence: float = 0.95


def wilson_ci(k: int, n: int, confidence: float = 0.95) -> WilsonCI:
    """Compute a Wilson score confidence interval.

    Uses the Wilson score method, which is well-calibrated for small
    samples and proportions near 0 or 1 — unlike the normal
    approximation (Wald interval) which can produce negative bounds or
    overshoot 1.0.

    Reference: Wilson, E. B. (1927). Probable inference, the law of
    succession, and statistical inference. JASA, 22(158), 209–212.

    Args:
        k: Number of successes.
        n: Total observations. Must be > 0.
        confidence: Confidence level in (0, 1). Default 0.95.

    Returns:
        A WilsonCI dataclass with proportion, lower, upper, n, k.
    """
    if n <= 0:
        return WilsonCI(
            proportion=0.0, lower=0.0, upper=0.0, n=0, k=0,
            confidence=confidence,
        )

    # z-score for the confidence level (two-tailed)
    # For 0.95 confidence, z ≈ 1.96
    from statistics import NormalDist

    z = NormalDist().inv_cdf(1 - (1 - confidence) / 2)
    z2 = z * z

    p_hat = k / n
    denom = 1 + z2 / n
    center = p_hat + z2 / (2 * n)
    spread = z * math.sqrt((p_hat * (1 - p_hat) + z2 / (4 * n)) / n)

    lower = (center - spread) / denom
    upper = (center + spread) / denom

    return WilsonCI(
        proportion=p_hat,
        lower=max(0.0, lower),
        upper=min(1.0, upper),
        n=n,
        k=k,
        confidence=confidence,
    )


@dataclass
class McNemarResult:
    """Result of McNemar's test for paired model comparison.

    Compares two models tested on the same scenarios. The test uses
    only the discordant pairs (one model right, the other wrong).

    Attributes:
        b: Count where model A is correct, model B is incorrect.
        c: Count where model A is incorrect, model B is correct.
        chi2: McNemar's chi-squared statistic (with continuity correction).
        p_value: Two-sided p-value.
        n_concordant: Pairs where both agree (both right or both wrong).
        n_discordant: Pairs where they disagree (b + c).
        interpretation: Plain-language summary.
    """

    b: int
    c: int
    chi2: float
    p_value: float
    n_concordant: int
    n_discordant: int
    interpretation: str


def mcnemar_test(
    results_a: list[dict],
    results_b: list[dict],
    condition: str = "baseline",
) -> McNemarResult:
    """Run McNemar's test comparing two models on the same scenarios.

    Pairs trials by (scenario_id, condition, trial). Only includes
    cells present in both result lists.

    Args:
        results_a: Per-trial results from model A.
        results_b: Per-trial results from model B.
        condition: Which prompt condition to compare on.

    Returns:
        A McNemarResult with the test statistic and interpretation.
    """
    def _key(r: dict) -> tuple:
        return (r["scenario_id"], r["condition"], r["trial"])

    a_by_key = {
        _key(r): bool(r["turn_2_passed"])
        for r in results_a
        if r["condition"] == condition
    }
    b_by_key = {
        _key(r): bool(r["turn_2_passed"])
        for r in results_b
        if r["condition"] == condition
    }

    shared_keys = set(a_by_key.keys()) & set(b_by_key.keys())

    # Contingency table for discordant pairs
    b_count = 0  # A correct, B incorrect
    c_count = 0  # A incorrect, B correct
    both_pass = 0
    both_fail = 0

    for key in shared_keys:
        a_pass = a_by_key[key]
        b_pass = b_by_key[key]
        if a_pass and b_pass:
            both_pass += 1
        elif a_pass and not b_pass:
            b_count += 1
        elif not a_pass and b_pass:
            c_count += 1
        else:
            both_fail += 1

    n_discordant = b_count + c_count
    n_concordant = both_pass + both_fail

    # McNemar's test with continuity correction
    if n_discordant == 0:
        chi2 = 0.0
        p_value = 1.0
        interpretation = (
            "No discordant pairs — models agree on every scenario."
        )
    else:
        chi2 = (abs(b_count - c_count) - 1) ** 2 / (b_count + c_count)
        # Compute p-value from chi-squared distribution with df=1
        p_value = _chi2_survival(chi2, df=1)

        if p_value < 0.05:
            if c_count > b_count:
                winner = "Model B"
            else:
                winner = "Model A"
            interpretation = (
                f"Significant difference (p={p_value:.4f}). "
                f"{winner} is statistically better on the discordant "
                f"scenarios."
            )
        else:
            interpretation = (
                f"No significant difference (p={p_value:.4f}). "
                f"The {n_discordant} discordant scenarios do not provide "
                f"sufficient evidence to distinguish the two models."
            )

    return McNemarResult(
        b=b_count,
        c=c_count,
        chi2=chi2,
        p_value=p_value,
        n_concordant=n_concordant,
        n_discordant=n_discordant,
        interpretation=interpretation,
    )


def _chi2_survival(x: float, df: int = 1) -> float:
    """Compute the survival function (1 - CDF) for chi-squared.

    Uses the regularized incomplete gamma function. For df=1 this
    simplifies to 1 - erf(sqrt(x/2)).
    """
    if x <= 0:
        return 1.0
    return math.erfc(math.sqrt(x / 2))


@dataclass
class ShiftTypeBreakdown:
    """Accuracy breakdown for a single shift type (cue_type)."""

    cue_type: str
    n_scenarios: int
    n_trials: int
    n_passed: int
    accuracy: float
    ci: WilsonCI


def per_shift_type_accuracy(
    results: list[dict],
    condition: str = "baseline",
) -> list[ShiftTypeBreakdown]:
    """Compute accuracy per shift type under a given condition.

    Groups trials by cue_type, computes pass rate and Wilson CI.

    Args:
        results: Per-trial result dicts (must include `cue_type`).
        condition: Which prompt condition to filter on.

    Returns:
        List of ShiftTypeBreakdown, sorted by cue_type.
    """
    by_type: dict[str, list[dict]] = defaultdict(list)
    for r in results:
        if r["condition"] == condition:
            by_type[r["cue_type"]].append(r)

    out: list[ShiftTypeBreakdown] = []
    for cue_type in sorted(by_type.keys()):
        trials = by_type[cue_type]
        n = len(trials)
        passed = sum(1 for t in trials if bool(t["turn_2_passed"]))
        scenarios = len({t["scenario_id"] for t in trials})
        ci = wilson_ci(passed, n)
        out.append(ShiftTypeBreakdown(
            cue_type=cue_type,
            n_scenarios=scenarios,
            n_trials=n,
            n_passed=passed,
            accuracy=passed / n if n > 0 else 0.0,
            ci=ci,
        ))
    return out


@dataclass
class EmpiricalDifficulty:
    """Empirically grounded difficulty for a scenario."""

    scenario_id: str
    author_tier: str
    pass_rate: float
    n_trials: int
    empirical_tier: str


def empirical_difficulty(
    all_runs_results: list[list[dict]],
    scenario_tiers: dict[str, str],
    condition: str = "baseline",
) -> list[EmpiricalDifficulty]:
    """Ground difficulty tiers empirically from multiple run results.

    Combines trials from multiple runs for the given condition and
    computes per-scenario pass rates. Assigns empirical difficulty:
        easy:   ≥ 80% pass
        medium: 40–80% pass
        hard:   < 40% pass

    Following MMStar (Chen et al., NeurIPS 2024) protocol of
    model-performance-grounded difficulty.

    Args:
        all_runs_results: List of per-trial result lists from multiple runs.
        scenario_tiers: scenario_id → author-assigned difficulty_tier.
        condition: Which prompt condition to use.

    Returns:
        List of EmpiricalDifficulty, sorted by scenario_id.
    """
    by_scenario: dict[str, list[bool]] = defaultdict(list)

    for results in all_runs_results:
        for r in results:
            if r["condition"] == condition:
                by_scenario[r["scenario_id"]].append(bool(r["turn_2_passed"]))

    out: list[EmpiricalDifficulty] = []
    for scenario_id in sorted(by_scenario.keys()):
        outcomes = by_scenario[scenario_id]
        n = len(outcomes)
        pass_rate = sum(outcomes) / n if n > 0 else 0.0

        if pass_rate >= 0.80:
            empirical_tier = "easy"
        elif pass_rate >= 0.40:
            empirical_tier = "medium"
        else:
            empirical_tier = "hard"

        author_tier = scenario_tiers.get(scenario_id, "unknown")
        out.append(EmpiricalDifficulty(
            scenario_id=scenario_id,
            author_tier=author_tier,
            pass_rate=pass_rate,
            n_trials=n,
            empirical_tier=empirical_tier,
        ))
    return out


def minimum_detectable_effect(n: int, confidence: float = 0.95) -> float:
    """Estimate the minimum detectable effect size for a binary comparison.

    Uses the rule-of-thumb approximation for a two-proportion z-test
    at 80% power.

    Args:
        n: Number of binary observations per model.
        confidence: Confidence level.

    Returns:
        Approximate minimum detectable difference in proportions.
    """
    from statistics import NormalDist

    z_alpha = NormalDist().inv_cdf(1 - (1 - confidence) / 2)
    z_beta = NormalDist().inv_cdf(0.80)  # 80% power

    # Approximate MDE assuming p ≈ 0.5 (most conservative)
    mde = (z_alpha + z_beta) * math.sqrt(2 * 0.5 * 0.5 / n)
    return mde
