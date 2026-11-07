# DR-001 · An exploratory hybrid decision, not a customer ROI result

**Original decision date:** 7 November 2026 · **Pilot status:** VERIFIED technically at [CI #25 on exact SHA `d4a8391`](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42405856175) · **Research status:** original 32 labeled examples synthetic, retrospectively assessed · **New business-data programme:** [Business-first research design](RESEARCH_DESIGN.md).

## In 30 seconds: how the thinking changed

The working synthetic n8n→local-LLM→SQLite prototype raised a question: **why pick one model to decide everything?** Its real CPU inference on 32 labeled *synthetic* scenarios produced **10/32** jointly correct category-and-urgency decisions, compared to **11/32** for the original deterministic baseline.

The operator proposed **LLM for category, rules for urgency**. The retrospective recombination delivered **22/32** on those same examples. But the rules missed **5/9 high-priority labels**, versus the LLM's **1/9**. Therefore the apparent accuracy winner can be the financially worse choice where missed critical work is expensive. **We did not hide this counterexample.**

## Method and authorship

- **Operator hypothesis:** assign responsibilities according to comparative advantage; separate engineering and authorization; analyze the business risk of the supposedly better classification.
- **AI-assisted implementation:** fixed [hybrid routing](mock-api/semantic.py) and [source attribution](evaluation/compare_routing.py), preserved approval gate, added tests and cost checks.
- **Observed evidence:** [36 actual local CPU inference outputs from CI #24](evaluation/evidence/ci24-observed-model-output.json), 32 labeled. Not linked to NLBSE 2023 or Volvo incidents.
- **Statistical limitation:** paired hybrid vs rules table: both correct 10, hybrid only 12, rules only 1, both wrong 9. Exact two-sided McNemar p≈0.00342 is **POST-HOC EXPLORATORY**, because the hybrid proposal was made after observing these cases. This is not a prospective confirmatory experiment.
- **Business limit:** compared with LLM-only, the hybrid on these 32 examples had **four extra missed high** versus **21 fewer false-high** cases. Their conditional break-even is `C(missed high)/C(false high)=21/4=5.25`, **ignoring** review and operating costs. No real customer impact was observed.

## What we corrected in the research plan

The earlier investigation was backwards: we started with a demo and four assumed categories, **Analytics, Automation, Integration, Incident Response**. Those categories were **not source labels** of our later public datasets, and domain and request urgency can overlap. A deployed client system must define taxonomy **from its business task first**.

Therefore the newer evidence architecture has **two deliberately unlinked streams**:
1. NLBSE 2023 actual harmonized source issue types `bug/feature/question/documentation` for genuine software-request classification. Source labels remain source labels; no imaginary urgency or ROI.
2. MD5-verified Volvo BPIC 2013 incidents for actual process traces; **9,454 observed group transitions** in **7,554 incidents**, source audited in [CI #27](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42411756411). These transitions are not proof of preventable work.

The €58.50/h 2025 Destatis information-and-communication average is used only for **explicit hypothetical scenario costs**. It is not Volvo wage data. The [research contract](evaluation/research_contract.json) and [static interactive demo](../../docs/index.html) make the boundary machine-readable and understandable to non-technical reviewers.

## Binding completion standard — the decision, not feature count

1. **Understandable in 30–60 seconds:** problem, plausible business result, strongest counterexample, outcome and next question, all sourced.
2. **Auditable:** original data and source licenses, hashes, exact-commit CI runs, code and independent review paths.
3. **Falsifiable:** document when a different policy becomes better; don't chase significance by inflating correlated prompts.
4. **Engineering-verified:** unit tests, real local model/n8n E2E and separate research-source gates on the **exact commit being released**.
5. **Honest endpoint:** publish an explainable static demonstration once release checks pass; do not deploy insecure n8n endpoints and do not claim observed savings or customer operations without a real pilot.

A future independent source of user requests or customer SLA/time studies is a possible *new evidence gate*, **not a prerequisite for paid market entry**. The correct outcome today is a technical/research work sample with validated historical data and explicit commercial uncertainty.

**Attribution:** The owner formed the hybrid-routing hypothesis and required adversarial, scientific and business validation. The assistant supported quantitative analysis, scripts and repo engineering. This work does not prove relative intelligence or an independent human customer deployment.
