#!/usr/bin/env python3
"""Verify a short, falsifiable decision narrative against frozen real observations.

This is a *documentation/evidence completeness* gate, not proof of a customer's
outcomes, an independent holdout, or current GitHub CI status. The latter needs
the independently checked successful run on the exact repository HEAD.
"""
import argparse
import json
import re
from pathlib import Path

from compare_routing import compare_recorded


def _require(condition: bool, code: str) -> None:
    if not condition:
        raise ValueError(code)


def _decision_text(brief: str) -> str:
    match = re.search(r"(?ms)^## In 30 seconds\s*\n(.*?)(?=^## |\Z)", brief)
    _require(match is not None, "30_second_section_missing")
    return match.group(1)


def word_count_in_30_second_case(brief: str) -> int:
    section = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", _decision_text(brief))
    return len(re.findall(r"[\w]+(?:[/-][\w]+)*", section, flags=re.UNICODE))


def audit_decision_case(record: dict, observed: dict, brief: str,
                        *, current_head: str | None = None,
                        successful_ci_sha: str | None = None) -> dict:
    _require(isinstance(record, dict) and record.get("id") == "DR-001",
             "decision_record_invalid")
    decision = record.get("decision") or {}
    for key in ("problem", "initial_framing", "hypothesis", "strongest_counterexample",
                "choice", "falsifier", "stop_rule"):
        _require(isinstance(decision.get(key), str) and len(decision[key].strip()) >= 20,
                 key + "_missing")
    alternatives = decision.get("alternatives")
    _require(isinstance(alternatives, list) and len(alternatives) >= 3
             and all(isinstance(x, str) and x.strip() for x in alternatives),
             "alternatives_missing")
    for key in ("operator", "ai_assistance"):
        val = (record.get("provenance") or {}).get(key)
        _require(isinstance(val, str) and len(val.strip()) >= 20,
                 "provenance_" + key + "_missing")

    n_words = word_count_in_30_second_case(brief)
    _require(n_words <= 110, "30_second_summary_too_long")
    hook = _decision_text(brief).lower()
    for literal in ("22/32", "10/32", "11/32", "5/9", "post-hoc"):
        _require(literal in hook, "30_second_summary_missing_" + literal)

    pilot = record.get("pilot") or {}
    _require(pilot.get("total") == observed["total_cases"]
             and pilot.get("labeled") == observed["labeled_cases"],
             "pilot_sample_mismatch")
    _require(pilot.get("verified_commit") == observed["source_commit"]
             and pilot.get("verified_run") == observed["evidence_source"],
             "pilot_evidence_provenance_mismatch")
    for name in ("model_only", "rules_only", "hybrid"):
        for field, observed_key in (("joint_correct", "pair_correct"),
                                    ("missed_high", "missed_high"),
                                    ("false_high", "false_high")):
            _require((pilot.get(field) or {}).get(name) == observed[name][observed_key],
                     "pilot_" + field + "_" + name + "_mismatch")
    _require(pilot.get("analysis_type") == "post_hoc_exploratory"
             and pilot.get("independent_holdout") is False,
             "pilot_selection_bias_not_disclosed")
    _require((observed.get("hybrid_vs_rules_exploratory") or {}).get(
                "confirmatory_validity") is False,
             "pilot_cannot_support_confirmatory_claim")
    econ = record.get("economics") or {}
    more_misses = observed["hybrid"]["missed_high"] - observed["model_only"]["missed_high"]
    fewer_false_alarms = (observed["model_only"]["false_high"]
                          - observed["hybrid"]["false_high"])
    _require(more_misses > 0 and econ.get("illustrative_break_even_cost_ratio") ==
             fewer_false_alarms / more_misses and
             econ.get("observed_customer_costs") is False,
             "business_proxy_without_evidence")
    boundaries = record.get("boundaries") or {}
    _require(boundaries.get("customer_economic_validation") == "NOT_ESTABLISHED",
             "customer_economics_must_not_be_claimed")
    _require(boundaries.get("prospective_holdout") == "NOT_COLLECTED",
             "holdout_not_collected")
    _require(boundaries.get("production_deployment") == "NONE",
             "deployment_not_evidenced")
    _require(boundaries.get("current_head_ci") == "PENDING",
             "current_head_status_requires_actual_ci_run")
    artifacts = record.get("artifacts") or {}
    _require(all(isinstance(artifacts.get(k), str) and artifacts[k].strip()
                 for k in ("entry", "method", "prospective_plan", "implementation",
                           "counterfactual", "sensitivity", "source")),
             "evidence_artifact_index_incomplete")

    # A caller-supplied SHA is conditional metadata, not independently verified
    # via the GitHub API. This function never fabricates successful workflow runs.
    valid_head = (isinstance(current_head, str)
                  and re.fullmatch("[a-fA-F0-9]{40}", current_head) is not None)
    sha_claim_matches = bool(valid_head and successful_ci_sha == current_head)
    # An unsigned user-provided SHA cannot attest a GitHub job's conclusion.
    # The caller must independently inspect the GitHub Actions API/UI.
    return {
        "case_id": record["id"],
        "30_second_word_count": n_words,
        "documented": True,
        "pilot_counts_reconciled": True,
        "limits_disclosed": True,
        "ci_sha_claim_matches_head": sha_claim_matches,
        "current_head_ci_verified": False,
        "economically_validated": False,
        "prospective_independent_validation": False,
        "next_gate": ("INDEPENDENT_GITHUB_CI_CONCLUSION_CHECK_REQUIRED"
                      if sha_claim_matches else "WAIT_FOR_EXACT_HEAD_CI"),
        "verification_note": ("A matching SHA is not proof of a completed successful run. "
                              "The GitHub Actions conclusion must be checked independently "
                              "on the exact current HEAD."),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Audit decision case, not production readiness")
    parser.add_argument("--current-head", help="Current full SHA, for status comparison only")
    parser.add_argument("--successful-ci-sha", help="Independently verified successful full SHA")
    args = parser.parse_args()
    showcase = Path(__file__).resolve().parents[1]
    record = json.loads((showcase / "DECISION_CASE.json").read_text(encoding="utf-8"))
    brief = (showcase / "DECISION_EVIDENCE_BRIEF.md").read_text(encoding="utf-8")
    output = audit_decision_case(record, compare_recorded(), brief,
                                 current_head=args.current_head,
                                 successful_ci_sha=args.successful_ci_sha)
    print(json.dumps(output, indent=2))
