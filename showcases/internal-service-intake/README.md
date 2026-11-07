# Internal service intake showcase (synthetic-only)

This showcase is a bounded, offline demonstration of one internal service-intake path:

**Synthetic request → authenticated webhook → strict input validation → deduplication → deterministic classification → explicit human approval → state-changing mock API → persisted result + audit evidence.**

It is intentionally isolated from the repository's research pipeline and from REA.

## Contents

- `docker-compose.yml` — isolated local stack with pinned `n8n` image and persistent volumes.
- `n8n/workflow.internal-service-intake.v1.json` — importable, versioned workflow export.
- `mock-api/app.py` + `mock-api/Dockerfile` — minimal persisted mock API using SQLite.

## Security and data constraints

- Synthetic data only; do not send production data.
- No paid model/API is required for the core flow.
- Core path runs fully local/offline once images and dependencies are already available.
- No secrets are committed; all tokens are local environment variables.

## Quick start

```bash
cd /home/runner/work/ai-knowledge-ops-lab/ai-knowledge-ops-lab/showcases/internal-service-intake
docker compose up --build -d
```

Open `http://localhost:5678` and sign in with local basic-auth values (`demo` / `demo-pass` by default).

## Import workflow (reproducible)

1. In n8n UI, open **Workflows → Import from File**.
2. Import `/home/runner/work/ai-knowledge-ops-lab/ai-knowledge-ops-lab/showcases/internal-service-intake/n8n/workflow.internal-service-intake.v1.json`.
3. Activate the workflow.

Webhook paths:

- Intake: `POST http://localhost:5678/webhook/internal-service-intake`
- Approval: `POST http://localhost:5678/webhook/internal-service-intake-approval`

Required request header for both webhooks:

- `X-INTAKE-TOKEN: local-intake-token` (or your override value)

## Nontechnical demo script

1. Send one synthetic intake request.
2. Observe response: pending registration + deterministic classification.
3. Send a duplicate intake with same `request_id`; observe duplicate response.
4. Send approval decision:
   - `reject` should not apply state change.
   - `approve` triggers the state-changing apply step.
5. Query persisted state and audit evidence from mock API.

### Example curl commands

```bash
export INTAKE_TOKEN="local-intake-token"
export MOCK_API_KEY="local-demo-api-key"

curl -sS -X POST "http://localhost:5678/webhook/internal-service-intake" \
  -H "Content-Type: application/json" \
  -H "X-INTAKE-TOKEN: ${INTAKE_TOKEN}" \
  -d '{
    "request_id": "REQ-DEMO-001",
    "requester": "Recruiting Demo",
    "service_type": "analytics",
    "urgency": "medium",
    "justification": "Need synthetic intake workflow evidence for recruiter demo"
  }'

curl -sS -X POST "http://localhost:5678/webhook/internal-service-intake-approval" \
  -H "Content-Type: application/json" \
  -H "X-INTAKE-TOKEN: ${INTAKE_TOKEN}" \
  -d '{
    "request_id": "REQ-DEMO-001",
    "approver": "human.reviewer",
    "decision": "approve",
    "rationale": "Synthetic demo approved"
  }'

curl -sS "http://localhost:8080/v1/intake/request/REQ-DEMO-001" \
  -H "X-MOCK-API-KEY: ${MOCK_API_KEY}"
```

## Restart recovery

SQLite DB is stored in the `mock_api_data` Docker volume. Restart and verify persisted records:

```bash
docker compose restart mock-api
curl -sS "http://localhost:8080/v1/intake/request/REQ-DEMO-001" -H "X-MOCK-API-KEY: ${MOCK_API_KEY}"
```

## Automated tests

From repo root:

```bash
python -m unittest tests.test_internal_service_intake_showcase -v
```

Covered scenarios:

- authentication required
- strict invalid input rejection
- deduplication/idempotent register
- missing approval block
- rejected approval block
- positive approval + apply path
- persistence across restart
- bounded retry + timeout configuration in workflow JSON

## n8n security audit status

Attempted command:

```bash
docker compose run --rm n8n n8n audit
```

If this fails in your environment (for example, Docker unavailable), use this actionable fallback:

```bash
docker compose run --rm n8n n8n --help | grep -i audit
```

Then run the listed n8n audit subcommand(s) available in your installed n8n image and record output with your demo evidence.

## Evidence template (fill after local run)

- Tested commit SHA: _see `git rev-parse HEAD` after test run_
- Commands run: list exact commands used
- Results: pass/fail per command
- Logs captured: mock-api stdout, n8n execution log, webhook request/response bodies
- Limitations: any environment gaps (for example Docker unavailable)

## Shutdown

```bash
docker compose down
```
