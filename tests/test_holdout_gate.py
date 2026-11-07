"""Prevent fake-n inflation and missing label provenance before held-out inference."""
import copy
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / "showcases" / "internal-service-intake" / "evaluation"
sys.path.insert(0, str(HERE))
from holdout_gate import audit_holdout  # noqa: E402


def build_sample():
    rows = []
    for language in ("DE", "EN"):
        for category in ("analytics", "automation", "integration", "incident-response"):
            for urgency in ("low", "medium", "high"):
                i = len(rows)
                text = (f"Independent {language} client scenario {i}: investigate a distinct "
                        f"operational requirement in {category} with {urgency} priority.")
                rows.append({
                    "id": f"HOLD-{i:04d}", "language": language, "text": text,
                    "category": category, "urgency": urgency,
                    "source_family": f"distinct-case-origin-{i}",
                    "labelers": ["independent-reviewer-A", "independent-reviewer-B"],
                    "labeler_a_category": category, "labeler_a_urgency": urgency,
                    "labeler_b_category": category, "labeler_b_urgency": urgency,
                    "adjudicated_category": category, "adjudicated_urgency": urgency,
                    "adjudication_reason": "Synthetic test case with matching reviewer labels",
                })
    return rows


class HoldoutGateTests(unittest.TestCase):
    def test_complete_strata_pass_auditable_structural_gate(self):
        report = audit_holdout(build_sample(), min_per_cell=1)
        self.assertEqual(24, report["cases"])
        self.assertEqual(24, report["strata"])
        self.assertEqual(24, report["unique_source_families"])
        self.assertFalse(report["proves_independence_or_label_validity"])

    def test_one_duplicated_source_family_fails(self):
        cases = build_sample()
        cases[1]["source_family"] = cases[0]["source_family"]
        with self.assertRaisesRegex(ValueError, "source_family"):
            audit_holdout(cases, min_per_cell=1)

    def test_recycled_case_text_fails(self):
        cases = build_sample()
        cases[1]["text"] = cases[0]["text"]
        with self.assertRaisesRegex(ValueError, "duplicate_text"):
            audit_holdout(cases, min_per_cell=1)

    def test_one_missing_stratum_fails(self):
        with self.assertRaisesRegex(ValueError, "stratum"):
            audit_holdout(build_sample()[:-1], min_per_cell=1)

    def test_adjudication_trace_is_required(self):
        cases = build_sample()
        del cases[0]["labeler_a_category"]
        with self.assertRaisesRegex(ValueError, "label"):
            audit_holdout(cases, min_per_cell=1)

    def test_claimed_two_reviewers_must_be_distinct(self):
        cases = build_sample()
        cases[0]["labelers"] = ["same-reviewer", "same-reviewer"]
        with self.assertRaisesRegex(ValueError, "labelers"):
            audit_holdout(cases, min_per_cell=1)


if __name__ == "__main__":
    unittest.main()
