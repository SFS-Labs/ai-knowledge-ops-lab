# SFS | Zero-Spend Model Router

A strict OpenAI Chat Completions-compatible Cloudflare Worker for **LangSmith Fleet custom models**.

**Deployed:** `https://sfs-free-inference-router.sfs-salesforce-custom-mcp.workers.dev`

- Base URL for Fleet: `https://sfs-free-inference-router.sfs-salesforce-custom-mcp.workers.dev/v1`
- Model ID: `sfs/free-router`
- Endpoint: `POST /v1/chat/completions`
- Discovery: `GET /v1/models` (authenticated)
- Health: `GET /health` (non-secret only)
- All inference requests require `Authorization: Bearer <ROUTER_CLIENT_TOKEN>`.

## Actually enforced runtime policy

1. OpenRouter `openrouter/free` first (uses `OPENROUTER_API_KEY` secret).
2. On primary quota (HTTP 429), upstream error, network timeout or no key,
   switch automatically to Cloudflare Workers AI `@cf/zai-org/glm-4.7-flash`
   through the account-local `AI` binding.
3. If neither free endpoint works, return HTTP 503. **No paid model ID is
   accepted**; only `sfs/free-router` is allowed. Requests are bounded.
4. The response carries `X-SFS-Route` to identify the served route.
5. Supports non-streaming and synthetic, delayed SSE completion frames.
   Streaming is compatible with the response framing but does not provide
   true incremental token latency.

## Secret configuration — USER ACTION REQUIRED

In the dedicated Cloudflare account, Workers & Pages ->
`sfs-free-inference-router` -> Settings -> Variables and Secrets:

- `ROUTER_CLIENT_TOKEN` (Secret): generate a strong random bearer token.
  Enter the **same** token into LangSmith Fleet's Custom Model API Key field
  via its secure settings UI. Never send this token in chat.
- `OPENROUTER_API_KEY` (Secret): existing OpenRouter API key, entered only
  via the Cloudflare secrets UI. Never store in Github or messages.

The Worker is uploaded and the route is enabled, but inference cannot
authenticate until `ROUTER_CLIENT_TOKEN` is set. Without the OpenRouter key,
Workers AI automatically serves as the free-only fallback.

## LangSmith Fleet setup

Open the agent -> Settings -> Model -> Add custom model:
- Name: `SFS Free Router`
- Model ID: `sfs/free-router`
- Base URL: `https://sfs-free-inference-router.sfs-salesforce-custom-mcp.workers.dev/v1`
- API key name: `SFS_ROUTER_CLIENT_TOKEN` (workspace secret name; UI wording may vary).
- API key value: the exact `ROUTER_CLIENT_TOKEN` stored in Cloudflare.

Save and **choose this custom model as the agent's active model**.
Fleet Fast is an independent managed model and cannot be automatically
chained into an external proxy through a documented supported API.
This router provides a mandatory automatic fallback across two independent
free provider quotas instead.

**Platform-level limit remains:** LangSmith Fleet's Developer plan currently
includes only 5 LCUs per organization per month; after exhaustion, Fleet pauses
new agent runs, regardless of whether the inference model uses an external API.
The OpenRouter -> Workers AI failover applies to MODEL CALLS ONLY. To keep
working after a Fleet cap, an independent agent runtime/client (outside Fleet)
would be required and is not yet implemented. Do not claim this cap is bypassed.

Use synthetic test data only; free OpenRouter models may have different
prompt retention policies. Cloudflare Workers Free has its own Workers AI
10,000-neuron/day allocation and responds with quota errors when exhausted.

## Verified compatibility corrections (2026-11-10)

- Live Cloudflare GLM inference: `chat_template_kwargs: {enable_thinking:false}` produced a usable `OK` response; the default thinking mode exhausted a small completion-token budget without returning text.
- The router rejects empty or truncated results instead of fabricating a successful answer.
- Live Cloudflare GLM function calling succeeded with the **nested OpenAI schema** `{type:"function", function:{name,description,parameters}}` and `tool_choice:"required"`.
- The earlier flattened tool schema returned Cloudflare HTTP 400 and has been removed from the Worker.
- The updated Workers AI fallback has been uploaded to the dedicated Cloudflare account; the server-side router key is still unset.

## Evidence and limitations

- Unit and simulated provider failure tests:
  `node --test sfs-inference-router/worker.test.mjs`.
- GitHub Actions run:
  https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42871284009
- Remote HTTP smoke:
  https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42872583807
- The tests verify routing logic, not a real OpenRouter model response.
- No active credentials or end-to-end LangSmith model requests have been tested.
