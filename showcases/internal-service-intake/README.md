# Internal service intake | Decision-first AI engineering (synthetic-only)

> **30-second result:** Which component should decide what? The LLM was better at category recognition, the deterministic baseline at overall urgency. Combining them got both labels right in **22/32** exploratory cases, vs **10/32** LLM-only and **11/32** rules-only. But keyword urgency missed **5/9** high-priority cases. **The business answer depends on the cost of those misses.**
>
> **Start with the reasoning:** [91-word hypothesis → counterexample → revised decision](DECISION_EVIDENCE_BRIEF.md). [Complete operator decision record](HYBRID_DECISION_RECORD.md) · [prospective protocol](STUDY_PROTOCOL_V1.md) · [machine-checked evidence gate](evaluation/decision_gate.py).
>
> **Evidence boundary:** [Genuine E2E CI #24](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42399345922) passed at its historical SHA only. Hybrid/method changes remain **IMPLEMENTED, not exact-HEAD CI VERIFIED**. No 480-case independent evaluation, measured customer ROI, merge or deployment.

This showcase is a bounded, offline demonstration of one internal service-intake path:

**Synthetic request → authenticated webhook → strict input validation → deduplication → deterministic classification → explicit human approval → state-changing mock API → persisted result + audit evidence.**

It is intentionally isolated from the repository's research pipeline and from REA.

## Contents

- `docker-compose.yml` — isolated local stack with pinned `n8n` image and persistent volumes.
- `n8n/workflow.internal-service-intake.v1.json` — importable, versioned workflow export.
- `mock-api/app.py` + `mock-api/Dockerfile` — minimal persisted mock API using SQLite.

## Verified evidence (7 November 2026)

- **Pre-hardening snapshot `0518333ab87b8881c314c7682265630b8c71d4ed`:** [successful GitHub Actions run #42381091511](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42381091511). GitHub-hosted Docker imported and published the workflow, ran the synthetic intake and approval webhooks, checked wrong-token non-application, duplicate/idempotent intake, the persisted audit trail, and replay after container restart. The complete repository unit suite passed **46 tests**.
- **Version:** Compose uses `n8nio/n8n:2.46.6`. In the run above the actual n8n audit still flagged **Official risky nodes** (Code/HTTP Request). The earlier outdated-instance warning was absent. An audit command with exit 0 is **not** a clean security clearance.
- **Evidence boundary:** The above run concerns its exact historical SHA. Any later change to this PR (including documentation or API-key hardening) requires a new exact-head deterministic CI/E2E run before release; older green runs must never be relabeled as current-head verification.

## Local-LLM free-text path — CI #24 VERIFIED; subsequent hybrid policy pending verification

The original structured intake remains supported. A new synthetic free-text webhook,
internal-service-intake-text, accepts request_id, requester, and genuinely
unstructured free_text. Its X-INTAKE-TOKEN is checked before model execution.

**Intended route:** authenticated n8n webhook → strict text/identity/size checks →
persistent request-id/hash preflight before inference → fixed local
llama.cpp HTTP endpoint → independent JSON-schema-shaped validation in
mock-api/semantic.py → deterministic review policy → pending SQLite record
with raw output, validated output, policy and audit → separate simulated
approval token → existing apply operation.

Malformed, ambiguous, unavailable or suspicious model results may be routed to
manual_review. A model cannot grant approval or provide executable commands
or outbound URLs. The existing credentials are possession-based demonstration
tokens, **not independently verified people or separation of duties**.

**Evidence boundary:** The historical [Actions #42392952295](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42392952295) was a failing intermediate debugging run and must not be presented as the final status. The later [CI #24 on SHA d02a76f](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42399345922) passed all three jobs, genuine local LLM/n8n/SQLite E2E and the real 36-case evaluation. These results belong **only to that exact commit**. The hybrid modification made *after* CI #24 is a new unverified HEAD, with its own regression tests and post-hoc frozen-output replay. Neither CI run establishes production readiness, validated reviewer identity, business benefit or model superiority on customer data.

The existing manually dispatched .github/workflows/ci.yml runs the model gate
only on the PR branch and only after the unit suite. It uses the official
Apache-2.0 Qwen2.5-1.5B-Instruct-GGUF Q4_K_M weights at revision
dd26da440ef0330c47919d1ecae0966d24022222, SHA256
6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e,
with pinned llama.cpp server-b12019 CPU image, on a free public-repo standard
GitHub runner. Model weights are excluded from git/artifacts. The test first
runs real CPU inference, then actual n8n/model/SQLite approval and audit checks,
then evaluates 36 pre-labeled synthetic cases in evaluation/cases.jsonl
against the baseline defined in mock-api/semantic.py.

**Recruiter view (conditional on a successful run):**
15 s: unstructured request, genuine local proposal, independent policy and audit.
90 s: inspect raw/validated output, duplicate response and denied approval.
5 min: follow the model runtime/weights, fixed API flow, evaluation metrics,
timeout and prompt-injection tests, restart persistence and exact-SHA Actions logs.

Limitations: synthetic-only, temporary CPU runner, no persistent hosting,
no production SLA, no human-identity proof, no independent human reviewer.
Concurrent first-time requests can infer twice; SQLite registration stays
atomic. Existing n8n Code/HTTP risky-node audit findings require review.

## Security and data constraints

- Synthetic data only; do not send production data.
- No paid model/API is required for the core flow.
- Core path runs fully local/offline once images and dependencies are already available.
- No secrets are committed; all tokens are local environment variables. The mock API has **no built-in default key** and refuses startup without a non-empty `--api-key`.
- Both ports bind to host loopback. n8n Code nodes can read environment variables in this isolated demo (`N8N_BLOCK_ENV_ACCESS_IN_NODE=false`); this is a **material security limitation**, not a production configuration.
- Separate intake and approval bearer tokens protect demo endpoints, but possession of the approval token **does not establish a verified human identity or independent authorization**. The approver identifier is caller-supplied. Do not reuse this gate for external customer operations.
- Official risky Code and HTTP nodes are retained only for the bounded local workflow. Do not expose n8n to the public network or import untrusted workflows.
- The isolated n8n container explicitly disables the unused public REST API, Swagger UI and community-package installation. The local workflow webhooks remain necessary for the bounded demo. These config changes are **pending fresh exact-head Docker verification**, not independently validated in the historical CI run.

## Quick start

```bash
cd showcases/internal-service-intake
export INTERNAL_INTAKE_TOKEN="$(openssl rand -hex 32)"
export APPROVAL_TOKEN="$(openssl rand -hex 32)"
export MOCK_API_KEY="$(openssl rand -hex 32)"
docker compose up --build -d
```

Open `http://localhost:5678` and complete n8n local owner setup. This is a local synthetic demonstration, not production identity management. Keep generated tokens private. n8n Code-node environment access is enabled for this demo and requires additional isolation in production.

## Import workflow (reproducible)

1. In n8n UI, open **Workflows → Import from File**.
2. Import `showcases/internal-service-intake/n8n/workflow.internal-service-intake.v1.json`.
3. Activate the workflow.

Webhook paths:

- Intake: `POST http://localhost:5678/webhook/internal-service-intake`
- Approval: `POST http://localhost:5678/webhook/internal-service-intake-approval`

Required request headers (distinct credentials):

- `X-INTAKE-TOKEN: $INTERNAL_INTAKE_TOKEN` for intake; `X-APPROVAL-TOKEN: $APPROVAL_TOKEN` for approval.

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
export INTAKE_TOKEN="$INTERNAL_INTAKE_TOKEN"

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
  -H "X-APPROVAL-TOKEN: ${APPROVAL_TOKEN}" \
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

## n8n security audit — executed, outstanding findings

The n8n audit was **actually executed** on 7 November 2026 in the [successful Actions run #42381091511](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42381091511), at `0518333`. n8n `2.46.6` no longer triggered an outdated-version finding. It still reports official risky nodes (Code and HTTP Request), which can execute code or send HTTP requests if an attacker can edit workflows or control their parameters. These findings have **not** been dismissed or remediated by the successful E2E.

Reproduce against the currently imported stack (from this showcase directory):

```bash
docker compose exec -T n8n n8n audit
```

Risk boundaries: use only synthetic data, keep 5678/8080 loopback-only, grant local n8n editing privileges only to the demonstrator, use distinct private credentials, and never label the test webhook as independently authenticated human approval. The workflow has static internal API destinations and no arbitrary external-target input; this reduces exposure, but is not a production isolation or code-execution guarantee. n8n Code-node environment access remains enabled to validate demonstration credentials.

## Recruiter inspection (15 seconds / 90 seconds / 5 minutes)

**15 seconds:** A service request arrives, is validated and classified, then requires a distinct approval token before a persisted state change. Duplicates are idempotent and every transition is auditable.

**90 seconds:** Follow the Quick start/import steps, submit the synthetic intake curl, replay it to see `duplicate=true`, try a deliberately invalid approval token (no apply), then submit approved decision and read `apply_executed` in the mock API. Optional restart verifies persistence.

**5 minutes:** Inspect the versioned [n8n workflow](n8n/workflow.internal-service-intake.v1.json), [Python mock API](mock-api/app.py), [behavioral tests](../../tests/test_internal_service_intake_showcase.py), [Compose](docker-compose.yml), and [CI implementation](../../.github/workflows/ci.yml). Cross-check exact SHA and [live CI run](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42381091511). Explain the limitations: local synthetic test only, caller-supplied approver identity, risk-flagged n8n nodes and no production/customer deployment.

## Evidence checklist after modifications

1. Record `git rev-parse HEAD` and the exact Actions run ID for the same SHA.
2. Require all repository tests to pass, Docker workflow import/publish, real authenticated intake/approval webhooks, wrong-token negative path, duplicate and restart recovery.
3. Inspect the **actual findings** of `n8n audit`, not merely its exit code. Classify changes affecting security separately.
4. Keep this draft unmerged until independent review and explicit owner approval.

## Shutdown

```bash
docker compose down
```
