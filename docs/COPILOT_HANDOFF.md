# ChatGPT → GitHub → Copilot handoff (AI Knowledge Ops Lab)

This is the **repository-specific** execution guide. The SFS-Labs-wide trigger, skill prioritization and current Expert preparation strategy live in [central draft PR #32](https://github.com/SFS-Labs/sfs-ai-development-gateway/pull/32).

## Trigger

Whenever the user asks for work involving GitHub, SFS-Labs projects, code, PRs, evaluations, docs or CI in this repository, even if GitHub is **not** explicitly named, the assistant should apply the Copilot proficiency routing strategy as part of normal execution. This instruction applies only when read by the assistant or imported into its Project instructions; storing it in GitHub **does not change ChatGPT settings**.

## Decision procedure

1. Read latest README, relevant paths, open issues/PRs, current tests, existing `.github/copilot-instructions.md` and approval rules.
2. Define deliverable, constraints, evidence, the smallest independently reviewable diff.
3. Select a supported **actual Copilot** surface when it adds value: cloud agent for suitable bounded development, Copilot PR review for real changes, Copilot GitHub chat for exploration, IDE Chat/inline/next-edit or CLI only when an actual IDE/CLI session is in use. Consider suitable agent skill/MCP/model selection for complex work; no complexity for its own sake.
4. When cloud agent is suitable and sufficiently available, create a GitHub Issue with objective, files, acceptance, test commands, negative cases, data/cost/permissions boundaries. Assign official Copilot. Verify **execution** by observing its events/PR, not just the assignee field.
5. If Copilot cannot start, record its exact reason and proceed with the existing GitHub connector or other permitted tool. **Do not assert that the fallback contributes to Copilot Verified Proficiency.**
6. Review the full diff and exact HEAD; inspect CI and test evidence, never infer success from the fact that a PR exists. No automated merge or unapproved spend.

### Known live blocker on 2026-11-13

[Issue #55](https://github.com/SFS-Labs/ai-knowledge-ops-lab/issues/55) accepted an assignment to Copilot, but Copilot commented that there were **insufficient GitHub AI Credits** to start a session. This is a **failed execution attempt**, not a completed Copilot contribution, and this documentation PR is being prepared through the ordinary ChatGPT GitHub connector. Recheck before a future assignment; do not silently trigger paid usage.

## Opportunity checklist (apply only to real tasks)

| Domain | Useful demonstrated Copilot behavior |
| --- | --- |
| AI Collaboration | Copilot coding-agent PR, Copilot-assisted review or GitHub.com chat |
| Prompting | Specific Copilot context, acceptance criteria, iterative debugging |
| Code Generation & Validation | Copilot-assisted implementation + verifiable positive/negative regression testing |
| Agent Configuration | Instructions, meaningful skill or custom agent actually used |
| Tool & Context Integration | Approved MCP/CLI/SDK/context source actually invoked in Copilot |
| Advanced preparation | Explicit model/tool tradeoffs, tested agent workflow, measured improvement |
| Expert preparation | Reusable capability, multi-agent coordination when needed, memory/state/evaluation, guardrails and deterministic alternative |

**Evaluation rule:** GitHub's official framework considers breadth, depth, and consistency of **real Copilot usage**; it does not publish the Advanced/Expert scoring algorithm. Do not claim a level increase from any one action. The most economical approach is to improve real project outcomes while gradually covering still-missing features across different real projects and over time.

## Smallest possible evidence note

```text
Outcome:
Actual Copilot activity (if any):
Evidence (Issue/PR/agent comment/check):
Relevant skill domains:
Tests and limitations:
Unexercised feature / reason:
```

Keep this note in the existing PR or issue. No new tracker is mandatory. The real Copilot proficiency dashboard is the authority for level changes.

## References

- https://learn.github.com/proficiencies/copilot/
- https://learn.github.com/learning-pathways/github-copilot
