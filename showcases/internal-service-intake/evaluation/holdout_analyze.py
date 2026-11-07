#!/usr/bin/env python3
"""Paired evaluation after a held-out, pre-inference lock exists.

Does not generate or infer any examples. Reporting statistical p-values is
conditional on independent observations, locked hypotheses and credible
adjudicated labels; this script cannot establish those conditions itself.
"""
import argparse
import json
import random
from pathlib import Path
from holdout_gate import audit_holdout, inspect_locked_file, CATEGORIES, URGENCIES
from study_statistics import exact_mcnemar_p

# Reuse the *actual* implemented deterministic baseline, not a local copy.
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "mock-api"))
from semantic import deterministic_baseline  # noqa: E402


def _paired(a: list[bool], b: list[bool]) -> dict:
    if len(a) != len(b):
        raise ValueError("pair_count_mismatch")
    a_only = sum(x and not y for x, y in zip(a, b))
    b_only = sum(y and not x for x, y in zip(a, b))
    both = sum(x and y for x, y in zip(a, b))
    neither = len(a) - (a_only + b_only + both)
    return {
        "both_correct": both, "a_only_correct": a_only,
        "b_only_correct": b_only, "both_wrong": neither,
        "difference_proportion": round((a_only - b_only) / len(a), 6),
        "exact_mcnemar_two_sided_p": exact_mcnemar_p(a_only, b_only),
    }


def evaluate_locked_predictions(
    gold: list[dict], observations: list[dict], *, min_per_cell: int = 20
) -> dict:
    gate = audit_holdout(gold, min_per_cell=min_per_cell)
    indexed = {}
    for row in observations:
        if not isinstance(row, dict):
            raise ValueError("invalid_prediction_record")
        key = row.get("id")
        if not isinstance(key, str) or key in indexed:
            raise ValueError("duplicate_or_invalid_prediction_id")
        valid = row.get("valid")
        if not isinstance(valid, bool):
            raise ValueError("prediction_validity_missing")
        if valid and (row.get("service_type") not in CATEGORIES
                      or row.get("urgency") not in URGENCIES):
            raise ValueError("valid_prediction_missing_fields")
        indexed[key] = row
    ids = {row["id"] for row in gold}
    if len(observations) != len(gold) or set(indexed) != ids:
        raise ValueError("prediction_ids_incomplete_or_mismatched")

    variants = ("rules_only", "llm_only", "hybrid")
    stats = {key: {"both_correct": 0, "category_correct": 0,
                   "urgency_correct": 0, "missed_high": 0, "false_high": 0}
             for key in variants}
    correctness = {key: [] for key in variants}
    for item in gold:
        m = indexed[item["id"]]
        model_cat = m["service_type"] if m["valid"] else None
        model_urgency = m["urgency"] if m["valid"] else None
        rule_cat, rule_urgency = deterministic_baseline(item["text"])
        candidates = {
            "rules_only": (rule_cat, rule_urgency),
            "llm_only": (model_cat, model_urgency),
            "hybrid": (model_cat, rule_urgency),
        }
        for name, (cat, urgency) in candidates.items():
            s = stats[name]
            s["category_correct"] += cat == item["category"]
            s["urgency_correct"] += urgency == item["urgency"]
            match = (cat, urgency) == (item["category"], item["urgency"])
            s["both_correct"] += match
            correctness[name].append(match)
            s["missed_high"] += item["urgency"] == "high" and urgency != "high"
            s["false_high"] += item["urgency"] != "high" and urgency == "high"

    return {
        "n": len(gold), "structural_holdout_gate": gate,
        **stats,
        "hybrid_vs_rules": _paired(correctness["hybrid"], correctness["rules_only"]),
        "hybrid_vs_llm": _paired(correctness["hybrid"], correctness["llm_only"]),
        "verified_customer_representativeness": False,
        "proves_business_optimality": False,
        "model_calls_observed_by_this_script": False,
        "mandatory_manual_checks": [
            "human independent labeling, pre-inference lock timing, case-family independence",
            "client case-mix weights, cost matrix, human-review time and SLA safety thresholds",
            "stable prompt/model provenance and fixed analysis plan",
        ],
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Report pre-registered paired results only after holdout provenance is secured")
    parser.add_argument("--gold", type=Path, required=True)
    parser.add_argument("--locked-gold-sha256", required=True)
    parser.add_argument("--predictions", type=Path, required=True)
    args = parser.parse_args()
    inspect_locked_file(args.gold, args.locked_gold_sha256)
    gold = [json.loads(line) for line in args.gold.read_text(encoding="utf-8").splitlines()
            if line.strip()]
    predictions = [json.loads(line) for line in
                   args.predictions.read_text(encoding="utf-8").splitlines() if line.strip()]
    report = evaluate_locked_predictions(gold, predictions)
    print(json.dumps(report, indent=2, sort_keys=True))
