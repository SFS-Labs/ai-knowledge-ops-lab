# Langfuse v4 readiness — code-only audit (2026-11-11)

**Repository inspected:** [SFS-Labs/ai-knowledge-ops-lab](https://github.com/SFS-Labs/ai-knowledge-ops-lab), default branch `main`; inspected Git tree commit `fbec303208dedaf2b3cdeb43b3bbd276243b1c6d` (95 entries). This repository is the last explicitly identified repository in the working context, **not a verified Langfuse application**.

**Outcome:** No Langfuse implementation was identifiable in the inspected repository. No SDK can truthfully be upgraded, and no trace/evaluator/export configuration may be inferred from the existence of local evaluation scripts. This is a **readiness audit, not a completed platform migration**. No application code, deployment configuration, SDK versions or lockfiles were changed.

## Evidence and scope

- GitHub code search scoped to this repository's indexed default branch returned **no matches** for `Langfuse`, `LANGFUSE_PUBLIC_KEY`, `/api/public`, `OpenTelemetry`, `otlp`, `mixpanel`, or `posthog`.
- The default-branch tree has no identified Langfuse SDK, dependency manifest, lockfile, OTel exporter or Langfuse-specific configuration file. **Declared Langfuse SDK version: not present; resolved version: not present.**
- Reviewed `README.md`, `docs/architecture.md`, `docs/evaluation.md`, `knowledge_ops/evaluate.py`, `knowledge_ops/export.py`, and `.github/workflows/ci.yml`. The documented evaluation is a local deterministic scorecard and the export is a static JSON replay; neither establishes a Langfuse evaluator or enriched-observation export.
- GitHub search is restricted to the default branch and may omit non-indexed content; this is not evidence about other repositories, deployed services, private configuration, or the live Langfuse project.
- Draft PR #32 (`feat/sfs-salesforce-remote-mcp`) is separate work; this audit does not modify it.

## Seven-row readiness report

| Area | Status | Evidence, blocker and next action |
| --- | --- | --- |
| project access | **blocked** | No confirmed Langfuse host/project or authorized project interface. **Next:** confirm the target host and project using an already configured project connection; inspect the migration status. For Langfuse Cloud, open [the Langfuse console](https://cloud.langfuse.com); self-hosted projects must use their own confirmed host. Do not request or commit credentials. |
| SDK/instrumentation | **blocked** | No Langfuse SDK, exporter, initializer, version, lockfile or trace-propagation code found in the inspected repo; no implementation exists here to migrate. **Next:** locate and identify the actual code/deployment that sends traces, check the target server version, then upgrade the existing SDK and instrument root input/output, inherited session/user/tags/metadata, and cost-bearing children. Current GA majors are Python v5 and JS/TS v6 **only** when server compatibility permits. |
| trace evaluators | **blocked** | **Project-verified contracts: none. Candidate targets from code: none.** Local `knowledge_ops/evaluate.py` is not a Langfuse rule. **Next:** inspect active legacy trace rules, definition, filters, mappings, sample traces and observations in [Evaluators](https://cloud.langfuse.com/project/~/evals) on the *confirmed Cloud host* (or self-hosted equivalent). Create successor observation rules **disabled**, validate with new observations, then enable only after approval; preserve legacy rules for rollback. |
| dataset evaluators | **blocked** | **Project-verified contracts: none. Candidate targets from code: none.** No Langfuse dataset evaluator contract found in this codebase. **Next:** inspect active legacy dataset rules and representative experiment items in [Evaluators](https://cloud.langfuse.com/project/~/evals), map them to experiment targets and test score parity before deactivation. |
| direct APIs | **ready** | No Langfuse direct REST API/legacy ingestion references were found by the scoped code search or selected source inspection. **No migration edit is applicable in this inspected default branch.** This does not certify uninspected deployment or project code; repeat the inventory if the actual instrumented repository is different. |
| exports | **blocked** | No Langfuse Blob Storage, Mixpanel or PostHog export setup found in code; **live project integration state is unknown**. **Next:** inspect **Project Settings > Integrations** on the confirmed [Langfuse host](https://cloud.langfuse.com), inventory active sources and downstream consumers, and validate the documented dual-source/enriched-observation migration before switching. Preserve credentials, schedules and formats. |
| verification/rollback | **blocked** | No migrated instrumentation to run or non-production Langfuse project to inspect; no live-ingestion, session-cost, API pagination, evaluator-score or downstream-export test has been performed. **Next:** after locating the actual implementation, run repository regressions, ingest representative traces to a non-production project and inspect root/child observation attributes and costs; compare evaluator scores, then verify the UI and retain disabled legacy rules until cutover is approved. |

## Verification performed

1. Read the canonical [Langfuse v4 project migration workflow](https://raw.githubusercontent.com/langfuse/skills/main/skills/langfuse/references/v4-project-migration.md) and [Langfuse upgrade guide](https://langfuse.com/faq/all/upgrade-to-langfuse-v4).
2. Inspected the default-branch tree and scoped GitHub code-search results; read the repository files listed above.
3. No code or lockfile edits were justified, so **no migration unit tests, SDK resolution, CI run, or backend smoke test can be claimed**. This document can be checked structurally, but that is not an ingestion test.

**Cutover caveat:** Langfuse Cloud's published v4 removal date for legacy APIs and ingestion is **2026-11-16**; self-hosted deployments follow their own upgrade schedule. See [compatibility](https://langfuse.com/docs/compatibility).

**Rollback boundary:** No production Langfuse configuration or code was changed by this audit. If migration work later proceeds, use reversible commits and preserve legacy evaluator rules disabled (not deleted) until the new rules are verified.
