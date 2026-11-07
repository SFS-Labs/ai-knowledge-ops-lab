# SFS Labs | Decision Evidence Brief — B2B AI Intake

**Read time:** ~2 minutes. **Purpose:** assess a candidate's technical judgment and research discipline, not the visual complexity of a demo.

## Business problem

Incoming B2B requests must be classified by service type and urgency before an authorized operator decides what happens next. A working LLM integration alone is not enough: accuracy, escalation risk, review workload and business costs can favor different components.

## What changed as we examined the evidence

1. **Observed reality, not a staged demo.** A pinned local Qwen model ran real HTTP inference through n8n and SQLite with separate simulated approval, rejection, restart and outage checks. [CI #24: exact-SHA green](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42399345922). Its 36 genuinely executed model responses, including 32 labeled cases, were frozen for inspection.
2. **Counterintuitive result.** Model category was right **30/32**, keyword baseline **13/32**. But model urgency was right only **10/32**, keyword urgency **24/32**. A single-method winner was the wrong framing.
3. **Operator hypothesis.** Assign **category to validated semantic extraction**, **urgency to deterministic rules**, and keep **authorization separate**. The post-hoc combined accuracy was **22/32** versus **10/32 model-only** and **11/32 rules-only**. A source-attributed experimental policy and tests were added on the same Draft PR.
4. **Adversarial challenge to our own idea.** The keyword rules missed **5/9 high-urgency** examples; the LLM missed **1/9**, but generated **21 false high** alerts. Our conditional miss-cost / false-alert-cost break-even was **5.25**. So hybrid pair accuracy does not establish that the hybrid is optimal for a real customer.
5. **Methodological correction.** The observed paired exact McNemar p-value of **0.00342** is **not confirmatory**, because the hybrid idea was selected from those very observations. Instead of inflating the same synthetic dataset, we specified a prospective **480-case planning target** with independent case-family provenance, two blinded labels, pre-inference lock and falsification criteria. **Those 480 cases do not exist yet.**

## Decision

**Use the hybrid as a bounded experiment, not a production claim.** Disagreements, malformed output and missing information go to manual review. The model never grants approval. Prospective evidence and a customer's documented SLA, cost and review constraints must determine whether the hybrid actually wins.

## What a hiring manager can verify

- [Full decision record and alternative hypotheses](HYBRID_DECISION_RECORD.md)
- [Prospective evaluation protocol and economic loss criteria](STUDY_PROTOCOL_V1.md)
- [Frozen observed model outputs](evaluation/evidence/ci24-observed-model-output.json)
- [Reproduce pairwise comparison](evaluation/compare_routing.py), [paired statistics](evaluation/study_statistics.py), [economic break-even](evaluation/economics.py), [integrity gate](evaluation/holdout_gate.py)
- [Current Draft PR with implementation and tests](https://github.com/SFS-Labs/ai-knowledge-ops-lab/pull/9)

**Evidence boundaries:** The original model/n8n E2E passed on commit `d02a76f`. The later hybrid and study tools are **IMPLEMENTED / NOT YET EXACT-HEAD CI VERIFIED**. No external customer, paid deployment, independently verified human identity, proven ROI or objectively quantified comparison to other applicants is claimed.

**Contribution attribution:** The project owner developed the hybrid-routing question and insisted on scientific/methodological scrutiny; AI assistance supported analysis, implementation and documentation. The work sample demonstrates *how decisions are made and corrected* rather than claiming unaided authorship of all code.
