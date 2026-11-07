# Business-first service-intake decision case (synthetic local stack)

**30–60-second nontechnical explanation:** [Candidate-first decision case](../../docs/index.html) → [Data architecture & source-truth boundaries](RESEARCH_DESIGN.md) → [Historical hybrid decision](DECISION_EVIDENCE_BRIEF.md).

**The decision:** Can a service desk recognize the *type* of request and avoid avoidable internal handoffs without missing urgent incidents? Start with the business outcome, **not** a fixed AI stack or a predefined service taxonomy.

| Evidence stream | Source classes/metrics | Current measured provenance |
|---|---|---|
| **What is it?** NLBSE 2023 | `bug`, `feature`, `question`, `documentation` – actual harmonized source issue labels; **not** Analytics/Automation/Integration/Incident Response | [Full official 142,320 test audited in CI #29](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42412917843): 49.25% keyword Accuracy, 41.49% Macro-F1; 541 repeated IDs (5 label conflicts), no NLBSE LLM inference |
| **How does work flow?** Volvo IT 2013 | incident event log; **9,454 observed transitions between groups** across **7,554 incidents / 65,533 events** | [Real original archive MD5-verified in CI #27](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42411756411), individual source-audit step SUCCESS |
| **What might it cost?** Destatis sector rate | **€58.50 per hour worked**, Germany 2025 Information & Communication | [Official statistic](https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/04/PD26_148_624.html); not Volvo labor costs |

**Hard boundary:** NLBSE issues and Volvo incidents are two **separate, unjoinable samples**. An observed group transition is not a proved avoidable handoff. Working hours saved, avoided incident losses and net ROI require explicit *assumptions or new customer data*. The scenario assumptions are fully documented in [research_methods.py](evaluation/research_methods.py); the public work sample prioritizes the engineering decision over hypothetical ROI figures.

**Technical prototype:** Authenticated local n8n 2.46.6 → local Qwen model → SQLite mock API; independent review/approval gate, rejection, idempotency and restart. **[CI #25 passed 100 tests and the real local LLM E2E](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42405856175)** at immutable `d4a8391`. The original 32 labeled synthetic cases were an exploratory *different taxonomy*; don't transfer their hybrid 22/32 to NLBSE or Volvo.

**Release semantics:** This is safe to **publish as static code + documentation** after exact-HEAD CI and review. It is not a hosted automation service. No production SLA, verified human identity, external customer or measured AI ROI. The original release passed [exact-HEAD CI #31](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42413698800); later documentation changes need their own review.

**Research reproducibility (Python 3.12, no paid API):**

```sh
python -m unittest discover -s tests -v
python showcases/internal-service-intake/evaluation/research_methods.py
python showcases/internal-service-intake/evaluation/volvo_process.py
python showcases/internal-service-intake/evaluation/nlbse_source.py
```

Source audits require access to public original archives; never re-publish raw issue text or identify individuals. See [Data contract](evaluation/research_contract.json), [source-audit evidence](evaluation/evidence/volvo-2013-source-audit-ci27.json), [business analysis](RESEARCH_DESIGN.md) and [evaluation caveats](STUDY_PROTOCOL_V1.md).

## Security and data constraints

- Synthetic data only; do not send production data.
- No paid model/API is required for the core flow.
- Core path runs fully local/offline once images and dependencies are already available.
- No secrets are committed; all tokens are local environment variables. The mock API has **no built-in default key** and refuses startup without a non-empty `--api-key`.
- Both ports bind to host loopback. n8n Code nodes can read environment variables in this isolated demo (`N8N_BLOCK_ENV_ACCESS_IN_NODE=false`); this is a **material security limitation**, not a production configuration.
- Separate intake and approval bearer tokens protect demo endpoints, but possession of the approval token **does not establish a verified human identity or independent authorization**. The approver identifier is caller-supplied. Do not reuse this gate for external customer operations.
- Official risky Code and HTTP nodes are retained only for the bounded local workflow. Do not expose n8n to the public network or import untrusted workflows.
- The isolated n8n container explicitly disables the unused public REST API, Swagger UI and community-package installation. The local workflow webhooks remain necessary for the bounded demo. The bounded configuration was exercised in [CI #25](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42405856175) on its exact historical SHA. This does not constitute a production security approval.

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
4. Merge/release only after an explicit authorized decision and exact-head verification. A safe static research page may be published; the webhook/LLM containers are never a public deployment target.

## Shutdown

```bash
docker compose down
```
