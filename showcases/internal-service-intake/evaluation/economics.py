#!/usr/bin/env python3
"""Conditional economic loss frontier over the frozen 32 labeled pilot cases.

This is a NON-PRODUCTION proxy, not measured customer cost/ROI. Reviews,
real prevalence, uptime, integration costs, and avoided labor are unobserved.
It is invalid to call the cheapest strategy economically optimal in business
without independent cost estimates and a representative prospective sample.
"""
import argparse
import json
import math
from compare_routing import compare_recorded


def loss_proxy(
    counts: dict, *, n_labeled: int, llm_calls: int,
    category_misroute_cost: float, missed_high_cost: float,
    false_high_cost: float, inference_cost: float,
) -> float:
    """Conditional sum of explicit, deliberately incomplete loss components."""
    costs = (category_misroute_cost, missed_high_cost, false_high_cost, inference_cost)
    if any(not isinstance(x, (int, float)) or isinstance(x, bool) or
           not math.isfinite(x) or x < 0 for x in costs):
        raise ValueError("costs must be finite, nonnegative scenario inputs")
    if (not isinstance(n_labeled, int) or n_labeled < 1 or
            not isinstance(llm_calls, int) or not (0 <= llm_calls <= n_labeled)):
        raise ValueError("invalid sample size or LLM call count")
    category_correct = counts["category_correct"]
    missed_high = counts["missed_high"]
    false_high = counts["false_high"]
    if (not all(isinstance(x, int) and 0 <= x <= n_labeled
                for x in (category_correct, missed_high, false_high))):
        raise ValueError("invalid observed prediction counts")
    return (
        (n_labeled - category_correct) * category_misroute_cost
        + missed_high * missed_high_cost
        + false_high * false_high_cost
        + llm_calls * inference_cost
    )


def critical_cost_ratio(*, extra_misses: int,
                        avoided_false_escalations: int) -> float:
    """FN/FP break-even ratio when all other costs and quality are unchanged."""
    if (not isinstance(extra_misses, int) or extra_misses <= 0
            or not isinstance(avoided_false_escalations, int)
            or avoided_false_escalations < 0):
        raise ValueError("invalid incremental error counts")
    return avoided_false_escalations / extra_misses


def evaluate_observed(report: dict, *, category_misroute_cost: float,
                      missed_high_cost: float, false_high_cost: float,
                      inference_cost: float) -> dict:
    n = report["labeled_cases"]
    losses = {}
    for policy in ("model_only", "rules_only", "hybrid"):
        calls = n if policy != "rules_only" else 0
        losses[policy] = round(loss_proxy(
            report[policy], n_labeled=n, llm_calls=calls,
            category_misroute_cost=category_misroute_cost,
            missed_high_cost=missed_high_cost,
            false_high_cost=false_high_cost,
            inference_cost=inference_cost), 6)
    return {
        "sample": "32 labeled synthetic cases, post-hoc, not representative",
        "hypothetical_cost_parameters": {
            "wrong_category": category_misroute_cost,
            "missed_high": missed_high_cost,
            "false_high": false_high_cost,
            "per_llm_call": inference_cost,
        },
        "modeled_loss_units_by_strategy": losses,
        "lowest_cost_proxy_strategy": min(losses, key=losses.get),
        "proves_business_optimality": False,
        "unobserved_necessary_costs": [
            "human_triage_and_approval_time_per_route",
            "actual_tickets_prevalence_and_SLA",
            "implementation_operations_monitoring",
            "escalation_and_rework_costs",
            "costs_of_medium_vs_low_misclassification",
            "customer_impact_and_data_protection",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Illustrative cost frontier; no real-world optimality claim")
    parser.add_argument("--category-cost", type=float)
    parser.add_argument("--missed-high-cost", type=float)
    parser.add_argument("--false-high-cost", type=float)
    parser.add_argument("--inference-cost", type=float)
    args = parser.parse_args()
    arguments = (args.category_cost, args.missed_high_cost,
                 args.false_high_cost, args.inference_cost)
    if any(v is None for v in arguments):
        # Abstain from ranking policies absent user-supplied cost assumptions.
        print(json.dumps({
            "status": "cost_assumptions_missing",
            "observed_counts_only": compare_recorded(),
            "hybrid_vs_model_missed_high_increase": 4,
            "hybrid_vs_model_false_high_decrease": 21,
            "hybrid_vs_model_breakeven_FN_to_FP_ratio": critical_cost_ratio(
                extra_misses=4, avoided_false_escalations=21),
            "hybrid_vs_rules_fewer_category_errors": 17,
            "not_claimed": "business_optimum_or_ROI",
        }, indent=2))
    else:
        print(json.dumps(evaluate_observed(
            compare_recorded(), category_misroute_cost=args.category_cost,
            missed_high_cost=args.missed_high_cost,
            false_high_cost=args.false_high_cost,
            inference_cost=args.inference_cost), indent=2))
