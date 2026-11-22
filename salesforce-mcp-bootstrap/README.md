# SFS | Salesforce Remote MCP — deployment and acceptance

**Status (2026-11-10): Cloudflare Worker uploaded, public OAuth discovery and authentication boundary smoke-tested. Salesforce authorization pending.**

- Original source (MIT): https://github.com/tsmztech/mcp-server-salesforce
- Remote port (MIT): https://github.com/tsmztech/salesforce-remote-mcp-cloudflare
- Pinned source SHA: `1924d34d73f5f883af13a257507f3fd2b92ffcb5`
- Dedicated Cloudflare connection only: **Salesforce Custom MCP** (`play@sfs-labs.dev`)
- Deployed worker: `sfs-salesforce-remote-mcp`
- **MCP endpoint:** `https://sfs-salesforce-remote-mcp.sfs-salesforce-custom-mcp.workers.dev/mcp`
- **Salesforce OAuth callback:** `https://sfs-salesforce-remote-mcp.sfs-salesforce-custom-mcp.workers.dev/sf/callback`
- KV: `OAUTH_KV` -> `SFS_SALESFORCE_MCP_OAUTH_KV`
- Durable Object: `SalesforceMCP`, SQLite backing (Cloudflare generated namespace).
- Server-side `SFS_READ_ONLY=true` by default, 8 read/query tools available, 7 mutation/exec tools blocked.
- `COOKIE_ENCRYPTION_KEY` securely generated and stored as a Cloudflare Worker secret, never printed in chat or committed to Git.

## Verified

- GitHub Actions: pinned build/typechecks, unit tests, mock OAuth, Wrangler dry run.
- Cloudflare: script upload accepted, Worker deployment confirmed, URL enabled, bindings and secret verified.
- Public GitHub Actions smoke: `/` HTTP 200, `/.well-known/oauth-authorization-server` HTTP 200, unauthenticated `/mcp` HTTP 401.
- Smoke test: https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42872583807

## Remaining mandatory Salesforce OAuth setup (USER AUTHENTICATION REQUIRED)

1. Open your **Salesforce Developer Edition** in the browser.
2. Setup -> App Manager -> New External Client App, with OAuth web authorization code and PKCE.
3. Callback URL exactly: `https://sfs-salesforce-remote-mcp.sfs-salesforce-custom-mcp.workers.dev/sf/callback`.
4. API scopes: `api`, `refresh_token/offline_access`. Configure permitted users for this Developer Edition.
5. Copy the resulting Consumer Key / Client ID and Consumer Secret **only into Cloudflare Dashboard** -> Workers & Pages -> `sfs-salesforce-remote-mcp` -> Settings -> Variables and Secrets:
    - `SALESFORCE_CLIENT_ID` (Secret)
    - `SALESFORCE_CLIENT_SECRET` (Secret)
6. Never paste secrets into issues, commits, chat or public URLs.
7. In LangSmith Fleet, add a remote MCP connector with URL above. Run Salesforce OAuth in the browser.
8. Test `ping`, describe Contact object, read a synthetic Contact. Only then consider writes, through a reviewed change.

Until both Salesforce app secrets exist, the Worker is online but cannot complete Salesforce OAuth or access Salesforce data.

## Build reproducibly

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

The SFS integration remains in an isolated GitHub draft PR. Main was not modified.
