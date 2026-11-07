"""Deterministic validation for untrusted synthetic service-intake model output.

The local LLM proposes data; this module, not the LLM, chooses a policy route.
"""
import hashlib
import json
import re
from typing import Any

REQUEST_ID = re.compile(r"^REQ-[A-Z0-9-]{3,40}$")
SERVICE_TYPES = frozenset({"analytics", "automation", "integration", "incident-response"})
URGENCIES = frozenset({"low", "medium", "high"})
MODEL_FIELDS = frozenset({"service_type", "urgency", "summary", "missing_information"})
MAX_TEXT = 1200

EXTRACTION_SCHEMA = {
    "type": "object", "additionalProperties": False,
    "required": ["service_type", "urgency", "summary", "missing_information"],
    "properties": {
        "service_type": {"type": "string", "enum": sorted(SERVICE_TYPES)},
        "urgency": {"type": "string", "enum": sorted(URGENCIES)},
        "summary": {"type": "string", "minLength": 10, "maxLength": 240},
        "missing_information": {"type": "array", "maxItems": 4,
                                "items": {"type": "string", "minLength": 3, "maxLength": 120}},
    },
}


def validate_free_text(body: Any) -> str | None:
    if not isinstance(body, dict):
        return "invalid_json_object"
    if not isinstance(body.get("request_id"), str) or not REQUEST_ID.fullmatch(body["request_id"]):
        return "invalid_request_id"
    requester = body.get("requester")
    if not isinstance(requester, str) or not requester.strip() or len(requester) > 80:
        return "invalid_requester"
    value = body.get("free_text")
    if not isinstance(value, str) or not (10 <= len(value.strip()) <= MAX_TEXT):
        return "invalid_free_text"
    if any(ord(c) < 32 and c not in "\r\n\t" for c in value):
        return "invalid_control_character"
    return None


def normalized_text_input(body: dict[str, Any]) -> dict[str, str]:
    return {k: body[k] for k in ("request_id", "requester", "free_text")}


