# The decision is the evidence | B2B AI intake

## In 30 seconds

**Problem:** A real local B2B-AI intake pipeline worked, but choosing one classifier was the wrong question: LLM-only classified both fields correctly in **10/32** labeled cases; rules-only in **11/32**.

**Hypothesis:** Give category to the validated LLM and urgency to deterministic rules. The **post-hoc** hybrid replay reached **22/32**.

**Counterexample:** Rules missed **5/9** high-urgency cases. When missed incidents are expensive, the higher-accuracy hybrid can still be the worse business decision.

**Decision:** Implement traceable hybrid routing; send conflicts to manual review; keep approval separate. Require independent validation before claiming business value. The original hybrid passed CI #25; later research changes have separate verification gates.

## The part I would defend in an interview

The relevant skill is **not** selecting the technology with the best headline metric. It is assigning responsibility by comparative advantage, finding the counterexample that could reverse the decision and refusing an economic or statistical claim without appropriate evidence.

**Question to challenge the decision:** If the customer loses far more from an overlooked high-priority request than from an unnecessary escalation, would I still choose the hybrid? **Not necessarily.** On the observed synthetic pilot, the hybrid avoids 21 false-high calls but adds four missed-high cases compared with LLM-only. Ignoring other costs, the economic preference flips when `C(missed high) / C(false high)` crosses **5.25**. The calculation is conditional; no customer cost figures have been observed.

This also explains why the pilot McNemar p-value of 0.00342 is **exploratory, not confirmatory**: the hypothesis was chosen after seeing the data. Enlarging the same test set with paraphrases would not solve that methodological flaw.

## Reproduce, challenge, or reject the decision

| Inspect | Direct evidence | What it does **not** prove |
|---|---|---|
| Genuine inference | [CI #25, 100 tests and real local LLM/n8n E2E](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42405856175) and [36 frozen pilot outputs](evaluation/evidence/ci24-observed-model-output.json) | Generalizable customer performance or current research-dataset LLM quality |
| Comparison | [Post-hoc replay](evaluation/compare_routing.py) and [paired statistics](evaluation/study_statistics.py) | Generalization to customers or a prospective result |
| Changed decision | [Source-attributed policy implementation](mock-api/semantic.py) and [tests](../../tests/test_hybrid_policy.py) | Verified human approver or automatic approval |
| Business trade-off | [Cost sensitivity](evaluation/economics.py) | Observed € savings or universally optimal strategy |
| Independent challenge | [New business-first NLBSE/Volvo design](RESEARCH_DESIGN.md), [native class contract](evaluation/research_contract.json) and [original-data audits](evaluation/nlbse_source.py) | Same-case matching between the two source populations, customer impact or actual AI savings |
| Completion criterion | [Machine-checkable decision gate](evaluation/decision_gate.py) and [decision record](DECISION_CASE.json) | Independent confirmation of any later exact-release-head CI conclusion |

**Decision status:** Original local LLM/n8n/hybrid engineering **VERIFIED** in CI #25 at `d4a8391` (100 tests). **New source-data research** is separately gated and cannot inherit the historical CI result. No customer deployment, measured ROI or independently verified human authorization.

**Current business-first continuation:** The [60-second static illustration](../../docs/index.html) combines real Volvo process-aggregate evidence with explicit assumptions, while [NLBSE issue-class labels](RESEARCH_DESIGN.md) form an independent classification stream. Actual customer-cost validation would require consented tickets and intervention data and is **not a prerequisite for paid delivery roles**.

## Attribution and deeper examination

The project owner proposed the component-level hybrid-routing hypothesis and demanded explicit methodological and business counterchecks. The AI assistant supported computation, adverse-case analysis, implementation and documentation. No claim of unaided authorship or quantified superiority to a candidate cohort is made.

Read [DR-001: the full reasoning trail](HYBRID_DECISION_RECORD.md) for alternatives, falsifiers and limitations; read [DR-002: the conditional research protocol](STUDY_PROTOCOL_V1.md) only if the sampling or economic evaluation is the topic of the discussion.
