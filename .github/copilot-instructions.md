# GitHub Copilot instructions — SFS-Labs/ai-knowledge-ops-lab

This repository is an evidence-first AI integration and evaluation laboratory, **not** a production-ready customer service or autonomous decision system. Follow the current README and the documentation for the relevant subsystem before editing.

## Work efficiently and safely

- First determine the exact task scope, affected subsystem and current executable checks. Do not refactor unrelated areas, replace the frozen data manifest, or update historic outcomes simply to improve a narrative.
- Default reproducible offline test: `python -m unittest discover -s tests -v` with Python 3.12+. Individual research/audit scripts can require external primary sources; do not silently invoke network tests or paid inference.
- The repository contains **distinct** streams (SEC 8-K processing and internal service intake with NLBSE/Volvo research). Do not mix their label taxonomies, test samples, measured effects or financial assumptions.
- Respect provenance: recorded model outputs are not live inference; synthetic cases are not real customer outcomes; unreviewed labels are not verified ground truth. Never claim accuracy, semantic support, cost savings or production readiness absent direct evidence.
- Preserve review/reject/fail-closed semantics, integrity checks, explicit approval boundaries and deterministic baselines. Never weaken assertions or safety controls merely to make tests green.
- Never add private datasets, customer or employer information, credentials, tokens, external model requests, paid resources, new services or deployment configuration without an explicitly scoped approval.
- Proposed changes must include a readable diff, precise test results (**run** vs **not run**), limitations and a reviewable PR. Do not auto-merge.

## Purposeful Copilot proficiency development (secondary objective)

Use Copilot for **real engineering** across the five official skill areas where beneficial: (1) AI Collaboration, (2) Prompting, (3) Code Generation & Validation, (4) Agent Configuration, (5) Tool & Context Integration.

- Prefer outcome-oriented, bounded tasks with explicit acceptance criteria, tests and negative cases; use Copilot cloud agent, Copilot PR review and GitHub.com chat where relevant and available.
- Reuse suitable repository instructions, prompts, agents, agent skills and approved MCP integrations **only when they solve a genuine problem**. Choose model/tool/context deliberately; document tradeoffs when they materially affect the result.
- For advanced work, prioritize useful evaluation, reusable orchestration, state handling and guardrails over extra agents or activity. Use deterministic code if more appropriate.
- Record actual Copilot feature usage and evidence in the PR/issue only when observed. Never count ordinary GitHub connector activity as Copilot usage, or suggest that doing these tasks guarantees a proficiency level.
- If Copilot has no AI credits or the requested feature is unavailable, report the block, use an authorized alternative and do **not** claim a Copilot-completed task.

For cross-repository task selection and official GitHub Proficiency references, consult the proposed central standard:
`SFS-Labs/sfs-ai-development-gateway/docs/COPILOT_PROFICIENCY_OPERATING_STANDARD.md` (currently Draft PR #32). This file is not automatically available inside Copilot's context in another repository; the user/assistant must provide relevant instructions in the assignment.
