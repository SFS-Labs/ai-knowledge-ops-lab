# DR-002 · Research protocol: business task first, two real evidence streams

**Status:** Source and method contract **IMPLEMENTED**; full original-data and current-HEAD verification tracked in GitHub Actions. Original 32-case pilot is permanently exploratory. **No client study, prospective intervention, deployed AI operation or measured realized saving is claimed.**

## Business-first question

For B2B IT requests, can appropriate request-type classification plus better routing reduce avoidable group handoffs **without** increasing harmful under-escalation, reviewer overload or total cost?

The actual business question chooses the taxonomy:
- **Request type (NLBSE GitHub source):** `bug`, `feature`, `question`, `documentation`. Issue types may be source-synonym-harmonized, not independently adjudicated truth.
- **Operational process (Volvo IT BPIC 2013):** incidents, event sequence, timestamp, observed group transitions and historical impact. No source-native Analytics/Automation/Integration/Incident Response class and no direct mapping to GitHub issues.
- **Urgency and service domain:** separate axes to be defined with a real client. A broken integration may simultaneously be an incident; the label dimensions should not be artificially mutually exclusive.
- **Costs:** €58.50/h published German 2025 Information & Communication employer labor cost (Destatis) is an **external reference**, not Volvo staffing pay.

See the canonical [source-provenance contract](evaluation/research_contract.json) and [business-design rationale](RESEARCH_DESIGN.md).

## Seven binding scientific criteria

1. **Original provenance and rights:** verify upstream URL, DOI, archive hash, exact commit, license, published source label semantics, source version. No raw issue text in public repo/site.
2. **Label integrity:** preserve published NLBSE `bug/feature/question/documentation` and record their original GitHub-label/synonym origin. In a future client study, urgency needs independently reviewed, SLA-grounded labels. Historical Volvo impact is not automatically a universal severity truth.
3. **No leakage or fake sample inflation:** the original NLBSE train/test split is preserved. Official benchmark comparisons require its **complete 142,320-example test set** (no test resampling). Cross-translated or cloned prompts are not independent. Volvo events are nested within cases, so counting 65,533 events as 65,533 independent incidents is invalid.
4. **Predefined comparisons:** frozen keyword-only baseline against NLBSE source labels; full per-class precision, recall and F1, macro and micro F1. New LLM classifier results can be called measured **only after genuinely executed and versioned model inference** on the identical test cases. Do not import the old 22/32 synthetic pilot into this new label space.
5. **Appropriate uncertainty:** report class imbalance, source-label noise, between-project dependence, confidence intervals and temporal/domain drift. Paired comparison and power calculations need defined independent units and meaningful detectable differences. **480 was merely a former hypothetical planning scenario, not a mandatory or automatically significant sample.**
6. **Economic validity:** distinguish original observed Volvo group changes from hypothetical avoidable share, minutes saved and conditional gross employer cost. Explicitly include false priority alarms, missed severe incidents, review, LLM inference, operations and actual capacity/SLA vetoes when such data exist. Do not multiply wall-clock case duration by hourly labor cost.
7. **Falsification and decision:** if a model fails an independent held-out classification objective or a customer-defined risk/cost constraint, discard/revise the policy. Publish both wins and failures, preserve exact-SHA evidence. No production release until authentic identity, isolation, governance and a monitored customer pilot justify it.

## Two parallel analyses, no invented joined outcome

### A. Real issue classification

Source: [NLBSE 2023 official challenge](https://github.com/nlbse2023/issue-report-classification). Reported **1,275,881 train / 142,320 test**, original harmonized source issue-type labels. [`evaluation/nlbse_source.py`](evaluation/nlbse_source.py) downloads and profiles the entire published test archive with SHA-256 output and a deterministic, transparent baseline. It publishes **aggregate scores only**, not original issue text.

**Observed SFS full-test result:** In [CI #29](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42412917843) a fixed keyword baseline scored **49.25% Accuracy/Micro-F1 and 41.49% Macro-F1** on all **142,320 original held-out records**. There were **541 repeat-ID rows**, including **5 label conflicts**; these are retained in official-size aggregate scores but reduce independent-unit credibility. The full-source SHA-256 and class-level measures are frozen in [CI #29 observation evidence](evaluation/evidence/nlbse2023-full-test-ci29.json). **No LLM was run on the NLBSE issue labels.**

The source benchmark publishes FastText and RoBERTa model performance; those are **author-reported external results**, not reruns conducted by SFS. The earlier local Qwen model was tuned for a different domain taxonomy, so a credible comparison against NLBSE requires a new fixed evaluation interface, independent trace of actual model responses, and errors reported by class.

### B. Real process operations

Source: [Volvo BPIC 2013 via 4TU.ResearchData](https://doi.org/10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee). Original gzip archive was MD5-verified in [CI #27](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42411756411); **7,554 cases, 65,533 events, 9,454 observed changes of `org:group`**. Original derived audit: [`evaluation/evidence/volvo-2013-source-audit-ci27.json`](evaluation/evidence/volvo-2013-source-audit-ci27.json). One case, not one event, is the independent unit for case outcomes. Wall-clock elapsed ≠ personnel minutes; a `group` change ≠ proven waste.

### C. Economic scenario (no causal claim)

```
conditional gross labor potential (€)
  = observed Volvo group transitions
  × assumed preventable fraction
  × assumed labor minutes saved per prevented transition / 60
  × external sector labor cost €/h
```

At 9,454 observed changes, **5% hypothetical preventability and five hypothetical minutes** imply **€2,304.41 gross across the entire historical log**. This value is a sensitivity illustration, **not measured savings**. [`research_methods.py`](evaluation/research_methods.py) enforces numerical validity and attaches explicit noncausality disclosures. [Scenario code](evaluation/research_methods.py) makes the assumptions independently adjustable. The [personal work sample](../../docs/index.html) concentrates on the decision process; no public LLM/webhook/API.

The datasets have **no per-request correspondence**: a correct NLBSE issue-class prediction cannot be used to claim a specific Volvo group handoff was avoided. Even the historical classification/handoff correlation within one dataset could not alone identify the intervention effect.

## What would be needed for a real customer proof?

Client-owned, consented and legitimately obtained **timestamped tickets**, an operationally grounded taxonomy, reviewed priority/urgency and SLA labels, true labor minutes per handling action, fully loaded labor costs, reassignment and review costs, LLM/ops expenses, and cost/severity of missed critical incidents. Randomized or staggered shadow-mode pilot comparing current process vs assisted triage is a stronger causal design than replaying historic tickets. Predeclare business endpoints and safety vetoes.

Only those matched client data and a controlled intervention could support a claim of **realized savings** or client-specific economic optimality. The public-data research is valuable as reproducible **method demonstration**, not a substitute for actual customer evidence.

## Verification commands

```sh
python -m unittest discover -s tests -v
python showcases/internal-service-intake/evaluation/research_methods.py
python showcases/internal-service-intake/evaluation/volvo_process.py
python showcases/internal-service-intake/evaluation/nlbse_source.py
```

Both source audits require network access. Exact-head CI evidence is required before merge; failed or blocked runs remain visible. The scope is intentionally bounded: no live production AI service, no unsourced claims, no additional portfolio prerequisites for applying to paid B2B-AI delivery roles.
