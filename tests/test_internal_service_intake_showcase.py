import json
from concurrent.futures import ThreadPoolExecutor
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / "showcases" / "internal-service-intake" / "mock-api" / "app.py"
WORKFLOW = ROOT / "showcases" / "internal-service-intake" / "n8n" / "workflow.internal-service-intake.v1.json"


def free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


class InternalServiceIntakeShowcaseTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.db_path = Path(self.tmp.name) / "intake.db"
        self.port = free_port()
        self.api_key = "test-api-key"
        self.server = self._start_server()

    def tearDown(self) -> None:
        self._stop_server()

    def _start_server(self) -> subprocess.Popen[str]:
        proc = subprocess.Popen(
            [
                sys.executable,
                str(APP),
                "--host",
                "127.0.0.1",
                "--port",
                str(self.port),
                "--db-path",
                str(self.db_path),
                "--api-key",
                self.api_key,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        deadline = time.time() + 5
        while time.time() < deadline:
            try:
                with urlopen(f"http://127.0.0.1:{self.port}/health", timeout=0.5) as response:
                    if response.status == 200:
                        return proc
            except Exception:
                time.sleep(0.1)
        self.fail("mock API failed to start")

    def _stop_server(self) -> None:
        if not getattr(self, "server", None):
            return
        self.server.terminate()
        try:
            self.server.wait(timeout=5)
        except subprocess.TimeoutExpired:
            self.server.kill()
            self.server.wait(timeout=5)
        if self.server.stdout:
            self.server.stdout.close()
        if self.server.stderr:
            self.server.stderr.close()

    def _post(self, path: str, payload: dict, auth: bool = True, timeout: float = 2.0) -> tuple[int, dict]:
        data = json.dumps(payload).encode("utf-8")
        request = Request(
            f"http://127.0.0.1:{self.port}{path}",
            data=data,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        if auth:
            request.add_header("X-MOCK-API-KEY", self.api_key)
        try:
            with urlopen(request, timeout=timeout) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except HTTPError as err:
            body = err.read().decode("utf-8")
            return err.code, json.loads(body)

    def _get(self, path: str, auth: bool = True) -> tuple[int, dict]:
        request = Request(f"http://127.0.0.1:{self.port}{path}", method="GET")
        if auth:
            request.add_header("X-MOCK-API-KEY", self.api_key)
        try:
            with urlopen(request, timeout=2.0) as response:
                return response.status, json.loads(response.read().decode("utf-8"))
        except HTTPError as err:
            body = err.read().decode("utf-8")
            return err.code, json.loads(body)

    @staticmethod
    def _valid_request(request_id: str = "REQ-INTAKE-001") -> dict:
        return {
            "request_id": request_id,
            "requester": "recruiter-demo",
            "service_type": "analytics",
            "urgency": "medium",
            "justification": "Need synthetic intake showcase evidence for hiring loop",
        }

    def test_positive_flow_persists_audit(self) -> None:
        status, register = self._post("/v1/intake/register", self._valid_request())
        self.assertEqual(200, status)
        self.assertFalse(register["duplicate"])
        self.assertEqual("standard_review", register["classification"])

        status, _ = self._post(
            "/v1/intake/approval",
            {
                "request_id": "REQ-INTAKE-001",
                "approver": "human.approver",
                "decision": "approve",
                "rationale": "Looks safe for synthetic demo",
            },
        )
        self.assertEqual(200, status)

        status, apply_result = self._post(
            "/v1/intake/apply",
            {"request_id": "REQ-INTAKE-001", "actor": "workflow"},
        )
        self.assertEqual(200, status)
        self.assertEqual("applied", apply_result["status"])

        status, state = self._get("/v1/intake/request/REQ-INTAKE-001")
        self.assertEqual(200, status)
        self.assertEqual("applied", state["request"]["status"])
        self.assertEqual(["registered", "approval_recorded", "apply_executed"], [e["event_type"] for e in state["audit"]])

    def test_approval_response_supports_workflow_apply(self) -> None:
        self._post("/v1/intake/register", self._valid_request("REQ-PROBE-001"))
        status, approval = self._post("/v1/intake/approval", {"request_id":"REQ-PROBE-001","approver":"human","decision":"approve","rationale":"approved demo"})
        self.assertEqual(200, status)
        status, result = self._post("/v1/intake/apply", {"request_id":approval["request_id"],"actor":approval.get("approver")})
        self.assertEqual(200, status, result)

    def test_duplicate_id_with_different_payload_is_conflict(self) -> None:
        payload = self._valid_request("REQ-PROBE-002")
        self._post("/v1/intake/register", payload)
        payload["justification"] = "An entirely different synthetic request"
        status, _ = self._post("/v1/intake/register", payload)
        self.assertEqual(409, status)

    def test_approval_retry_is_idempotent(self) -> None:
        self._post("/v1/intake/register", self._valid_request("REQ-RETRY-001"))
        decision = {"request_id":"REQ-RETRY-001","approver":"human","decision":"approve","rationale":"approved demo"}
        first, _ = self._post("/v1/intake/approval", decision)
        second, response = self._post("/v1/intake/approval", decision)
        self.assertEqual(200, first)
        self.assertEqual(200, second, response)
        status, state = self._get("/v1/intake/request/REQ-RETRY-001")
        self.assertEqual(1, sum(event["event_type"] == "approval_recorded" for event in state["audit"]))

    def test_invalid_json_types_are_rejected_without_disconnect(self) -> None:
        payload = self._valid_request("REQ-TYPES-001")
        payload["service_type"] = []
        status, _ = self._post("/v1/intake/register", payload)
        self.assertEqual(400, status)

    def test_oversized_request_is_rejected(self) -> None:
        payload = self._valid_request("REQ-SIZE-001")
        payload["junk"] = "x" * 70000
        status, _ = self._post("/v1/intake/register", payload)
        self.assertEqual(413, status)

    def test_concurrent_register_and_apply_have_one_effect_each(self) -> None:
        request = self._valid_request("REQ-CONCURRENT-001")
        with ThreadPoolExecutor(max_workers=8) as pool:
            results = list(pool.map(lambda _: self._post("/v1/intake/register", request), range(16)))
        self.assertTrue(all(status == 200 for status, _ in results), results)
        self.assertEqual(1, sum(not body["duplicate"] for _, body in results))
        decision = {"request_id":"REQ-CONCURRENT-001","approver":"human","decision":"approve","rationale":"approved demo"}
        self.assertEqual(200, self._post("/v1/intake/approval", decision)[0])
        with ThreadPoolExecutor(max_workers=8) as pool:
            applied = list(pool.map(lambda _: self._post("/v1/intake/apply", {"request_id":"REQ-CONCURRENT-001","actor":"workflow"}), range(16)))
        self.assertTrue(all(status == 200 for status, _ in applied), applied)
        self.assertEqual(1, sum(not body["already_applied"] for _, body in applied))
        _, state = self._get("/v1/intake/request/REQ-CONCURRENT-001")
        self.assertEqual(1, sum(e["event_type"] == "apply_executed" for e in state["audit"]))

    def test_standalone_api_requires_explicit_nonempty_key(self) -> None:
        for key_args in ([], ["--api-key", ""]):
            with self.subTest(key_args=key_args):
                proc = subprocess.run(
                    [sys.executable, str(APP), "--host", "127.0.0.1",
                     "--port", "0", "--db-path", str(self.db_path), *key_args],
                    text=True, capture_output=True, timeout=5, check=False,
                )
                self.assertNotEqual(0, proc.returncode)
                self.assertIn("--api-key", proc.stderr)

    def test_authentication_required(self) -> None:
        status, body = self._post("/v1/intake/register", self._valid_request(), auth=False)
        self.assertEqual(401, status)
        self.assertEqual("unauthorized", body["error"])

    def test_invalid_input_rejected(self) -> None:
        invalid = self._valid_request()
        invalid["request_id"] = "bad"
        status, body = self._post("/v1/intake/register", invalid)
        self.assertEqual(400, status)
        self.assertEqual("invalid_request_id", body["error"])

    def test_duplicate_registration_is_idempotent(self) -> None:
        status, first = self._post("/v1/intake/register", self._valid_request("REQ-INTAKE-DUPE"))
        self.assertEqual(200, status)
        self.assertFalse(first["duplicate"])

        status, duplicate = self._post("/v1/intake/register", self._valid_request("REQ-INTAKE-DUPE"))
        self.assertEqual(200, status)
        self.assertTrue(duplicate["duplicate"])
        self.assertEqual("pending", duplicate["status"])

    def test_apply_blocked_without_or_with_rejected_approval(self) -> None:
        self._post("/v1/intake/register", self._valid_request("REQ-INTAKE-REJECT"))

        status, missing = self._post("/v1/intake/apply", {"request_id": "REQ-INTAKE-REJECT", "actor": "workflow"})
        self.assertEqual(409, status)
        self.assertEqual("missing_or_rejected_approval", missing["error"])

        status, _ = self._post(
            "/v1/intake/approval",
            {
                "request_id": "REQ-INTAKE-REJECT",
                "approver": "human.approver",
                "decision": "reject",
                "rationale": "Not justified",
            },
        )
        self.assertEqual(200, status)

        status, rejected = self._post("/v1/intake/apply", {"request_id": "REQ-INTAKE-REJECT", "actor": "workflow"})
        self.assertEqual(409, status)
        self.assertEqual("missing_or_rejected_approval", rejected["error"])

    def test_restart_recovery_with_same_db(self) -> None:
        self._post("/v1/intake/register", self._valid_request("REQ-INTAKE-RESTART"))
        self._post(
            "/v1/intake/approval",
            {
                "request_id": "REQ-INTAKE-RESTART",
                "approver": "human.approver",
                "decision": "approve",
                "rationale": "Approved for synthetic replay",
            },
        )
        self._post("/v1/intake/apply", {"request_id": "REQ-INTAKE-RESTART", "actor": "workflow"})

        self._stop_server()
        self.server = self._start_server()

        status, state = self._get("/v1/intake/request/REQ-INTAKE-RESTART")
        self.assertEqual(200, status)
        self.assertEqual("applied", state["request"]["status"])

    def test_mock_image_does_not_embed_default_secret(self) -> None:
        dockerfile = (ROOT / "showcases/internal-service-intake/mock-api/Dockerfile").read_text()
        self.assertNotIn("local-demo-api-key", dockerfile)
        self.assertNotIn("MOCK_API_KEY:-", dockerfile)
        self.assertIn('CMD ["python", "/app/app.py"]', dockerfile)

    def test_n8n_unused_public_api_and_community_packages_disabled(self) -> None:
        compose = (ROOT / "showcases/internal-service-intake/docker-compose.yml").read_text()
        self.assertIn('N8N_PUBLIC_API_DISABLED: "true"', compose)
        self.assertIn('N8N_PUBLIC_API_SWAGGERUI_DISABLED: "true"', compose)
        self.assertIn('N8N_COMMUNITY_PACKAGES_ENABLED: "false"', compose)

    def test_compose_is_loopback_only_and_has_no_fixed_token_defaults(self) -> None:
        compose = (ROOT / "showcases/internal-service-intake/docker-compose.yml").read_text()
        self.assertIn('127.0.0.1:5678:5678', compose)
        self.assertIn('127.0.0.1:8080:8080', compose)
        self.assertNotIn('local-intake-token', compose)
        self.assertNotIn('local-demo-api-key', compose)

    def test_workflow_has_bounded_retries_timeouts_and_approval_boundary(self) -> None:
        workflow_export = json.loads(WORKFLOW.read_text(encoding="utf-8"))[0]
        nodes = {node["name"]: node for node in workflow_export["nodes"]}

        for node_name in ["Register Pending Request", "Record Approval", "Apply Approved Request"]:
            node = nodes[node_name]
            self.assertTrue(node.get("retryOnFail"), node_name)
            self.assertEqual(2, node.get("maxTries"), node_name)
            self.assertEqual(3000, node["parameters"]["options"]["timeout"])

        self.assertIn("x-intake-token", nodes["Validate Intake Webhook"]["parameters"]["jsCode"])
        self.assertIn("x-approval-token", nodes["Validate Approval Webhook"]["parameters"]["jsCode"])

        approval_connections = workflow_export["connections"]["Approval Decision Is Approve"]["main"]
        true_branch_nodes = {edge["node"] for edge in approval_connections[0]}
        false_branch_nodes = {edge["node"] for edge in approval_connections[1]}
        self.assertIn("Apply Approved Request", true_branch_nodes)
        self.assertIn("Respond Approval", false_branch_nodes)


if __name__ == "__main__":
    unittest.main()
