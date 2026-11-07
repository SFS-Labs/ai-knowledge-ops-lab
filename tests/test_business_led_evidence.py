"""Enforce business-first research; prevent mixing two independent data sources."""
import copy
import csv
from io import StringIO
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1] / "showcases/internal-service-intake/evaluation"
sys.path.insert(0, str(ROOT))
from research_methods import load_contract, validate_contract, scenario_labour_savings  # noqa: E402
from nlbse_source import profile_csv_bytes, EXPECTED  # noqa: E402


class EvidenceStreamTests(unittest.TestCase):
    def test_label_taxonomy_is_actual_source_and_not_legacy_four_domains(self):
        c = load_contract()
        self.assertEqual({"bug", "feature", "question", "documentation"},
                         set(c["streams"]["classification"]["labels"]))
        self.assertNotEqual(
            {"analytics", "automation", "integration", "incident-response"},
            set(c["streams"]["classification"]["labels"]))
        self.assertEqual("NOT_MEASURED on NLBSE labels",
                         c["streams"]["classification"]["model_results"])

    def test_relabeling_original_classes_to_old_sales_story_fails(self):
        c = load_contract()
        c["streams"]["classification"]["labels"] = [
            "analytics", "automation", "integration", "incident-response"]
        with self.assertRaisesRegex(ValueError, "unsubstantiated_class_mapping"):
            validate_contract(c)

    def test_erasing_unlinked_datasets_or_causal_limit_fails(self):
        for k in ("cross_source_limit", "causal_limit"):
            c = load_contract()
            c["economics"][k] = "Claims observed ROI"
            with self.assertRaises(ValueError):
                validate_contract(c)

    def test_no_measured_cost_is_manufactured_from_wall_clock(self):
        result = scenario_labour_savings(
            observed_handoffs=100, assumed_avoidable_fraction=.2,
            assumed_minutes_saved=10, hourly_reference_eur=58.5)
        self.assertAlmostEqual(result["hypothetical_gross_cost_avoided_eur"], 195)
        self.assertIsNone(result["realized_customer_savings"])
        self.assertFalse(result["causal_proof"])
        self.assertEqual("unknown", result["additional_costs_completeness"])

    def test_input_sensitivity_and_limits(self):
        low = scenario_labour_savings(
            observed_handoffs=100, assumed_avoidable_fraction=.1,
            assumed_minutes_saved=10)
        high = scenario_labour_savings(
            observed_handoffs=100, assumed_avoidable_fraction=.4,
            assumed_minutes_saved=10)
        self.assertAlmostEqual(high["hypothetical_gross_cost_avoided_eur"],
                               4 * low["hypothetical_gross_cost_avoided_eur"])
        for change in ({"assumed_avoidable_fraction":-1},
                       {"assumed_avoidable_fraction":1.2},
                       {"assumed_minutes_saved":-5},
                       {"observed_handoffs":-7}):
            args={"observed_handoffs":100, "assumed_avoidable_fraction":.2,
                  "assumed_minutes_saved":10}
            args.update(change)
            with self.assertRaises(ValueError):
                scenario_labour_savings(**args)

    def test_source_annotated_csv_preserves_original_class_names(self):
        source = b"id,title,body,label\n100,Bug fix,There is an outage,bug\n101,Feature,New feature,feature\n102,Q,How to configure,question\n103,Doc,Doc typo,documentation\n"
        result = profile_csv_bytes(source, require_published_counts=False)
        self.assertEqual(4, result["observed_issue_count"])
        self.assertEqual(4, len(result["observed_source_label_counts"]))
        self.assertFalse(result["official_full_test_checked"])
        self.assertIsNone(result["observed_test_model_accuracy"])

    def test_unlicensed_new_mapping_and_unknown_label_are_rejected(self):
        rows=b"id,title,body,label\n100,Bug,Example,incident-response\n"
        with self.assertRaisesRegex(ValueError, "unexpected_source_label"):
            profile_csv_bytes(rows, require_published_counts=False)

    def test_short_sample_never_claims_official_full_benchmark(self):
        rows=b"id,title,body,label\n100,Bug,Example,bug\n"
        with self.assertRaisesRegex(ValueError,"official_test_set_distribution_mismatch"):
            profile_csv_bytes(rows)

    def test_duplicate_issue_ids_fail_closed(self):
        rows=b"id,title,body,label\n100,Bug,Example,bug\n100,Bug,Example,bug\n"
        with self.assertRaisesRegex(ValueError,"duplicated_source_issue_id"):
            profile_csv_bytes(rows, require_published_counts=False)


if __name__ == "__main__":
    unittest.main()
