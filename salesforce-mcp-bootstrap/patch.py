#!/usr/bin/env python3
"""Apply SFS read-only-by-default policy to the pinned MIT-licensed upstream remote MCP."""
from pathlib import Path
import subprocess
import sys

PIN = "1924d34d73f5f883af13a257507f3fd2b92ffcb5"
POLICY = '''import type { Tool } from "@modelcontextprotocol/sdk/types.js";

export const READ_ONLY_NAMES = new Set([
  "ping",
  "salesforce_search_objects",
  "salesforce_describe_object",
  "salesforce_query_records",
  "salesforce_aggregate_query",
  "salesforce_search_all",
  "salesforce_read_apex",
  "salesforce_read_apex_trigger",
]);

export function isToolAllowed(name: string, readOnly: boolean): boolean {
  return !readOnly || READ_ONLY_NAMES.has(name);
}

export function visibleTools(tools: Tool[], readOnly: boolean): Tool[] {
  return tools.filter(tool => isToolAllowed(tool.name, readOnly));
}
'''
TESTS = '''import { describe, expect, it } from "vitest";
import { TOOLS } from "../src/mcp/toolRegistry";
import { isToolAllowed, visibleTools, READ_ONLY_NAMES } from "../src/mcp/accessPolicy";

describe("SFS read-only MCP tool policy", () => {
  it("advertises only eight read-only tools", () => {
    const names = visibleTools(TOOLS, true).map(tool => tool.name);
    expect(new Set(names)).toEqual(READ_ONLY_NAMES);
    expect(names).not.toContain("salesforce_dml_records");
    expect(names).not.toContain("salesforce_execute_anonymous");
  });
  it("rejects unadvertised tools even when called directly", () => {
    for (const tool of TOOLS) {
      expect(isToolAllowed(tool.name, true)).toBe(READ_ONLY_NAMES.has(tool.name));
    }
    expect(isToolAllowed("unknown_tool", true)).toBe(false);
  });
  it("restores upstream registry on explicit write opt-in", () => {
    expect(visibleTools(TOOLS, false)).toEqual(TOOLS);
  });
});
'''

def substitute(s: str, old: str, new: str, path: str) -> str:
    n = s.count(old)
    if n != 1:
        raise RuntimeError(f"{path}: expected one match for {old!r}, got {n}")
    return s.replace(old, new, 1)

def main(root: Path):
    root = root.resolve()
    sha = subprocess.check_output(["git", "-C", str(root), "rev-parse", "HEAD"], text=True).strip()
    if sha != PIN:
        raise RuntimeError(f"Unexpected upstream revision {sha}, expected {PIN}")
    agent = root / "src/mcp/salesforceAgent.ts"
    env = root / "src/env-extra.d.ts"
    wrangler = root / "wrangler.jsonc"
    a = agent.read_text()
    e = env.read_text()
    w = wrangler.read_text()
    a = substitute(a, 'import { TOOLS } from "./toolRegistry";',
                   'import { TOOLS } from "./toolRegistry";\nimport { isToolAllowed, visibleTools } from "./accessPolicy";', str(agent))
    a = substitute(a, "tools: TOOLS,",
                   'tools: visibleTools(TOOLS, this.env.SFS_READ_ONLY !== "false"),', str(agent))
    a = substitute(a, "        const props = this.effectiveProps();",
                   '''        if (!isToolAllowed(name, this.env.SFS_READ_ONLY !== "false")) {
          return {
            content: [{ type: "text", text: "Tool disabled by SFS read-only policy." }],
            isError: true,
          };
        }
        const props = this.effectiveProps();''', str(agent))
    e = substitute(e, "  SALESFORCE_API_VERSION?: string;",
                   "  SALESFORCE_API_VERSION?: string;\n  SFS_READ_ONLY?: string;", str(env))
    w = substitute(w, '"name": "salesforce-remote-mcp-cloudflare"',
                   '"name": "sfs-salesforce-remote-mcp"', str(wrangler))
    w = substitute(w, '"SALESFORCE_LOGIN_HOST": "login.salesforce.com"',
                   '"SALESFORCE_LOGIN_HOST": "login.salesforce.com", "SFS_READ_ONLY": "true"', str(wrangler))
    w = substitute(w, '"id": "REPLACE_WITH_YOUR_KV_NAMESPACE_ID"',
                   '"id": "d34ce8cc45574d069298a2fe3b15aeb6"', str(wrangler))
    # Apply only after all expected upstream anchors match; no partial edits.
    (root / "src/mcp/accessPolicy.ts").write_text(POLICY)
    (root / "test/accessPolicy.test.ts").write_text(TESTS)
    agent.write_text(a)
    env.write_text(e)
    wrangler.write_text(w)
    print("SFS read-only overlay applied at pinned upstream commit", PIN)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        raise SystemExit("usage: python3 patch.py PATH_TO_UPSTREAM")
    main(Path(sys.argv[1]))
