"""Proof of the hybrid decision hypothesis and its business-risk counterexamples.
No model calls; frozen observations come from real CI #24 CPU inference.
"""
import importlib.util
import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOWCASE = ROOT / "showcases" / "internal-service-intake"
sys.path.insert(0, str(SHOWCASE / "mock-api"))
from semantic import hybrid_decision, semantic_register  # noqa: E402


def model_response(category="analytics", urgency="medium", missing=None):
    proposal = {"service_type": category, "urgency": urgency,
                "summary": "A synthetic customer request for analysis",
                "missing_information": [] if missing is None else missing}
    return {"choices": [{"message": {"content": json.dumps(proposal)}}]}


class StubStore:
    def __init__(self):
        self.last = None

    def register(self, registration):
        self.last = registration
        return {"request_id": registration["request_id"],
                "status": "pending", "classification": registration["classification"]}


class HybridDecisionTests(unittest.TestCase):
    def test_category_from_valid_llm_urgency_from_deterministic_rule(self):
        result = hybrid_decision(
            "We need a dashboard with weekly operational reporting.",
            {"service_type": "analytics", "urgency": "high",
             "summary": "Synthetic weekly reporting dashboard",
             "missing_information": []})
        self.assertEqual("analytics", result["category"])
        self.assertEqual("medium", result["urgency"])
        self.assertEqual("validated_llm", result["category_source"])
        self.assertEqual("deterministic_rule", result["urgency_source"])
        self.assertEqual("manual_review", result["policy_decision"])
        self.assertEqual("urgency_signal_disagreement", result["review_reason"])
        self.assertTrue(result["urgency_disagreement"])

    def test_high_sla_keyword_is_not_silently_downgraded(self):
        valid = {"service_type": "analytics", "urgency": "high",
                 "summary": "Urgent synthetic operational report",
                 "missing_information": []}
        result = hybrid_decision("Bitte dringend heute einen Bericht erstellen.", valid)
        self.assertEqual("high", result["urgency"])
        self.assertEqual("expedite_review", result["policy_decision"])
        valid["urgency"] = "low"
        result = hybrid_decision("Bitte dringend heute einen Bericht erstellen.", valid)
        self.assertEqual("high", result["urgency"])
        self.assertEqual("manual_review", result["policy_decision"])

    def test_invalid_model_never_falls_back_to_unreviewed_automatic_action(self):
        result = hybrid_decision("Urgent customer support request.", None)
        self.assertIsNone(result["category"])
        self.assertIsNone(result["urgency"])
        self.assertEqual("manual_review", result["policy_decision"])
        self.assertEqual("invalid_model_output", result["review_reason"])

    def test_missing_information_requires_manual_review(self):
        result = hybrid_decision("Build weekly analytics reporting.", {
            "service_type": "analytics", "urgency": "medium",
            "summary": "A weekly reporting dashboard request",
            "missing_information": ["Which CRM system?"]})
        self.assertEqual("manual_review", result["policy_decision"])
        self.assertEqual("missing_information", result["review_reason"])

    def test_real_registration_persists_verifiable_source_attribution(self):
        store = StubStore()
        body = {
            "request_id": "REQ-HYBRID-001", "requester": "synthetic-reviewer",
            "free_text": "We need a weekly dashboard for customer account data.",
            "model_response": model_response("analytics", "high"),
        }
        code, reply = semantic_register(store, body)
        self.assertEqual(200, code)
        self.assertEqual("manual_review", reply["classification"])
        decision = store.last["payload"]["decision_trace"]
        self.assertEqual("analytics", decision["category"])
        self.assertEqual("medium", decision["urgency"])
        self.assertEqual("high", decision["model_urgency"])
        self.assertEqual("manual_review", store.last["classification"])
        self.assertNotIn("approval", decision)
        self.assertNotIn("applied", decision)

    def test_ci24_replay_proves_retrospective_22_of_32_and_high_risk(self):
        script = SHOWCASE / "evaluation" / "compare_routing.py"
        spec = importlib.util.spec_from_file_location("compare_routing", script)
        self.assertIsNotNone(spec)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        report = module.compare_recorded()
        self.assertEqual(36, report["total_cases"])
        self.assertEqual(32, report["labeled_cases"])
        self.assertEqual(10, report["model_only"]["pair_correct"])
        self.assertEqual(11, report["rules_only"]["pair_correct"])
        self.assertEqual(22, report["hybrid"]["pair_correct"])
        self.assertEqual(5, report["hybrid"]["missed_high"])
        self.assertFalse(report["held_out_validation"])


if __name__ == "__main__":
    unittest.main()
