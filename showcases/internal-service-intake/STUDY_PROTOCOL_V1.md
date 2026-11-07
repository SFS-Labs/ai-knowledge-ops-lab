# DR-002 — Prospective Evaluation Protocol (v1.0; pre-registration proposal)

**Document status:** SPECIFIED / NOT YET EXECUTED  
**Owner's research claim:** demonstrate scientific decision-making, not assert candidate intelligence or paid customer outcomes.  
**Pilot:** [CI #24](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42399345922), 36 genuine local model inferences, 32 labeled, post-hoc 22/32 hybrid pairs.  
**Methods:** [Exact paired statistics](evaluation/study_statistics.py), [paired replay](evaluation/compare_routing.py), [economic sensitivity](evaluation/economics.py).  
**Protocol lock:** No independent evaluation dataset or external reviewer is currently locked. This document is a *proposal* and must be frozen, with a Git commit/hash, **before collecting any confirmatory outcomes**. The 36-case pilot is permanently DEVELOPMENT/EXPLORATORY and cannot be relabeled as holdout.

## Research questions

**H1 (primary, statistical):** On a genuinely independent, prospectively labeled B2B-intake sample, the prespecified hybrid (validated LLM category + deterministic rule urgency) has a different probability of getting *both category and urgency right* than the rules-only baseline. Null: equal paired probabilities (two-sided exact McNemar; alpha 0.05). Report the sign and absolute effect size; if the test favors the baseline, H1 has failed. Do not claim superiority based solely on rejection of equality without direction.

**H2 (secondary, gated):** If H1 is supported in the beneficial direction, compare hybrid with LLM-only using a second exact paired test. The ordered testing sequence limits familywise error from reporting two post-hoc winners. Any additional method variants are exploratory and must not be described as pre-registered.

**H3 (commercial, NOT testable without actual business inputs):** Hybrid is preferable only if its client-measured **expected total handling cost per request** is lower than the best feasible alternative without breaching **client-defined missed-high/SLA, privacy, review-capacity and authorization constraints**. There is no client cost matrix or such deployment evidence now.

**Safety veto:** Success on H1 never overrides an unacceptable high-urgency miss rate, security finding, manual-review burden or failed approval gate. An accuracy p-value cannot establish economic optimality.

## Target sample and its limits

A **planning target of 480 independently sourced/labeled requests**, not 480 templated mutations:
- Controlled coverage target: 4 categories × 3 urgency labels × 2 languages (DE/EN) × 20 **distinct scenarios per cell** = 480. Collect case families/source IDs and check semantic similarity; paraphrases or cross-translations of the same underlying situation form **one cluster**, not independent observations.
- A balanced design permits class-specific diagnostics, including a planned 160 high-urgency prompts, but **does not estimate production class prevalence or real-world average profit**. Client operational data must subsequently supply prevalence weights or a separate representative evaluation.
- Of the 480, targets should be as independent as reasonably possible across industries, task types, origins and writing styles; source/case-family clustering must be documented. If independence cannot be defended, do not report a nominal McNemar p-value based on 480 IID observations. Prefer group-level estimates or a cluster-aware design with an explicit effective sample-size discussion.
- **The target 480 is conditional, not a magic significance threshold.** Illustrative paired-binary normal planning approximation: alpha=0.05 two-sided, 80% nominal power, detectable absolute paired improvement 0.08, presumed discordance probability 0.30, *hypothetical* dependence inflation 1.30 ⇒ 479 pairs, rounded to **480**. If the minimum meaningful effect were 0.05 with the same assumptions ⇒ approximately **1,225**, not 480. Inputs are *planning scenarios*, not empirically proven properties of future data. This approximation is not an independent power study or a basis to disregard clustering.
- For 480 truly IID binary outcomes, worst-case unadjusted normal-approximation 95% margin of error is about ±4.5 percentage points for one proportion; multiple comparisons, stratification and clustering can widen this. For 160 independent high-urgency examples and *zero* misses, the one-sided 95% exact upper bound on miss probability would still be ~1.85%. No zero-miss outcome is claimed or assumed.

## Case creation and truth-label governance (pre-inference)

1. Source genuinely separate scenarios through consented/anonymized client-like requests or independent realistic case-writing. Respect IP/privacy; **never put real client secrets in a public repo**. Do not copy/relabel the 36 pilot examples. Mark synthetic cases as synthetic.
2. **Two independent labelers** assign category and urgency, blind to model predictions and to one another's first labels. Record the proposed client-specific urgency definition, supporting facts, ambiguities and adjudication. If only AI labelers are available, disclose this and do **not** claim independent human ground truth. Human adjudication is not implied by a successful programmatic test.
3. Before running models, lock dataset, labels, duplicate/group inventory, code version, 4-category/3-urgency schema, thresholds and business objectives with a committed checksum and no further changes. Invalid/ambiguous/out-of-scope requests are separately tallied, **never silently dropped**.
4. Predeclare exclusions (e.g. corrupt input), missing-output handling (count as incorrect for pair accuracy, retain fail-closed workflow result), fixed model weights/prompt/settings, inference cap, cost ceiling and stopping rules. No peeking, selective reruns, or updating the test set after inspecting model errors.
5. A held-out test is *not* necessarily production representative: a new client source/prevalence review is needed for the economic decision and to estimate drift.

## Metrics and inference

- **Primary endpoint:** paired both-correct rate, hybrid vs rules on the **same requests**, with full 2×2 discordance table and **two-sided exact McNemar p**. Include paired absolute difference and a 95% uncertainty interval using a justified paired method; if clustered, use a prespecified cluster-aware method rather than IID CIs.
- Secondary: category accuracy, urgency confusion by class, high recall/miss rate, false high per 100 requests, coverage/abstention, human-review share, schema failures, and p50/p95 latency. Clearly separate route classification from explicit human authorization/apply.
- No optimization on the holdout; no scanning multiple thresholds and only reporting the winner. Once new features/tuning use the holdout, the set becomes **development**, not confirmatory.
- Numeric metrics and uncertainty do **not** validate the target's construct on their own. Labels for urgency are tied to actual SLA/customer definitions, not to a generic "urgent" keyword.

## Expected business loss: conditional decision, not proof by p-value

For each strategy `s`, client context `x`, true outcome `y`, authorized action `a` and client loss `L`:

`R(s) = E_{(x,y)~P_client}[ L(s(x), y, a) + C_inference(s,x) + C_review(s,x) + C_ops(s,x) ]`

Operational decision is subject to client veto constraints (critical miss limits, service levels, human approval, security). Compare with manual processing and the existing rules baseline. Count **avoided labor only when actually measured**; do not assume that a route marked standard_review is an automated approval.

The current 32-case retrospective **incomplete loss proxy** has these empirically observed errors:

| Strategy | Wrong category | Missed high | False high | LLM calls on labeled cases |
|---|---:|---:|---:|---:|
| LLM-only | 2 | 1 | 21 | 32 |
| Rules-only | 19 | 5 | 0 | 0 |
| Hybrid | 2 | 5 | 0 | 32 |

Assuming equal losses for every wrong category and every false/missed high:
- Hybrid versus LLM, with equal inference and category errors: hybrid incurs **4 more missed high**, avoids **21 false high**. The *proxy* break-even is **C(missed high)/C(false high) = 21/4 = 5.25**. If the ratio exceeds 5.25, model-only would have lower *urgency-only proxy* loss; below it, hybrid. This ignores review, category-specific severity, and routing actions; it is NOT a production policy recommendation.
- Hybrid versus rules has **17 fewer category errors** and equal urgency errors, but 32 additional model inferences. Ignoring all other differences, it wins the cost proxy iff **17×C(wrong category) > 32×C(inference)**. Human-review differences could reverse the conclusion.
- The all-36-original-model-output `manual_review` rate was **100%**; the frozen snapshot does not preserve the hybrid's original missing-information fields or an observed human cost. Therefore **no credible end-to-end savings or hybrid review-rate estimate can be computed from that snapshot**.

The executable [economic sensitivity tool](evaluation/economics.py) **requires input assumptions before ranking policies**. All outputs are clearly hypothetical cost proxies, not Euros, ROI, revenue or evidence of deployment. A claim of optimality requires a real client case mix, accepted cost ranges, measured time/review workload, rollout/operations costs, capacity/SLA constraints and uncertainty analysis. If no option is robust across plausible assumptions, report **no dominant strategy** instead of selecting one by aesthetics.

## Falsification and stop conditions

- Reject/reconsider hybrid if its prespecified benefit is absent on the locked dataset; do not edit the benchmark to recover significance.
- Reject/reconsider urgency rules if missed-high risk exceeds client-defined tolerances, even when aggregate accuracy increases.
- No claim of ROI if review cost or customer workload distribution cannot be measured.
- Fail closed on invalid inference, model outage, authorization denial, and conflict. Separate technical feasibility from independent verified human authorization.
- No more synthetic “n inflation” if samples are near-duplicates. No GPU upgrades, new product architectures or new repos to make a graph look impressive.

## Why this document matters for an employer/customer

The sellable work is the **decision trail**: identify a false inference from aggregate accuracy, formulate an improved architecture, predefine a falsifiable test, expose an adverse cost scenario, implement auditable controls and **refuse claims the evidence cannot support**. The applicant comparison claim (“I think better than others”) is unquantified, because no competitor cohort was sampled; the research process is a concrete work sample, not a statistical measurement of relative candidate ability.

**Provenance:** The project owner supplied the hybrid idea and the demand for research-level scrutiny; AI assistance calculated the pilot contrast, designed this provisional protocol and wrote supporting code. All authorship, independent review and customer benefit claims remain appropriately bounded.

### Methodological references

- NIST AI RMF MEASURE, especially 2.5/2.6: https://airc.nist.gov/airmf-resources/airmf/5-sec-core/
- NIST McNemar reference (paired binary outcomes): https://www.itl.nist.gov/div898/software/dataplot/refman1/auxillar/mcnemar.htm
- University of Vienna calculator (assumption-based McNemar sample planning): https://homepage.univie.ac.at/robin.ristl/samplesize.php?test=mcnemar
- DataSAIL / Nature Communications on leakage from similar samples: https://www.nature.com/articles/s41467-025-58606-8
- Canadian AI Safety Institute on evaluation uncertainty/reporting: https://ised-isde.canada.ca/site/ised/en/canadian-artificial-intelligence-safety-institute/what-information-should-ai-evaluators-share
- Research on cost-sensitive thresholds: https://link.springer.com/article/10.1007/s10618-021-00790-4
