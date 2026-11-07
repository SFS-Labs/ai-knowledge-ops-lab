# SFS Decision Engineering — business-led evidence, not demo-led storytelling

**Status: Real source audits and fixed rule benchmark VERIFIED as individual CI #29 steps; exact final release HEAD and public static hosting pending.** This document is the canonical research and recruiting explanation. Original project: Sigma Finance Systems (SFS), synthetic-local implementation + independently sourced public evidence.

## The 30-second question

A technical team receives bugs, feature requests, questions and documentation requests. **Can classification improve routing – and when would reducing handoffs actually save labor costs?**

Rather than reverse-engineering a business story around a preferred AI stack, we choose the business decision first and then assemble two legitimate, **unlinked evidence streams**:

| Question | Actual evidence | Observed result | What it cannot prove |
|---|---|---|---|
| **WHAT is the request?** | NLBSE 2023: public GitHub software issues, source-harmonized classes **bug / feature / question / documentation** | **142,320 actual original test records scanned** in [CI #29](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42412917843); 49.25% keyword Accuracy/Micro-F1 and 41.49% Macro-F1; 541 repeated issue-ID rows, five conflicting labels | No urgency, personnel costs, or current LLM model quality for these classes |
| **HOW does it move through work?** | Volvo IT BPIC 2013: original 4TU incident event log, independent MD5 verified | **7,554 cases / 65,533 events / 9,454 observed `org:group` transitions**; original source verified by [CI #27](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42411756411) | Groups changing do not prove wasted work, that AI could avoid a group change or how many minutes that would save |

**The streams are not joined**. There is no person-/case-level relationship between a public GitHub issue and a Volvo incident, and we must never label them as a single observed case population.

### An economically legible counterfactual, not fake ROI

Given **9,454 observed group changes** in Volvo and a verified **German 2025 employer cost reference of €58.50/h** for Information & Communication, a reader can vary *two hypothetical inputs*: the share of group changes that a better routing decision could prevent, and labor minutes saved per prevented change.

`potential_gross_labor_saving = 9,454 observed changes × hypothetical avoidable share × hypothetical labor minutes / 60 × €58.50/h`

For **5%** and **5 minutes**, the conditional gross scenario is **€2,304.41 across the historical dataset**. It is **NOT an observed saving**, nor a forecast for a specific business. Net benefit could be zero or negative after LLM inference, review, monitoring, deployment and missed-critical-case costs. Duration between historical events is **not** measured active working time.

The illustrated potential is better communicated to non-technical readers by a [static interactive page](../../docs/index.html) than by exposing n8n webhooks or an unprotected AI model. Source code, tests, the cited original archive and the observable assumptions remain available to the technical reviewer.

**Official rate:** [Destatis, 29 April 2026, 2025 sector Information & Communication €58.50 per hour](https://www.destatis.de/DE/Presse/Pressemitteilungen/2026/04/PD26_148_624.html), not a Volvo employee or client-specific cost.

## Method and decision gate

1. **Business-first problem definition:** What routing decision, business outcome and risk constraint would matter to an actual customer? In a paid project, start with discovery; this artifact is a sample of that reasoning.
2. **Taxonomy from task and source:** NLBSE native harmonized issue-type labels. The older Analytics/Automation/Integration/Incident Response are an exploratory *different* taxonomy; **never** present them as source labels or urgency classes.
3. **Reproducible original sources:** NLBSE [published source and benchmark instructions](https://github.com/nlbse2023/issue-report-classification); Volvo [4TU DOI](https://doi.org/10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee); original MD5, download SHA and aggregate output where available. No original raw request text is copied into git or the public page.
4. **Measure the appropriate outcomes:** NLBSE original-test class distribution, precision/recall/F1 of a fixed transparent keyword-rule baseline, separately publish *only independently executed* LLM figures; Volvo observed process transitions and elapsed time, with no labor-minute inference.
5. **Control leakage and uncertainty:** Do not tune to original benchmark test outputs or treat harmonized GitHub issue labels as independently adjudicated ground truth. The original 32 labeled synthetic hybrid cases remain an exploratory pilot, not part of NLBSE.
6. **Model economic decisions with uncertainty:** User-visible and code-executable scenarios; break-even/sensitivity, unknown review and operations costs, potential loss from urgency mistakes, zero claimed realized savings.
7. **Conclude, do not optimize forever:** A method is accepted only in a bounded, transparent business scenario. An actual customer rollout would require case mix, real labor times, SLAs, security authorization, monitored shadow-mode pilot and ideally a controlled causal comparison.

**What evidence would invalidate the recommendation?** A client with costly undetected critical incidents, a high review queue, or measured implementation costs higher than saved work should reject or revise the policy even if its overall category accuracy improves.

## Real-world versus demonstrator distinctions

| Claim | Evidentiary status |
|---|---|
| Volvo group transitions 9,454 across original historical log | **VERIFIED, exact-source MD5; CI #27 Volvo audit step** |
| NLBSE original source labels + full 142,320 test cases | **EXECUTED in CI #29**: 49.25% keyword Accuracy/Micro-F1, 41.49% Macro-F1; **541 duplicate-ID rows, 5 label conflicts**. No LLM inference on NLBSE. |
| Previous n8n / local Qwen / SQLite E2E | **VERIFIED in historical exact-head CI #25** with 100 tests |
| Original 22/32 pilot hybrid outcome | **POST-HOC synthetic pilot, not prospective customer validation** |
| AI reduced Volvo handoffs or customer expenditure | **NOT MEASURED, NOT CLAIMED** |
| The public static site is a productive AI service | **FALSE**; no live inference, credentials or endpoints |
| The project owner's argument is unique vs other applicants | **NOT QUANTIFIED**; judge documented decisions on merit |

**Data governance:** NLBSE repository license must not be mistaken for permission to republish every upstream GitHub contributor's issue body; raw issue text stays out of git/site. Attribute Volvo to Ward Steeman/Volvo IT / 4TU.ResearchData; license terms of original archive must be respected. Neither original dataset validates the other's causal or category claims.

## Reproduce the evidence with no paid API

```bash
python -m unittest discover -s tests -v
python showcases/internal-service-intake/evaluation/research_methods.py
python showcases/internal-service-intake/evaluation/volvo_process.py
python showcases/internal-service-intake/evaluation/nlbse_source.py
```

The last two commands access external public source archives; a network error is a **BLOCKED** source run, not a verified metric. The benchmark script audits the full test file and reports a rules-only comparator; it does **not** execute a new LLM on 142,320 issues. Aggregates are source-backed, model comparisons need real inference runs. The static HTML needs no API and performs only local arithmetic.

**Observed cross-source conclusion:** Both original sources have now been directly read. The NLBSE baseline is **only 49.25% on its actual full test set**; Volvo group transitions are **9,454 historical observations**. They do NOT share a test population or show any effect of our AI on Volvo operations. Missing client economics remain explicitly unmeasured.

**Audit artifacts:** [Machine-readable business/data contract](evaluation/research_contract.json) · [Cost math with disclosure controls](evaluation/research_methods.py) · [Original Volvo measured aggregates](evaluation/evidence/volvo-2013-source-audit-ci27.json) · [NLBSE observed full test evidence](evaluation/evidence/nlbse2023-full-test-ci29.json) · [NLBSE source-integrity audit](evaluation/nlbse_source.py) · [Historical decision evolution](HYBRID_DECISION_RECORD.md).

**Attribution:** The owner insisted on scientific scrutiny, discovered the field-specific hybrid-routing hypothesis and corrected the data-selection direction to business-first; AI-assisted implementation and analysis are identified as such. No claims of unaided senior engineering, client engagements, measured profits or proven cognitive superiority.
