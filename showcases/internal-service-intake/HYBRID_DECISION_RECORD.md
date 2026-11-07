# Decision Record DR-001 — Hybrid B2B Intake: Sell the Decision Process, Not Just the Repository

**Status:** EXPERIMENTAL / IMPLEMENTED, pending exact-head CI verification  
**Evidence:** [Genuine CPU inference + n8n E2E, CI #24](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42399345922) at `d02a76f856acf62725eb5ec402802e6bb5febeae`  
**Replay:** `python showcases/internal-service-intake/evaluation/compare_routing.py` (no model download)  
**Observed data:** [Frozen per-case inference, 36 real model requests](evaluation/evidence/ci24-observed-model-output.json); [synthetic case labels](evaluation/cases.jsonl)  
**Scope:** Existing Draft PR #9; no new product, repository, architecture, production service, or automatic merge.

## 1. The operator's question

A working AI integration is not the commercial deliverable by itself. The scarce, transferable skill is identifying *which part of a business decision each component should own*, checking that claim against evidence, exposing counterexamples and accepting or rejecting a proposed improvement.

The project owner's central hypothesis, developed during review of CI #24: **Do not select a single winner (LLM versus rules) for every field. Route category extraction to the LLM, route urgency to deterministic rules, and make the overall decision in an explicit policy layer.**

The first proposal also suggested relying on the baseline for the combined outcome. We corrected that: a combined outcome is a *pair of component predictions*, so its accuracy must be measured on the actual paired cases rather than inferred from two marginal accuracies or taken from the rules-only system.

This record is about the decision trail, not presenting an attractive repository as evidence of independent senior engineering or customer deployment.

## 2. Initial observations — what the tests really established

On 7 November 2026, the exact-SHA CI #24 completed **68/68 Python tests**, the synthetic Docker/n8n-to-local-LLM-to-SQLite E2E, approval/reject, restart and outage gates, and **36 genuine CPU model calls**.

Of 36 authored synthetic examples, **32 have category and urgency labels** and **four are marked ambiguous**. The LLM produced **35 schema-valid outputs**. The original model policy routed **all 36 to manual review**, so no reduction in human processing cost was demonstrated.

| Outcome on 32 labeled examples | LLM alone | Keyword baseline | Retrospective hybrid |
|---|---:|---:|---:|
| Category correct | 30/32 | 13/32 | 30/32 |
| Urgency correct | 10/32 | 24/32 | 24/32 |
| **Both correct for the same example** | **10/32** | **11/32** | **22/32** |

The hybrid **22/32 (68.75%)** is calculated from the *same saved per-case real inference results*, with LLM category + baseline urgency. It is **not** a new model run, not a held-out experiment and not evidence that 68.75% will generalize to a customer's workload.

## 3. Strongest counterexample: urgency error costs are asymmetric

Overall urgency accuracy can conceal dangerous behavior. By class:

| Ground-truth urgency | LLM correct | Keyword baseline correct |
|---|---:|---:|
| Low (3) | 2/3 | 0/3 |
| Medium (20) | 0/20 | 20/20 |
| High (9) | 8/9 | 4/9 |

The keyword baseline defaults to **medium** and fails to identify **5 of 9 high-urgency** examples. A service desk might prefer false alarms to missed critical incidents, depending on SLA, staffing, incident severity and actual losses. Therefore **the 22/32 pair result is not enough to select a production urgency policy**.

A reasonable business objective is *expected loss*, not unweighted field accuracy:

`expected_loss = missed_critical * C_miss + false_escalations * C_false_alarm + manual_reviews * C_review + latency * C_delay`

All cost weights are **unknown**. We will not invent customer SLA values, savings or probabilities. On these same cases, the LLM detects 8/9 high cases but flags 21 non-high cases as high; the keyword rule detects 4/9 high cases and flags none of the non-high cases as high. Both have meaningful failure modes.

## 4. Competing approaches and decision

**A. LLM-only** — strong semantic category recognition, weak urgency calibration, no independent decision authority. Rejected as the sole classifier.

**B. Keywords-only** — inexpensive/deterministic and good at predicting the dominant medium class; poor semantic category coverage and misses several urgent cases. Rejected as a complete solution.

**C. Hybrid with explicit policy** — preferred **for a bounded experiment**, not approved for customer production:
- The **validated** LLM supplies the proposed category. Unparseable or schema-invalid output has **no accepted model category**.
- The **existing deterministic keyword baseline** supplies the urgency proposal, even if LLM output is invalid. This is *not* a safety certificate or evidence the keyword list is sufficient.
- Both urgency signals and their sources are recorded. **If they disagree, route to manual review**. A disagreement is a trigger to investigate, not a warrant to auto-escalate or to silently ignore the LLM.
- Missing information or invalid model output routes to manual review. Absent a conflict, a high rule-based urgency or an integration/incident-response category routes to `expedite_review`; other cases to `standard_review`.
- Classification/routing can never approve or apply a request. The existing approval gate remains separate, credential-based and **not a verified human identity**.

This policy may preserve more safety information while increasing manual-review workload; its operational benefit is **UNPROVEN**. No tuning to the 36 cases, extra keyword expansions or per-case exception rules are introduced here.

## 5. Change trace and reproducibility

This iteration makes exactly three independently reviewable changes **inside the existing Draft PR**:
1. Freeze actual CI #24 per-case model outputs as an immutable-by-commit observation file, with source URL and provenance warning.
2. Implement `hybrid_decision(free_text, validated_model)` in the existing `mock-api/semantic.py`, used by `semantic_register`, and persist a source-attributed `decision_trace` alongside the original model-only policy. The n8n graph, model weights and approval/apply logic do not change.
3. Add regression tests and a dependency-free replay script that recomputes *all three* strategies, including missed-high and false-high counts, from the frozen evidence.

**Verification hierarchy:**
- OBSERVED: the original exact-SHA CI #24, its genuine model outputs, E2E and unit tests.
- RECOMPUTED: the retrospective hybrid 22/32 and high-class failure modes.
- IMPLEMENTED: the hybrid decision function, audit provenance and regression tests on the new PR head.
- NOT YET VERIFIED: exact-new-HEAD Docker/n8n/LLM E2E and full repository CI.
- NOT ESTABLISHED: generalization, human-review reduction, net business ROI, customer SLA suitability, production authorization or security clearance.

## 6. Falsification criteria and next decision

Do **not** label the hybrid “better” just because it wins this post-hoc synthetic comparison. It must earn that claim on **previously unseen real or realistically sampled inquiries**, with the client specifying the actual objective function.

Candidate falsifiers:
- On held-out inputs, hybrid pair performance does not beat a reasonable rules/LLM alternative.
- Missed critical cases, manual-review burden or total expected loss exceed a client-selected limit.
- LLM category error rate causes costly downstream misrouting.
- Source conflicts cause the review queue to grow without demonstrable value.
- Authorization and audit controls are insufficient for real operations.

Until such evidence exists, the appropriate outcome is: **working technical prototype; interesting comparative advantage hypothesis; deliberately unproven commercial optimum**.

## 7. Ownership of the thinking

The **project owner** articulated the comparative-advantage hypothesis and challenged the premature conclusion that no further implementation was warranted. The assistant contributed calculations, adversarial counterexamples, alternative designs, AI-assisted implementation and verification. This record distinguishes the operator's conceptual direction from assistant-generated code and analysis; it does **not** claim that one person authored every line unaided.

**Market-entry use:** In a job interview or paid discovery call, walk through (a) the initial data, (b) the conflicting evidence, (c) the hypothesis, (d) the bounded implementation, (e) what could falsify it, and (f) which customer metrics would decide rollout. Show the exact commits and tests. Do not make publication or “finishing” this demonstration a prerequisite for applying for paid B2B-AI delivery roles.