def text_hash(body: dict[str, Any]) -> str:
    raw = json.dumps(normalized_text_input(body), ensure_ascii=False,
                     sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def validate_proposal(value: Any) -> str | None:
    """Standard-library enforcement of EXTRACTION_SCHEMA; never trust model JSON mode."""
    if not isinstance(value, dict) or set(value) != MODEL_FIELDS:
        return "invalid_schema_fields"
    if not isinstance(value["service_type"], str) or value["service_type"] not in SERVICE_TYPES:
        return "invalid_service_type"
    if not isinstance(value["urgency"], str) or value["urgency"] not in URGENCIES:
        return "invalid_urgency"
    summary = value["summary"]
    if not isinstance(summary, str) or not (10 <= len(summary.strip()) <= 240):
        return "invalid_summary"
    missing = value["missing_information"]
    if not isinstance(missing, list) or len(missing) > 4 or any(
        not isinstance(v, str) or not (3 <= len(v.strip()) <= 120) for v in missing
    ):
        return "invalid_missing_information"
    return None


def examine_model_response(response: Any) -> dict[str, Any]:
    raw = None
    if isinstance(response, dict):
        try:
            raw = response["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError):
            pass
    if not isinstance(raw, str) or not raw or len(raw) > 3000:
        return {"raw_model_output": raw if isinstance(raw, str) else None,
                "validated_model_output": None, "policy_decision": "manual_review",
                "review_reason": "model_unavailable_or_invalid_response"}
    try:
        proposal = json.loads(raw)
    except (json.JSONDecodeError, UnicodeError):
        return {"raw_model_output": raw, "validated_model_output": None,
                "policy_decision": "manual_review", "review_reason": "invalid_model_json"}
    error = validate_proposal(proposal)
    if error:
        return {"raw_model_output": raw, "validated_model_output": None,
                "policy_decision": "manual_review", "review_reason": error}
    policy = "manual_review" if proposal["missing_information"] else (
        "expedite_review" if proposal["urgency"] == "high" or
        proposal["service_type"] in {"integration", "incident-response"}
        else "standard_review")
    return {"raw_model_output": raw, "validated_model_output": proposal,
            "policy_decision": policy,
            "review_reason": "missing_information" if proposal["missing_information"] else None}


def semantic_preflight(store: Any, body: Any) -> tuple[int, dict[str, Any]]:
    """Pre-inference dedup; final atomic register remains the concurrency guard."""
    error = validate_free_text(body)
    if error:
        return 400, {"error": error}
    fields = normalized_text_input(body)
    fingerprint = text_hash(fields)
    with store._connect() as conn:
        row = conn.execute(
            "SELECT request_hash, classification, status FROM requests WHERE request_id = ?",
            (fields["request_id"],),
        ).fetchone()
    if row and row["request_hash"] != fingerprint:
        return 409, {"error": "request_id_conflict"}
    if row:
        return 200, {"request_id": fields["request_id"], "duplicate": True,
                     "needs_inference": False, "status": row["status"],
                     "classification": row["classification"]}
    return 200, dict(fields, duplicate=False, needs_inference=True)



def model_transport_diagnostic(response: Any) -> dict[str, Any]:
    """Record only response shape and a fixed error class; never persist error text."""
    if not isinstance(response, dict):
        return {"response_type": type(response).__name__}
    details: dict[str, Any] = {
        "response_type": "object",
        "top_level_keys": sorted(str(k) for k in response.keys())[:20],
    }
    error = response.get("error")
    if isinstance(error, dict):
        details["error_keys"] = sorted(str(k) for k in error.keys())[:20]
        for key in ("statusCode", "httpCode", "status"):
            value = error.get(key)
            if isinstance(value, int) and not isinstance(value, bool):
                details["error_http_status"] = value
                break
        diagnostic_text = " ".join(str(error.get(k, "")) for k in ("message", "description", "cause")).lower()
    elif isinstance(error, str):
        diagnostic_text = error.lower()
    else:
        diagnostic_text = ""
    indicators = {
        "json_body_invalid": ('json body" field is not valid json',
                              "json parameter needs to be valid json",
                              "the value in the json body field is not valid json"),
        "expression_evaluation": ("expressionerror", "cannot read properties of undefined",
                                  "referenced node is unexecuted", "invalid expression"),
        "model_api_request_rejected": ("bad request - please check your parameters",),
        "connection_refused": ("econnrefused", "connection refused"),
        "dns_failure": ("enotfound", "getaddrinfo", "dns"),
        "timeout": ("etimedout", "timeout", "timed out"),
        "schema_rejected": ("json_schema", "schema invalid", "invalid schema"),
        "http_400": ("400 bad request", "status code 400"),
        "http_500": ("500 internal server error", "status code 500"),
    }
    details["error_class"] = next(
        (name for name, needles in indicators.items() if any(w in diagnostic_text for w in needles)),
        "unspecified" if error is not None else "none",
    )
    details["error_length"] = min(len(diagnostic_text), 10000)
    return details


def semantic_register(store: Any, body: Any) -> tuple[int, dict[str, Any]]:
    error = validate_free_text(body)
    if error:
        return 400, {"error": error}
    fields = normalized_text_input(body)
    evaluated = examine_model_response(body.get("model_response"))
    registration = {
        "request_id": fields["request_id"],
        "request_hash": text_hash(fields),
        "classification": evaluated["policy_decision"],
        "payload": {
            "source": "unstructured_free_text", "input": fields,
            "raw_model_output": evaluated["raw_model_output"],
            "validated_model_output": evaluated["validated_model_output"],
            "policy_decision": evaluated["policy_decision"],
            "review_reason": evaluated["review_reason"],
            "model_transport_diagnostic": model_transport_diagnostic(body.get("model_response")) if evaluated["validated_model_output"] is None else None,
        },
        "model_evaluation": {
            "valid": evaluated["validated_model_output"] is not None,
            "policy_decision": evaluated["policy_decision"],
            "review_reason": evaluated["review_reason"],
        },
    }
    result = store.register(registration)
    return (409 if result.get("error") else 200), result


def deterministic_baseline(text: str) -> tuple[str | None, str]:
    """Minimal keyword comparison, not a fallback classification."""
    lower = text.lower()
    keywords = {
        "incident-response": ("incident", "security breach", "outage", "ausfall", "angriff", "datenleck"),
        "integration": ("integration", "integrate", "connect", "api", "anbinden", "schnittstelle"),
        "analytics": ("dashboard", "analytics", "reporting", "auswertung", "bericht", "kennzahl"),
        "automation": ("automate", "automation", "automatisieren", "workflow", "routine"),
    }
    category = next((k for k, words in keywords.items() if any(w in lower for w in words)), None)
    urgency = "high" if any(w in lower for w in (
        "urgent", "critical", "sofort", "dringend", "today", "heute")) else "medium"
    return category, urgency
