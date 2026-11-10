# SFS | Salesforce Remote MCP — isolated bootstrap

**Status:** pre-deployment build and review. This feature branch is not a live Salesforce connection.

- Original Salesforce MCP: https://github.com/tsmztech/mcp-server-salesforce (MIT, local stdio)
- Reused author's full 15-tool remote port: https://github.com/tsmztech/salesforce-remote-mcp-cloudflare (MIT, Streamable HTTP, Cloudflare Workers)
- Remote source pinned at commit `1924d34d73f5f883af13a257507f3fd2b92ffcb5`
- SFS addition: server-side read-only default; 8 safe discovery/query tools exposed and permitted; write/Apex execution tools disabled until explicitly opted in.
- Dedicated Cloudflare account: **Salesforce Custom MCP**; Worker subdomain: `sfs-salesforce-custom-mcp.workers.dev`; existing KV namespace: `SFS_SALESFORCE_MCP_OAUTH_KV`.
- API credentials never enter GitHub code, Actions, artifacts or chat.

## Build without Cloudflare credentials

```bash
git clone https://github.com/tsmztech/salesforce-remote-mcp-cloudflare.git upstream
git -C upstream checkout --detach 1924d34d73f5f883af13a257507f3fd2b92ffcb5
python3 salesforce-mcp-bootstrap/patch.py upstream
cd upstream
npm ci --legacy-peer-deps
npm run typecheck
npm test
npx wrangler deploy --dry-run
```

The CI workflow on this branch executes that preflight, with no environment credentials or deploy.

## After passing CI

Deploy the bundled Worker **only** in the dedicated Cloudflare account. Bind the already-created OAuth KV namespace as `OAUTH_KV` and configure the Durable Object `SalesforceMCP` migration. Use the Workers subdomain above; expected MCP route is `https://sfs-salesforce-remote-mcp.sfs-salesforce-custom-mcp.workers.dev/mcp` (not active until deployed).

Configure Salesforce Developer Edition with an OAuth-enabled External Client App; callback: `https://<actual-worker-host>/sf/callback`, supported scopes `api` and `refresh_token/offline_access`, PKCE. Store Salesforce app credentials and cookie encryption key in Cloudflare Worker secrets. Never grant production org access. Test OAuth, `ping`, schema discovery, and a read-only contact query before enabling writes.

The prompt for LangSmith should point to the **actual deployed URL only after connection verification**. No automated paid fallback is allowed. OpenRouter is not required for this Salesforce MCP server.

## Explicit blockers

- GitHub repository connector cannot create a dedicated repository or transfer private credentials.
- Salesforce OAuth client ID/secret and External Client App setup have not yet been provided or completed.
- LangSmith Fleet integration cannot be assumed from prompt content alone.
