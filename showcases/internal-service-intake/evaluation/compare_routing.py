#!/usr/bin/env python3
"""Recalculate routing counterfactuals from observed CI #24 model outputs.

No model is invoked. Candidate strategy was chosen after seeing these
observations: this is exploratory analysis, NOT held-out generalization.
"""
import json
import sys
from pathlib import Path

EVALUATION = Path(__file__).resolve().parent
SHOWCASE = EVALUATION.parent
sys.path.insert(0, str(SHOWCASE / "mock-api"))
from semantic import deterministic_baseline, hybrid_decision  # noqa: E402
from study_statistics import exact_mcnemar_p  # noqa: E402


def compare_recorded() -> dict:
    evidence = json.loads((EVALUATION / "evidence" / "ci24-observed-model-output.json")
                          .read_text(encoding="utf-8"))
    cases = [json.loads(line) for line in (EVALUATION / "cases.jsonl")
             .read_text(encoding="utf-8").splitlines() if line.strip()]
    observed = evidence["model_observations"]
    if len(cases) != 36 or len(observed) != len(cases):
        raise ValueError("evidence_case_count_mismatch")
    by_id = {row["id"]: row for row in observed}
    if len(by_id) != len(cases) or set(by_id) != {c["id"] for c in cases}:
        raise ValueError("evidence_case_id_mismatch")

    names = ("model_only", "rules_only", "hybrid")
    scores = {name: {"category_correct": 0, "urgency_correct": 0,
                     "pair_correct": 0, "missed_high": 0,
                     "false_high": 0} for name in names}
    n_labeled = 0
    high_total = 0
    paired = {"both_correct": 0, "hybrid_only_correct": 0,
              "rules_only_correct": 0, "both_wrong": 0}
    for case in cases:
        obs = by_id[case["id"]]
        if case["service_type"] is None:
            continue
        n_labeled += 1
        high_total += case["urgency"] == "high"
        cat_rules, urgency_rules = deterministic_baseline(case["text"])
        cat_model = obs["model_service_type"] if obs["valid"] else None
        urgency_model = obs["model_urgency"] if obs["valid"] else None
        # Run the same hybrid decision function as the actual mock API.
        proposal = ({"service_type": cat_model, "urgency": urgency_model,
                     "summary": "Recorded synthetic inference for evaluation",
                     "missing_information": []} if obs["valid"] else None)
        # Validity of full JSON schema was already checked by CI #24; this replay
        # does not claim to reconstruct the original model summary/question text.
        hybrid = hybrid_decision(case["text"], proposal)
        predictions = {
            "model_only": (cat_model, urgency_model),
            "rules_only": (cat_rules, urgency_rules),
            "hybrid": (hybrid["category"], hybrid["urgency"]),
        }
        hybrid_correct = predictions["hybrid"] == (case["service_type"], case["urgency"])
        rules_correct = predictions["rules_only"] == (case["service_type"], case["urgency"])
        paired[("both_correct" if hybrid_correct and rules_correct
                else "hybrid_only_correct" if hybrid_correct
                else "rules_only_correct" if rules_correct else "both_wrong")] += 1
        for name, (category, urgency) in predictions.items():
            score = scores[name]
            score["category_correct"] += category == case["service_type"]
            score["urgency_correct"] += urgency == case["urgency"]
            score["pair_correct"] += ((category, urgency) ==
                                      (case["service_type"], case["urgency"]))
            score["missed_high"] += (case["urgency"] == "high" and urgency != "high")
            score["false_high"] += (case["urgency"] != "high" and urgency == "high")

    return {
        "evidence_source": evidence["source_url"],
        "source_commit": evidence["source_commit"],
        "analysis_type": "post_hoc_counterfactual_replay",
        "held_out_validation": False,
        "total_cases": len(cases),
        "labeled_cases": n_labeled,
        "ambiguous_cases": len(cases) - n_labeled,
        "high_priority_cases": high_total,
        "hybrid_vs_rules_exploratory": {
            **paired,
            "exact_two_sided_p": exact_mcnemar_p(paired["hybrid_only_correct"],
                                                paired["rules_only_correct"]),
            "confirmatory_validity": False,
            "invalid_for_confirmatory_claim": "Hybrid selected after inspecting these cases",
        },
        **scores,
        "limitations": [
            "Same observations used to propose and evaluate hybrid routing",
            "Synthetic authored labels, not a customer distribution",
            "Keyword rules miss high-urgency cases; pair accuracy hides asymmetric loss",
            "No measured customer costs, SLA evidence, prospective holdout or production approval",
        ],
    }


if __name__ == "__main__":
    print("SFS_HYBRID_REPLAY=" + json.dumps(compare_recorded(), sort_keys=True))
