#!/usr/bin/env python3
import argparse
import json
import logging
import re
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
from http import HTTPStatus
from secrets import compare_digest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

REQUEST_ID_PATTERN = re.compile(r"^REQ-[A-Z0-9-]{3,40}$")
SERVICE_TYPES = {"analytics", "automation", "integration", "incident-response"}
URGENCIES = {"low", "medium", "high"}
DECISIONS = {"approve", "reject"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class ApiConfig:
    db_path: Path
    api_key: str


class IntakeStore:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        with self._connect() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS requests (
                  request_id TEXT PRIMARY KEY,
                  request_hash TEXT NOT NULL,
                  classification TEXT NOT NULL,
                  payload_json TEXT NOT NULL,
                  status TEXT NOT NULL,
                  created_at TEXT NOT NULL,
                  updated_at TEXT NOT NULL,
                  approver TEXT,
                  approval_decision TEXT,
                  approval_rationale TEXT,
                  approved_at TEXT,
                  applied_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS audit (
                  id INTEGER PRIMARY KEY AUTOINCREMENT,
                  request_id TEXT NOT NULL,
                  event_type TEXT NOT NULL,
                  event_payload TEXT NOT NULL,
                  created_at TEXT NOT NULL
                )
                """
            )

    def _audit(self, conn: sqlite3.Connection, request_id: str, event_type: str, payload: dict[str, Any]) -> None:
        conn.execute(
            "INSERT INTO audit(request_id, event_type, event_payload, created_at) VALUES(?, ?, ?, ?)",
            (request_id, event_type, json.dumps(payload, sort_keys=True), now_iso()),
        )

    def register(self, payload: dict[str, Any]) -> dict[str, Any]:
        request_id = payload["request_id"]
        request_hash = payload["request_hash"]
        classification = payload["classification"]
        ts = now_iso()
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT request_id, classification, status, request_hash FROM requests WHERE request_id = ?",
                (request_id,),
            ).fetchone()
            if row and row["request_hash"] != request_hash:
                return {"error": "request_id_conflict"}
            if row:
                self._audit(conn, request_id, "register_duplicate", {"request_hash": row["request_hash"]})
                return {
                    "duplicate": True,
                    "request_id": row["request_id"],
                    "classification": row["classification"],
                    "status": row["status"],
                }
            conn.execute(
                """
                INSERT INTO requests(
                  request_id, request_hash, classification, payload_json, status,
                  created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (request_id, request_hash, classification, json.dumps(payload["payload"], sort_keys=True), "pending", ts, ts),
            )
            self._audit(conn, request_id, "registered", {"classification": classification, "request_hash": request_hash})
            return {
                "duplicate": False,
                "request_id": request_id,
                "classification": classification,
                "status": "pending",
            }

    def approval(self, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        request_id = payload["request_id"]
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute("SELECT status, approval_decision, approver, approval_rationale FROM requests WHERE request_id = ?", (request_id,)).fetchone()
            if not row:
                return HTTPStatus.NOT_FOUND, {"error": "unknown_request_id"}
            if row["approval_decision"]:
                if (row["approval_decision"] == payload["decision"] and row["approver"] == payload["approver"] and row["approval_rationale"] == payload["rationale"]):
                    return HTTPStatus.OK, {"request_id": request_id, "status": row["status"], "decision": row["approval_decision"], "approver": row["approver"]}
                return HTTPStatus.CONFLICT, {"error": "approval_already_recorded"}
            decision = payload["decision"]
            status = "approved" if decision == "approve" else "rejected"
            ts = now_iso()
            conn.execute(
                """
                UPDATE requests
                SET status = ?, approver = ?, approval_decision = ?, approval_rationale = ?, approved_at = ?, updated_at = ?
                WHERE request_id = ?
                """,
                (status, payload["approver"], decision, payload["rationale"], ts, ts, request_id),
            )
            self._audit(conn, request_id, "approval_recorded", payload)
            return HTTPStatus.OK, {"request_id": request_id, "status": status, "decision": decision, "approver": payload["approver"]}

    def apply(self, payload: dict[str, Any]) -> tuple[int, dict[str, Any]]:
        request_id = payload["request_id"]
        with self._connect() as conn:
            conn.execute("BEGIN IMMEDIATE")
            row = conn.execute(
                "SELECT status, approval_decision FROM requests WHERE request_id = ?", (request_id,)
            ).fetchone()
            if not row:
                return HTTPStatus.NOT_FOUND, {"error": "unknown_request_id"}
            if row["approval_decision"] != "approve":
                return HTTPStatus.CONFLICT, {"error": "missing_or_rejected_approval"}
            if row["status"] == "applied":
                return HTTPStatus.OK, {"request_id": request_id, "status": "applied", "already_applied": True}
            ts = now_iso()
            conn.execute(
                "UPDATE requests SET status = ?, applied_at = ?, updated_at = ? WHERE request_id = ?",
                ("applied", ts, ts, request_id),
            )
            self._audit(conn, request_id, "apply_executed", {"actor": payload["actor"]})
            return HTTPStatus.OK, {"request_id": request_id, "status": "applied", "already_applied": False}

    def read(self, request_id: str) -> tuple[int, dict[str, Any]]:
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM requests WHERE request_id = ?", (request_id,)).fetchone()
            if not row:
                return HTTPStatus.NOT_FOUND, {"error": "unknown_request_id"}
            audit_rows = conn.execute(
                "SELECT event_type, event_payload, created_at FROM audit WHERE request_id = ? ORDER BY id ASC", (request_id,)
            ).fetchall()
            return HTTPStatus.OK, {
                "request": dict(row),
                "audit": [
                    {
                        "event_type": audit_row["event_type"],
                        "event_payload": json.loads(audit_row["event_payload"]),
                        "created_at": audit_row["created_at"],
                    }
                    for audit_row in audit_rows
                ],
            }


def classify(payload: dict[str, Any]) -> str:
    if payload["urgency"] == "high" or payload["service_type"] in {"integration", "incident-response"}:
        return "expedite_review"
    return "standard_review"


def canonical_hash(payload: dict[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256(canonical).hexdigest()


def validate_register_payload(body: dict[str, Any]) -> tuple[bool, str | None]:
    required = {"request_id", "requester", "service_type", "urgency", "justification"}
    missing = sorted(required - set(body.keys()))
    if missing:
        return False, f"missing_fields:{','.join(missing)}"
    if not isinstance(body["request_id"], str) or not REQUEST_ID_PATTERN.match(body["request_id"]):
        return False, "invalid_request_id"
    if not isinstance(body["requester"], str) or not body["requester"].strip() or len(body["requester"]) > 80:
        return False, "invalid_requester"
    if not isinstance(body["service_type"], str) or body["service_type"] not in SERVICE_TYPES:
        return False, "invalid_service_type"
    if not isinstance(body["urgency"], str) or body["urgency"] not in URGENCIES:
        return False, "invalid_urgency"
    if not isinstance(body["justification"], str) or len(body["justification"].strip()) < 10 or len(body["justification"]) > 500:
        return False, "invalid_justification"
    return True, None


def validate_approval_payload(body: dict[str, Any]) -> tuple[bool, str | None]:
    required = {"request_id", "approver", "decision", "rationale"}
    missing = sorted(required - set(body.keys()))
    if missing:
        return False, f"missing_fields:{','.join(missing)}"
    if not isinstance(body["request_id"], str) or not REQUEST_ID_PATTERN.match(body["request_id"]):
        return False, "invalid_request_id"
    if not isinstance(body["approver"], str) or not body["approver"].strip() or len(body["approver"]) > 80:
        return False, "invalid_approver"
    if not isinstance(body["decision"], str) or body["decision"] not in DECISIONS:
        return False, "invalid_decision"
    if not isinstance(body["rationale"], str) or len(body["rationale"].strip()) < 5 or len(body["rationale"]) > 500:
        return False, "invalid_rationale"
    return True, None


def validate_apply_payload(body: dict[str, Any]) -> tuple[bool, str | None]:
    required = {"request_id", "actor"}
    missing = sorted(required - set(body.keys()))
    if missing:
        return False, f"missing_fields:{','.join(missing)}"
    if not isinstance(body["request_id"], str) or not REQUEST_ID_PATTERN.match(body["request_id"]):
        return False, "invalid_request_id"
    if not isinstance(body["actor"], str) or not body["actor"].strip() or len(body["actor"]) > 80:
        return False, "invalid_actor"
    return True, None


def make_handler(config: ApiConfig, store: IntakeStore):
    class Handler(BaseHTTPRequestHandler):
        server_version = "InternalIntakeMockApi/1.0"

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A003
            logging.info("%s - - %s", self.address_string(), format % args)

        def _json_response(self, status: int, payload: dict[str, Any]) -> None:
            encoded = json.dumps(payload, sort_keys=True).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def _read_json(self) -> dict[str, Any] | None:
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                return None
            raw = self.rfile.read(size)
            try:
                data = json.loads(raw.decode("utf-8")) if raw else {}
            except (json.JSONDecodeError, UnicodeDecodeError):
                return None
            return data if isinstance(data, dict) else None

        def _require_api_key(self) -> bool:
            provided = self.headers.get("X-MOCK-API-KEY", "")
            if not provided.isascii() or not compare_digest(provided, config.api_key):
                self._json_response(HTTPStatus.UNAUTHORIZED, {"error": "unauthorized"})
                return False
            return True

        def do_GET(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path == "/health":
                self._json_response(HTTPStatus.OK, {"status": "ok"})
                return
            if parsed.path.startswith("/v1/intake/request/"):
                if not self._require_api_key():
                    return
                request_id = parsed.path.rsplit("/", 1)[-1]
                status, payload = store.read(request_id)
                self._json_response(status, payload)
                return
            self._json_response(HTTPStatus.NOT_FOUND, {"error": "not_found"})

        def do_POST(self) -> None:  # noqa: N802
            parsed = urlparse(self.path)
            if parsed.path.startswith("/v1/intake/") and not self._require_api_key():
                return
            try:
                size = int(self.headers.get("Content-Length", "0"))
            except ValueError:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "invalid_content_length"})
                return
            if size < 0 or size > 65536:
                self._json_response(HTTPStatus.REQUEST_ENTITY_TOO_LARGE, {"error": "body_too_large"})
                self.close_connection = True
                return
            body = self._read_json()
            if body is None:
                self._json_response(HTTPStatus.BAD_REQUEST, {"error": "invalid_json"})
                return

            if parsed.path == "/v1/intake/register":
                valid, error = validate_register_payload(body)
                if not valid:
                    self._json_response(HTTPStatus.BAD_REQUEST, {"error": error})
                    return
                classification = classify(body)
                payload = {
                    "request_id": body["request_id"],
                    "request_hash": canonical_hash(body),
                    "classification": classification,
                    "payload": body,
                }
                result = store.register(payload)
                self._json_response(HTTPStatus.CONFLICT if result.get("error") == "request_id_conflict" else HTTPStatus.OK, result)
                return

            if parsed.path == "/v1/intake/approval":
                valid, error = validate_approval_payload(body)
                if not valid:
                    self._json_response(HTTPStatus.BAD_REQUEST, {"error": error})
                    return
                status, payload = store.approval(body)
                self._json_response(status, payload)
                return

            if parsed.path == "/v1/intake/apply":
                valid, error = validate_apply_payload(body)
                if not valid:
                    self._json_response(HTTPStatus.BAD_REQUEST, {"error": error})
                    return
                status, payload = store.apply(body)
                self._json_response(status, payload)
                return

            self._json_response(HTTPStatus.NOT_FOUND, {"error": "not_found"})

    return Handler


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthetic internal service intake mock API")
    parser.add_argument("--host", default="0.0.0.0")
    parser.add_argument("--port", default=8080, type=int)
    parser.add_argument("--db-path", default="/data/intake.db")
    parser.add_argument("--api-key", required=True, help="Explicit nonempty local API key; no built-in default")
    args = parser.parse_args()
    if not args.api_key.strip():
        parser.error("--api-key must not be empty")
    return args


def main() -> None:
    args = parse_args()
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    config = ApiConfig(db_path=Path(args.db_path), api_key=args.api_key)
    store = IntakeStore(config.db_path)
    server = ThreadingHTTPServer((args.host, args.port), make_handler(config, store))
    logging.info("mock API listening on %s:%s db=%s", args.host, args.port, config.db_path)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logging.info("mock API shutdown requested")


if __name__ == "__main__":
    main()
