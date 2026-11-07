"""Deterministic tests; do not require downloading or simulating model weights."""
import json
import sys
import unittest
from pathlib import Path

MOD = Path(__file__).resolve().parents[1] / "showcases/internal-service-intake/mock-api"
sys.path.insert(0, str(MOD))
from semantic import (validate_free_text, text_hash, examine_model_response,  # noqa: E402
                      validate_proposal, deterministic_baseline, EXTRACTION_SCHEMA,
                      model_transport_diagnostic)


class SemanticIntakeTests(unittest.TestCase):
    @staticmethod
    def free_text():
        return {"request_id": "REQ-TEXT-001", "requester": "synthetic",
                "free_text": "We need a dashboard using weekly sales information."}

    @staticmethod
    def model(**changes):
        obj = {"service_type": "analytics", "urgency": "medium",
               "summary": "Dashboard for weekly sales information",
               "missing_information": []}
        obj.update(changes)
        return {"choices": [{"message": {"content": json.dumps(obj)}}]}

    def test_model_transport_classifies_n8n_body_failures_without_error_text(self):
        examples = [
            ("The value in the \"JSON Body\" field is not valid JSON", "json_body_invalid"),
            ("JSON parameter needs to be valid JSON", "json_body_invalid"),
            ("ExpressionError: Cannot read properties of undefined", "expression_evaluation"),
            ("Bad request - please check your parameters", "model_api_request_rejected"),
        ]
        for raw, classification in examples:
            with self.subTest(raw=raw):
                result = model_transport_diagnostic({"error": raw})
                self.assertEqual(classification, result["error_class"])
                self.assertEqual(len(raw), result["error_length"])
                self.assertNotIn(raw, json.dumps(result))

    def test_model_transport_diagnostic_never_preserves_secret_message(self):
        bad = {"error": {"statusCode": 400,
                         "message": "400 Bad Request token=SUPER-SECRET-STRING"}}
        result = model_transport_diagnostic(bad)
        self.assertEqual("object", result["response_type"])
        self.assertEqual(["error"], result["top_level_keys"])
        self.assertEqual(["message", "statusCode"], result["error_keys"])
        self.assertEqual(400, result["error_http_status"])
        self.assertNotIn("SUPER-SECRET-STRING", json.dumps(result))
        self.assertEqual("connection_refused",
                         model_transport_diagnostic({"error": "connect ECONNREFUSED"})["error_class"])

    def test_valid_input(self):
        self.assertIsNone(validate_free_text(self.free_text()))

    def test_reject_invalid_text_and_identity(self):
        for key, value in [("request_id", "bad"), ("requester", []),
                           ("free_text", []), ("free_text", "x" * 1201),
                           ("free_text", "x\0yz" * 4)]:
            with self.subTest(key=key):
                payload = self.free_text()
                payload[key] = value
                self.assertIsNotNone(validate_free_text(payload))

    def test_hash_is_deterministic_and_bound_to_source(self):
        body = self.free_text()
        hash_ = text_hash(body)
        self.assertEqual(hash_, text_hash(dict(body, extra="not hashed")))
        body["free_text"] = "An entirely different request"
        self.assertNotEqual(hash_, text_hash(body))

    def test_valid_proposal_and_deterministic_policy(self):
        result = examine_model_response(self.model())
        self.assertEqual("standard_review", result["policy_decision"])
        self.assertIsNotNone(result["validated_model_output"])
        self.assertIsNone(result["review_reason"])

    def test_high_priority_does_not_grant_approval(self):
        result = examine_model_response(self.model(urgency="high"))
        self.assertEqual("expedite_review", result["policy_decision"])
        self.assertNotIn("approved", result)

    def test_missing_information_requires_manual_review(self):
        result = examine_model_response(self.model(missing_information=["Which CRM is involved?"]))
        self.assertEqual("manual_review", result["policy_decision"])

    def test_invalid_or_adversarial_output_never_defaults_to_success(self):
        samples = [{}, None, {"choices": []},
                   {"choices": [{"message": {"content": "not JSON"}}]},
                   self.model(service_type="book-flight"),
                   self.model(urgency="immediate"),
                   self.model(summary="brief"),
                   self.model(missing_information="none"),
                   self.model(missing_information=["x" * 121]),
                   self.model(approved=True),
                   self.model(service_type={"command": "rm -rf /"})]
        for sample in samples:
            with self.subTest(sample=sample):
                result = examine_model_response(sample)
                self.assertEqual("manual_review", result["policy_decision"])
                self.assertIsNone(result["validated_model_output"])

    def test_schema_is_closed_and_requires_four_fields(self):
        self.assertFalse(EXTRACTION_SCHEMA["additionalProperties"])
        self.assertEqual(4, len(EXTRACTION_SCHEMA["required"]))
        self.assertIsNotNone(validate_proposal({"service_type": "analytics"}))

    def test_baseline_has_no_approval_capability(self):
        self.assertEqual(("analytics", "medium"), deterministic_baseline("Create a dashboard"))

    def test_model_expression_does_not_close_before_end(self):
        # n8n v2.46.6 expression-parser.ts closes at the FIRST "}}".
        # A nested literal object without spaced closing braces is truncated.
        path = (Path(__file__).resolve().parents[1] /
                "showcases/internal-service-intake/n8n/workflow.internal-service-intake.v1.json")
        workflow = json.loads(path.read_text(encoding="utf-8"))[0]
        model = next(n for n in workflow["nodes"] if n["name"] == "Local LLM Extract")
        expression = model["parameters"]["jsonBody"]
        self.assertTrue(expression.startswith("={{"))
        self.assertTrue(expression.endswith("}}"))
        self.assertNotIn("}}", expression[3:-2],
                         "Premature n8n template closing braces truncate nested JSON expression")

    def test_rejected_approval_routes_to_response_without_apply(self):
        path = (Path(__file__).resolve().parents[1] /
                "showcases/internal-service-intake/n8n/workflow.internal-service-intake.v1.json")
        workflow = json.loads(path.read_text(encoding="utf-8"))[0]
        node = next(n for n in workflow["nodes"] if n["name"] == "Approval Decision Is Approve")
        self.assertEqual(2, node["typeVersion"])
        conditions = node["parameters"]["conditions"]
        self.assertNotIn("string", conditions, "Legacy v1 condition is invalid for n8n IF v2")
        self.assertEqual("strict", conditions["options"]["typeValidation"])
        predicate = conditions["conditions"][0]
        self.assertEqual("={{ $json.decision }}", predicate["leftValue"])
        self.assertEqual("approve", predicate["rightValue"])
        self.assertEqual({"type": "string", "operation": "equals"},
                         predicate["operator"])
        routes = workflow["connections"]["Approval Decision Is Approve"]["main"]
        self.assertEqual("Apply Approved Request", routes[0][0]["node"])
        self.assertEqual("Respond Approval", routes[1][0]["node"])

    def test_n8n_text_path_does_not_connect_directly_to_approval_or_apply(self):
        path = (Path(__file__).resolve().parents[1] /
                "showcases/internal-service-intake/n8n/workflow.internal-service-intake.v1.json")
        workflow = json.loads(path.read_text(encoding="utf-8"))[0]
        nodes = {node["name"]: node for node in workflow["nodes"]}
        self.assertIn("x-intake-token", nodes["Validate Text Webhook"]["parameters"]["jsCode"])
        self.assertEqual("http://mock-api:8080/v1/intake/preflight-text",
                         nodes["Preflight Text"]["parameters"]["url"])
        self.assertEqual("http://model:8080/v1/chat/completions",
                         nodes["Local LLM Extract"]["parameters"]["url"])
        self.assertEqual("continueRegularOutput", nodes["Local LLM Extract"]["onError"])
        self.assertIn("type: 'json_schema'", nodes["Local LLM Extract"]["parameters"]["jsonBody"])
        self.assertIn("json_schema: {name: 'service_intake'", nodes["Local LLM Extract"]["parameters"]["jsonBody"])
        self.assertIn("missing_information", nodes["Local LLM Extract"]["parameters"]["jsonBody"])
        typed_if = nodes["Needs Model Inference"]["parameters"]["conditions"]
        self.assertEqual("and", typed_if["combinator"])
        self.assertEqual("strict", typed_if["options"]["typeValidation"])
        self.assertEqual("boolean", typed_if["conditions"][0]["operator"]["type"])
        self.assertEqual("true", typed_if["conditions"][0]["operator"]["operation"])
        self.assertNotIn("boolean", typed_if)
        self.assertIn("120000", str(nodes["Local LLM Extract"]["parameters"]["options"]))
        connections = workflow["connections"]
        self.assertEqual("Preflight Text",
                         connections["Validate Text Webhook"]["main"][0][0]["node"])
        self.assertEqual("Needs Model Inference",
                         connections["Preflight Text"]["main"][0][0]["node"])
        self.assertEqual("Register Semantic Text",
                         connections["Local LLM Extract"]["main"][0][0]["node"])
        self.assertEqual("Respond Semantic Text",
                         connections["Register Semantic Text"]["main"][0][0]["node"])
        self.assertNotIn("Apply Approved Request",
                         str(connections["Local LLM Extract"]))


if __name__ == "__main__":
    unittest.main()
