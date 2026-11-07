#!/usr/bin/env python3
"""Study design utilities; exploratory pilot is NOT a confirmatory test.

Use the exact McNemar binomial distribution for paired binary outcomes.
Approximate sample size depends on *prespecified* plausible discordance and
effect; no sample size alone guarantees significance or generalizability.
"""
import json
import math
import statistics


def exact_mcnemar_p(a_only: int, b_only: int) -> float:
    """Two-sided exact paired comparison from discordant counts.

    The test treats distinct *pairs* as independent; testing multiple
    near-duplicate generated prompts as independent is invalid. This code does
    not determine whether pre-registration or independence is satisfied.
    """
    if (not isinstance(a_only, int) or isinstance(a_only, bool)
            or not isinstance(b_only, int) or isinstance(b_only, bool)
            or a_only < 0 or b_only < 0):
        raise ValueError("discordant counts must be nonnegative integers")
    discordant = a_only + b_only
    if discordant == 0:
        return 1.0
    lower = min(a_only, b_only)
    log_probability_of_half = -discordant * math.log(2.0)
    # Log-gamma avoids overflow from combinations for larger future datasets.
    lower_tail = math.fsum(
        math.exp(math.lgamma(discordant + 1) - math.lgamma(k + 1)
                 - math.lgamma(discordant - k + 1) + log_probability_of_half)
        for k in range(lower + 1)
    )
    return min(1.0, 2.0 * lower_tail)


def approximate_paired_sample_size(
        *, minimum_effect: float, discordance_rate: float, alpha: float = 0.05,
        power: float = 0.80, design_effect: float = 1.0) -> int:
    """Planning approximation for paired binary outcomes, not a guarantee.

    minimum_effect = absolute (A-only - B-only) probability under H1.
    discordance_rate = P(A-only)+P(B-only). Must exceed the assumed effect.
    design_effect is an externally justified inflation for dependence;
    setting it to 1.3 does NOT correct unknown clustering by itself.
    """
    vals = [minimum_effect, discordance_rate, alpha, power, design_effect]
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
               and math.isfinite(v) for v in vals):
        raise ValueError("all parameters must be finite numbers")
    if not (0 < minimum_effect <= discordance_rate <= 1):
        raise ValueError("require 0 < effect <= discordance <= 1")
    if not (0 < alpha < 1 and 0.5 < power < 1 and design_effect >= 1):
        raise ValueError("alpha, power or design effect outside valid range")
    z_alpha = statistics.NormalDist().inv_cdf(1 - alpha / 2)
    z_power = statistics.NormalDist().inv_cdf(power)
    n = design_effect * (z_alpha + z_power) ** 2 * discordance_rate / minimum_effect ** 2
    return math.ceil(n)


if __name__ == "__main__":
    print(json.dumps({
        "observed_pilot": {
            "paired_comparison": "hybrid_vs_rules_on_32_labeled_cases",
            "hybrid_only_correct": 12, "rules_only_correct": 1,
            "exact_two_sided_p": exact_mcnemar_p(12, 1),
            "analysis_type": "exploratory_post_hoc_NOT_confirmatory",
        },
        "prospective_planning_assumptions_NOT_findings": {
            "alpha_two_sided": 0.05, "power_target": 0.80,
            "minimum_detectable_absolute_difference": 0.08,
            "assumed_discordance": 0.30,
            "hypothetical_design_effect": 1.30,
            "approximate_number_of_independent_pairs": approximate_paired_sample_size(
                minimum_effect=0.08, discordance_rate=0.30,
                alpha=0.05, power=0.80, design_effect=1.30),
            "at_five_point_effect": approximate_paired_sample_size(
                minimum_effect=0.05, discordance_rate=0.30,
                alpha=0.05, power=0.80, design_effect=1.30),
            "warning": "These assumptions require justification, independence verification and a locked protocol."
        },
    }, indent=2))
