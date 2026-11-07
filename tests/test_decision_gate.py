"""Gate the 30-second scientific decision work sample against its actual pilot.

No live model requests, no GitHub action dispatch, no production authorization.
"""
import copy
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOWCASE = ROOT / "showcases" / "internal-service-intake"
sys.path.insert(0, str(SHOWCASE / "evaluation"))
from compare_routing import compare_recorded  # noqa: E402
from decision_gate import audit_decision_case, word_count_in_30_second_case  # noqa: E402


class DecisionGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads((SHOWCASE / "DECISION_CASE.json").read_text(encoding="utf-8"))
        cls.brief = (SHOWCASE / "DECISION_EVIDENCE_BRIEF.md").read_text(encoding="utf-8")
        cls.pilot = compare_recorded()

    def test_30_second_hook_is_short_and_contains_costly_counterexample(self):
        count = word_count_in_30_second_case(self.brief)
        self.assertLessEqual(count, 110)
        for required in ("22/32", "10/32", "11/32", "5/9", "post-hoc"):
            self.assertIn(required, self.brief.split("## In 30 seconds", 1)[1].split("\n## ", 1)[0])

    def test_complete_evidence_record_matches_frozen_genuine_inferences(self):
        report = audit_decision_case(self.record, self.pilot, self.brief)
        self.assertTrue(report["documented"])
        self.assertTrue(report["pilot_counts_reconciled"])
        self.assertTrue(report["limits_disclosed"])
        self.assertFalse(report["current_head_ci_verified"])
        self.assertEqual("WAIT_FOR_EXACT_HEAD_CI", report["next_gate"])

    def test_marketing_inflation_does_not_pass(self):
        wrong = copy.deepcopy(self.record)
        wrong["pilot"]["joint_correct"]["hybrid"] = 25
        with self.assertRaisesRegex(ValueError, "pilot"):
            audit_decision_case(wrong, self.pilot, self.brief)

    def test_unknown_client_roi_must_not_be_described_as_verified(self):
        wrong = copy.deepcopy(self.record)
        wrong["boundaries"]["customer_economic_validation"] = "VERIFIED"
        with self.assertRaisesRegex(ValueError, "customer"):
            audit_decision_case(wrong, self.pilot, self.brief)

    def test_no_exact_head_ci_claim_on_historical_ci(self):
        head = "a" * 40
        old = self.record["pilot"]["verified_commit"]
        self.assertNotEqual(head, old)
        report = audit_decision_case(self.record, self.pilot, self.brief,
                                     current_head=head, successful_ci_sha=old)
        self.assertFalse(report["current_head_ci_verified"])

    def test_exact_head_ci_is_only_conditional_evidence_not_customer_proof(self):
        head = "a" * 40
        report = audit_decision_case(self.record, self.pilot, self.brief,
                                     current_head=head, successful_ci_sha=head)
        self.assertTrue(report["ci_sha_claim_matches_head"])
        self.assertFalse(report["current_head_ci_verified"])
        self.assertEqual("INDEPENDENT_GITHUB_CI_CONCLUSION_CHECK_REQUIRED",
                         report["next_gate"])
        self.assertFalse(report["economically_validated"])

    def test_recruiter_sees_the_counterexample_before_the_technical_readme(self):
        opening = (ROOT / "README.md").read_text(encoding="utf-8")[:1050]
        self.assertIn("30-second decision sample", opening)
        self.assertIn("22/32", opening)
        self.assertIn("5/9", opening)
        self.assertIn("DECISION_EVIDENCE_BRIEF.md", opening)
        self.assertIn("await exact-HEAD CI", opening)

    def test_scope_does_not_make_480_cases_or_customer_roi_a_job_entry_gate(self):
        document = (SHOWCASE / "HYBRID_DECISION_RECORD.md").read_text(encoding="utf-8")
        self.assertIn("Binding completion standard", document)
        self.assertIn("optional future evidence gates, not prerequisites for paid market entry",
                      document)
        self.assertIn("current hybrid/method changes", document)

    def test_missing_falsifier_or_alternative_blocks_documentation(self):
        for key in ("hypothesis", "strongest_counterexample", "falsifier"):
            with self.subTest(key=key):
                wrong = copy.deepcopy(self.record)
                wrong["decision"][key] = ""
                with self.assertRaisesRegex(ValueError, key):
                    audit_decision_case(wrong, self.pilot, self.brief)


if __name__ == "__main__":
    unittest.main()
