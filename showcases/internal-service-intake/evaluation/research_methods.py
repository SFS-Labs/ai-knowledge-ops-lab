#!/usr/bin/env python3
"""Business-led research contract: honest, independent evidence streams.

This intentionally does NOT pretend to join unlinked issues and incident logs.
Class labels reflect original NLBSE harmonized GitHub issue-type annotations;
Volvo attributes belong to a different population and business process.
"""
from pathlib import Path
import json
import math

HERE = Path(__file__).resolve().parent
EXPECTED_CLASSES = frozenset(("bug", "feature", "question", "documentation"))
ORIGINAL_DOMAINS = frozenset(("analytics", "automation", "integration", "incident-response"))


def load_contract(path=HERE / "research_contract.json"):
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    validate_contract(doc)
    return doc


def validate_contract(c):
    if not c["business_problem"]["statement"].strip():
        raise ValueError("missing_business_problem")
    labels = c["business_problem"]["dimensions"]["request_type"]
    if frozenset(labels) != EXPECTED_CLASSES or len(labels) != len(EXPECTED_CLASSES):
        raise ValueError("labels_not_NLBSE_harmonized")
    observed = c["streams"]["classification"]["labels"]
    if observed != labels:
        raise ValueError("unsubstantiated_class_mapping")
    if frozenset(observed) == ORIGINAL_DOMAINS:
        raise ValueError("legacy_domains_must_not_be_claimed_as_source_labels")
    assert c["streams"]["operations"]["id"] != c["streams"]["classification"]["id"]
    if c["economics"]["cross_source_limit"].find("No row-level join") < 0:
        raise ValueError("missing_unlinked_population_limit")
    if c["economics"]["causal_limit"].find("cannot claim") < 0:
        raise ValueError("causal_limit_required")
    return True


def scenario_labour_savings(*, observed_handoffs, assumed_avoidable_fraction,
                            assumed_minutes_saved, hourly_reference_eur=58.5,
                            additional_measured_cost_eur=0):
    """Illustrative scenario, explicitly NOT observed intervention effect or ROI.

    Uses number of *observed* group transitions, not duration between events.
    Positive avoided share and saved minutes are assumed counterfactual inputs.
    """
    values = (observed_handoffs, assumed_avoidable_fraction, assumed_minutes_saved,
              hourly_reference_eur, additional_measured_cost_eur)
    if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
               and math.isfinite(v) for v in values):
        raise ValueError("numeric_inputs_required")
    if (observed_handoffs < 0 or int(observed_handoffs) != observed_handoffs or
            not 0 <= assumed_avoidable_fraction <= 1 or
            assumed_minutes_saved < 0 or hourly_reference_eur < 0 or
            additional_measured_cost_eur < 0):
        raise ValueError("inputs_out_of_range")
    hours = (observed_handoffs * assumed_avoidable_fraction *
             assumed_minutes_saved / 60.0)
    gross = hours * hourly_reference_eur
    return {
        "source_metric": "observed group transitions (not actual reductions)",
        "observed_handoffs": int(observed_handoffs),
        "assumption_avoidable_share": assumed_avoidable_fraction,
        "assumption_minutes_saved_per_avoided_handoff": assumed_minutes_saved,
        "reference_eur_per_hour": hourly_reference_eur,
        "hypothetical_avoided_hours": round(hours, 3),
        "hypothetical_gross_cost_avoided_eur": round(gross, 2),
        "hypothetical_net_after_entered_cost_eur": round(gross - additional_measured_cost_eur, 2),
        "additional_costs_completeness": "unknown",
        "realized_customer_savings": None,
        "causal_proof": False,
        "validity_warning": "Observed handoffs are not proved avoidable; labour minutes are scenario inputs, not Volvo observations.",
    }


if __name__ == "__main__":
    c = load_contract()
    print(json.dumps({"status":"contract_verified",
                      "business_problem":c["business_problem"]["id"],
                      "classification_labels":c["streams"]["classification"]["labels"],
                      "streams_unlinked":True,
                      "observed_customer_roi":False}, indent=2))
