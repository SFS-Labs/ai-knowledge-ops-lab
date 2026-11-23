# SFS Interactive — Public source supplement, 2026-11-23

**Purpose:** Evidence-only supplement to the public portfolio and ElevenLabs agent. This document is a dated GitHub source snapshot, NOT a live-synchronized knowledge base. Private repositories and blind-evaluation reference material are outside scope.

## Release state and correct live links (23 November 2026)

**Important:** The newly authored `security-engineering.html`, `adversarial-evaluation.html`, `agent-systems.html`, and `work.html` are on draft website PR #58, **not yet published on production GitHub Pages**. Do not claim a production `sfs-labs.github.io` page works before merge.

Current clickable public development preview:
- Portfolio and opt-in voice agent: https://sfs-portfolio-v2-preview.sfs-labs-core.workers.dev/interactive.html
- Cybersecurity / CTF case: https://sfs-portfolio-v2-preview.sfs-labs-core.workers.dev/security-engineering.html
- Native benchmark case: https://sfs-portfolio-v2-preview.sfs-labs-core.workers.dev/adversarial-evaluation.html
- REA/MCP case: https://sfs-portfolio-v2-preview.sfs-labs-core.workers.dev/agent-systems.html
- Curated engineering work: https://sfs-portfolio-v2-preview.sfs-labs-core.workers.dev/work.html

The canonical public GitHub repositories and merged commit / run links in the other sections can be used as live primary sources. The `open_project` tool only displays an allowlisted link in the webpage; do not promise that it opens a browser tab automatically. After publishing the site, the knowledge-base source URLs must be refreshed.

## Agent ground rules
- Speak about Mathias Steinbach in the third person. Never claim to be him.
- Distinguish merged integration, separate draft PR, historically executed local toolchain, blind discovery, and independent verification.
- Source labels, measurements and limitations must remain attached to each numeric claim.
- Public documentation is AI-assisted; do not attribute upstream MIT-licensed CTF skills to SFS-Labs.
- Do not claim live repository status unless it was really fetched through an approved live tool.
- Protect private repositories, proprietary data, hidden benchmark references and sensitive personal records.

## Cybersecurity · Penetration Testing · CTF Engineering
Case study: https://sfs-labs.github.io/ai-knowledge-ops-lab/security-engineering.html
Canonical repository: https://github.com/SFS-Labs/ctf-skills
At 22 November 2026 merged PR #2 and PR #3 consolidated 133 distinct knowledge cards from 134 source records (one alias) and V8/V9 runtime integration. THESE ARE NOT 133 INSTALLED EXECUTABLE SCANNERS.
Commit for the V8/V9 integration reported 170 passed tests, 2 skipped tests, and 1616 subtests. Source: https://github.com/SFS-Labs/ctf-skills/pull/3
Historical local Mac mini run: Surya contract map, 12 Slither findings, 3 passed Forge tests on an intentionally vulnerable Vault, negative control and evidence verification. An actual skill() invocation by a newly restarted new local agent session was NOT verified. Source: https://github.com/SFS-Labs/ctf-skills/blob/main/docs/FREEBUFF-V8-RUNTIME-ACCEPTANCE.md
Local tool inventory from 21 November reported 22 executable tools, not all factory source repositories. Source: https://github.com/SFS-Labs/ctf-skills/blob/main/STATUS.md
Echidna located a known invariant breach where Medusa did not in the dated run. Source: https://github.com/SFS-Labs/ctf-skills/blob/main/VERIFICATION.md
SEPARATE DRAFT PR #4: https://github.com/SFS-Labs/ctf-skills/pull/4 ; head reported 184 passed tests, 2 skips, 1616 subtests. No verified independent RUN-A/B blind evaluation. Do not conflate this draft with merged main or real agent skill activation.
Never claim zero-day discovery, generalized autonomous detection rates, real bug-bounty bounty income, client auditing, or earned Copilot Proficiency.

## Agent Orchestration / Camber / REA
Case study: https://sfs-labs.github.io/ai-knowledge-ops-lab/agent-systems.html
Repository: https://github.com/SFS-Labs/security-reviews
Historical 28 October 2026: Real Camber selection of three read-only REA tools, then an actual GitHub Actions run enumerating 229 MCP tools and executing 3 specifically allowed MCP tool calls. 33 validation checks passed. The runner had fixed allowlist and maximum three calls, with empty arguments. It did NOT investigate any APK or Android device. An unattended fresh Camber model invocation was NOT verified.
Primary run: https://github.com/SFS-Labs/security-reviews/actions/runs/40716523503
Acceptance report: https://github.com/SFS-Labs/security-reviews/blob/main/docs/CAMBER_MULTITOOL_ACCEPTANCE.md
Open autonomy issue: https://github.com/SFS-Labs/security-reviews/issues/5

## POINCARE scope-limited Solidity review
Public report: https://github.com/SFS-Labs/SFS-Labs/blob/main/security-review/case-studies/poincare-2026.md
October 24-26 2026: seven Solidity files, approximately 1298 LOC, independent reproduction of 222 original Foundry tests, two Low findings and eight Notes. Source-level follow-up of nine remediation commits across 26 files. Maintainer claimed 240 revised tests, NOT independently rerun. No formal audit certificate or guarantee.

## Previously evidenced work
HubSpot Stripe: https://sfs-labs.github.io/ai-knowledge-ops-lab/hubspot-stripe.html ; modeled/synthetic, no measured customer ROI.
AI Knowledge Ops: https://github.com/SFS-Labs/ai-knowledge-ops-lab/blob/main/showcases/internal-service-intake/DECISION_EVIDENCE_BRIEF.md ; real pipeline tests, synthetic routing with unsafe missed urgency.
Tender: https://github.com/SFS-Labs/tender-intelligence-case-study/blob/main/docs/DECISION-LOG.md ; commercial development paused after no supported A/B improvement.
Genomics: https://github.com/SFS-Labs/sfs-genomics/blob/main/genomics/PORTFOLIO.md ; engineering, not clinical validation.
Value Rail: https://github.com/SFS-Labs/value-rail-mvp ; historical offline tests, no trading outcome.
Education Funding: https://github.com/SFS-Labs/SFS-Labs/blob/main/case-studies/education-funding.md ; historical zero verified funding programs.

## Publication and KB status
23 visible organization repositories include private and inherited/archived content, not 23 personal published case studies. Ten source-backed items are curated in work.html. This dated source supplement is prepared on a GitHub review branch. The separately created V2 ElevenLabs agent now uses an indexed document based on this material; the original production agent remains in a different, currently inaccessible workspace. V2 RAG retrieval is confirmed, but a real voice conversation and client-tool execution still require independent browser verification.

## Native CTF / adversarial benchmark evaluation (independent workstream)
Case study: https://sfs-labs.github.io/ai-knowledge-ops-lab/adversarial-evaluation.html
Historic canonical source: https://github.com/SFS-Labs/ctf-skill-factory/blob/main/benchmarks/README.md
On 21 November 2026, the native evaluation adapters for CyberChainBench and ReEVMBench were merged. A later merged PR #5 addressed original DeFiHackLabs forge-std submodule source pinning and a mismatched ReEVMBench judge-model alias. The documented calibration runs show compiler/runtime progress and infrastructure failures: historical RPC replay HTTP 429 (CyberChainBench); solver construction error prior to fix (ReEVMBench). No independently confirmed autonomous blindtest score. See https://github.com/SFS-Labs/ctf-skill-factory/pull/5 .
