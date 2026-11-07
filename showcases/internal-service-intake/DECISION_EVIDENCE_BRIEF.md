# The decision is the evidence | B2B AI intake

## In 30 seconds

**Problem:** A real local B2B-AI intake pipeline worked, but choosing one classifier was the wrong question: LLM-only classified both fields correctly in **10/32** labeled cases; rules-only in **11/32**.

**Hypothesis:** Give category to the validated LLM and urgency to deterministic rules. The **post-hoc** hybrid replay reached **22/32**.

**Counterexample:** Rules missed **5/9** high-urgency cases. When missed incidents are expensive, the higher-accuracy hybrid can still be the worse business decision.

**Decision:** Implement traceable hybrid routing; send conflicts to manual review; keep approval separate. Require independent validation before claiming business value. Current changes await CI.

## The part I would defend in an interview

The relevant skill is **not** selecting the technology with the best headline metric. It is assigning responsibility by comparative advantage, finding the counterexample that could reverse the decision and refusing an economic or statistical claim without appropriate evidence.

**Question to challenge the decision:** If the customer loses far more from an overlooked high-priority request than from an unnecessary escalation, would I still choose the hybrid? **Not necessarily.** On the observed synthetic pilot, the hybrid avoids 21 false-high calls but adds four missed-high cases compared with LLM-only. Ignoring other costs, the economic preference flips when `C(missed high) / C(false high)` crosses **5.25**. The calculation is conditional; no customer cost figures have been observed.

This also explains why the pilot McNemar p-value of 0.00342 is **exploratory, not confirmatory**: the hypothesis was chosen after seeing the data. Enlarging the same test set with paraphrases would not solve that methodological flaw.

## Reproduce, challenge, or reject the decision

| Inspect | Direct evidence | What it does **not** prove |
|---|---|---|
| Genuine inference | [CI #24 on historical exact SHA `d02a76f`](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42399345922) and [36 frozen outputs](evaluation/evidence/ci24-observed-model-output.json) | Current Draft HEAD passing CI |
| Comparison | [Post-hoc replay](evaluation/compare_routing.py) and [paired statistics](evaluation/study_statistics.py) | Generalization to customers or a prospective result |
| Changed decision | [Source-attributed policy implementation](mock-api/semantic.py) and [tests](../../tests/test_hybrid_policy.py) | Verified human approver or automatic approval |
| Business trade-off | [Cost sensitivity](evaluation/economics.py) | Observed € savings or universally optimal strategy |
| Independent challenge | [Prospective study plan](STUDY_PROTOCOL_V1.md) and [data integrity checks](evaluation/holdout_gate.py) | 480 cases already collected or independently labeled |
| Completion criterion | [Machine-checkable decision gate](evaluation/decision_gate.py) and [decision record](DECISION_CASE.json) | Remote CI success before an exact-HEAD run |

**Decision status:** Original local-model technical chain **VERIFIED** at SHA `d02a76f`; hybrid change and method code **IMPLEMENTED, pending exact-HEAD CI**. No customer deployment, measured ROI or independently verified human authorization.

**Work boundary:** The next controlled step is exact-HEAD CI on [existing Draft PR #9](https://github.com/SFS-Labs/ai-knowledge-ops-lab/pull/9), deliberately not initiated here. Independent holdout collection and customer-cost validation occur **only when credible sources and a concrete commercial decision justify them**, not as a prerequisite for applying to paid delivery roles.

## Attribution and deeper examination

The project owner proposed the component-level hybrid-routing hypothesis and demanded explicit methodological and business counterchecks. The AI assistant supported computation, adverse-case analysis, implementation and documentation. No claim of unaided authorship or quantified superiority to a candidate cohort is made.

Read [DR-001: the full reasoning trail](HYBRID_DECISION_RECORD.md) for alternatives, falsifiers and limitations; read [DR-002: the conditional research protocol](STUDY_PROTOCOL_V1.md) only if the sampling or economic evaluation is the topic of the discussion.
