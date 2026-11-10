# SFS CRM Integration Lab — final secure connection handoff

This document contains **no secret values**. Both Workers are deployed in the
dedicated Cloudflare connection **Salesforce Custom MCP** (`play@sfs-labs.dev`).
Main branch is untouched; work is in Draft PR #32.

## 1. Salesforce External Client App (iPhone Safari)

In the **Salesforce Developer Edition**, open Setup -> **External Client App Manager**
and create a local External Client App named `SFS CRM Integration Lab`.

Use:
- OAuth authorization code / web server flow, PKCE S256 supported.
- **Exact callback**: `https://sfs-salesforce-remote-mcp.sfs-salesforce-custom-mcp.workers.dev/sf/callback`
- OAuth scopes: `api` and `refresh_token/offline_access`.
- Limit permitted users to the synthetic Developer Edition test org.
- The existing Worker sends a confidential client secret during code and
  refresh-token exchanges; enable the matching secret requirement.

After saving, open Settings -> OAuth -> Consumer Key and Secret and complete
the required Salesforce identity challenge if prompted.

In the dedicated **Cloudflare** dashboard -> Workers & Pages ->
`sfs-salesforce-remote-mcp` -> Settings -> Variables and Secrets:
- Secret `SALESFORCE_CLIENT_ID`: Salesforce Consumer Key / Client ID.
- Secret `SALESFORCE_CLIENT_SECRET`: Salesforce Consumer Secret.

`COOKIE_ENCRYPTION_KEY` is already generated and securely stored. Do not
replace it unless deliberately invalidating pending OAuth transactions.

Never send any of these secret **values** through chat, code, GitHub or screenshots.

## 2. Free-model router

In the **same dedicated Cloudflare account**, open Workers & Pages ->
`sfs-free-inference-router` -> Settings -> Variables and Secrets.

Create two secrets:
- `OPENROUTER_API_KEY`: your already-created OpenRouter API key.
- `ROUTER_CLIENT_TOKEN`: a newly generated long random token (32+ random bytes
  recommended). Save a copy in your trusted password manager: this same token
  must be pasted into LangSmith's secure Custom Model API Key field.

The deployed router uses `openrouter/free` first and automatically uses
Cloudflare Workers AI `@cf/zai-org/glm-4.7-flash` as a free-only fallback.
If both are unavailable, it fails closed. It does **not** provide paid fallback.

## 3. LangSmith Fleet

In your Fleet agent settings -> Model -> Add custom model:
- Display name: `SFS Free Router`
- Model ID: `sfs/free-router`
- OpenAI-compatible Base URL:
  `https://sfs-free-inference-router.sfs-salesforce-custom-mcp.workers.dev/v1`
- API key: the same `ROUTER_CLIENT_TOKEN` generated in step 2.

Select this custom model as the agent's **active model**.

Connect remote MCP integrations in Fleet:
- Salesforce custom MCP:
  `https://sfs-salesforce-remote-mcp.sfs-salesforce-custom-mcp.workers.dev/mcp`
- HubSpot official MCP:
  `https://mcp.hubspot.com`

Authorize Salesforce via its OAuth browser flow against your Developer Edition.
Use a separate HubSpot test account; only synthetic data.

## 4. Acceptance sequence

After the secrets and OAuth connections are configured:
1. Confirm Fleet custom model can answer one minimal prompt without billed model.
2. Check Salesforce MCP `ping`, object discovery and a read-only Contact query.
3. Check HubSpot MCP read-only object access.
4. Request an integration **dry-run** with one synthetic contact.
5. Only after the user approves: one scoped, reversible test write.
6. Inspect errors, tool-call arguments, duplicate behavior and rollback.

**Hard limitation:** the LangSmith Fleet Developer monthly quota is a
platform-level limit. Model-provider fallback does **not** bypass Fleet's own
quota. An independent agent runtime would be needed after Fleet pauses runs.

## Verification already completed

- Cloudflare Salesforce Worker deployed with KV + Durable Object bindings;
  `COOKIE_ENCRYPTION_KEY` present.
- OAuth discovery + unauthenticated 401 behavior tested by GitHub Actions.
- Cloudflare Workers AI GLM-4.7-Flash live text response verified with
  `enable_thinking: false`.
- Live function calling verified with nested OpenAI tools.
- Router fallback, closed failure, secret gate, tool-call transformation and
  reasoning-only response tests passed in GitHub Actions.
- The two missing Salesforce secrets and the two missing router secrets
  have **not** been fabricated or installed.
