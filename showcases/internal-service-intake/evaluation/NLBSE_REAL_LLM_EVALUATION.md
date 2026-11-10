# Real Qwen inference on original NLBSE 2023 software issues

## Evidence and claim boundaries

- **Original data:** publicly distributed NLBSE 2023 held-out issue-type set, 142,320 labeled issue rows: bug, feature, question, documentation. Archive SHA256 `f625dc78af6139b94623004dcbe575b5dfb6dc3293b7e9fa2fa109352d1cdf0e`.
- **Data source:** https://github.com/nlbse2023/issue-report-classification
- **Label limitations:** source GitHub labels were normalized by benchmark organizers; they are not independently adjudicated ground truth. The published test CSV has no project ID column. The full original test also contains 541 repeated issue-ID rows and five conflicting labels; these are excluded entirely from the diagnostic sample.
- **Frozen model:** actual CPU inference using Qwen2.5-1.5B-Instruct GGUF Q4_K_M and pinned llama.cpp server; original model SHA256 `6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e`.
- **Original competition rules:** official submissions require the **entire** 142,320-row held-out test, with no sampling/rebalancing, and evaluate micro-F1. Our stratified diagnostic is intentionally not an official submission. The original [NLBSE competition repository](https://github.com/nlbse2023/issue-report-classification) licenses its own code under AGPL-3.0; that does **not** establish blanket republication rights to third-party GitHub issue bodies. We only publish derived decisions, hashes and aggregate statistics, never original text.
- **No customer claim:** a real public software-issue dataset is not B2B customer service-ticket data. Neither urgency, handoff savings nor economic outcomes were measured by this study.

## Original genuine 96-case diagnostic (v1, preserve unchanged)

Exactly 24 distinct issue IDs per published class, selected by a frozen ID hash/seed before inference. No duplicate ID admitted. Qwen and the simple original deterministic keyword baseline used the same truncated issue text.

| Metric | Qwen 1.5B | Simple keyword rule |
|---|---:|---:|
| Accuracy | **42.71%** (41/96) | **44.79%** (43/96) |
| Macro-F1 | **35.64%** | **42.75%** |
| Bug recall | 24/24 | 6/24 |
| Feature recall | 10/24 | 19/24 |
| Question recall | **0/24** | 11/24 |
| Documentation recall | 7/24 | 7/24 |

**Critical negative result:** The first zero-shot prompt overpredicted `bug`: of 24 genuine `question` cases, 20 were predicted `bug`, 3 `feature` and 1 `documentation`. This is a measured class-imbalance failure of the model/prompt, not a network error or a failure to run inference. All 96 requests returned parseable classifications. Absolute accuracy advantage over baseline: **-2.08 percentage points**; stratified paired bootstrap 95% interval **[-10.42, +6.25] pp**.

- Exact-head successful execution: https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42424660728
- Machine-readable, 96 per-case hashed identities, predictions, source labels, response hashes, latencies, confusion matrices, per-class precision and recall: [nlbse-qwen-real-v1-ci34.json](evidence/nlbse-qwen-real-v1-ci34.json).
- Executed prompt: `nlbse-issue-type-v1` in [nlbse_llm_eval.py](nlbse_llm_eval.py).
- Wall time including original-data retrieval and model requests (not model download/startup): **296.74 s**. This is not a user-facing server latency or a production capacity claim.

These results are a **balanced, small-sample diagnostic**, not the NLBSE leaderboard score. A balanced dataset changes prevalence relative to the original test distribution, so Accuracy here is not a population-frequency-weighted estimate. Class-conditional F1 and the confusion matrix are more informative than a lone Accuracy number. Model superiority, statistical significance, and commercial viability have **not** been established.

## Independent prompt-retuning diagnostic (v2)

The v1 failure motivates a narrow change: explicitly distinguish user questions without reported defects from actual defects. To avoid optimizing on v1's observed 96 cases:

1. Exclude the original 96 IDs and all repeated IDs.
2. Select new fixed, distinct development and test cases: 8 development and 24 test cases per class (32 + 96), via deterministic hash seed fixed in code before model execution.
3. Evaluate *both* original v1 prompt and new v2 prompt on the **development set**; select by Macro-F1, ties in favor of v1.
4. Execute **both** original and candidate prompts on the same completely fresh 96 held-out cases; compare them with the frozen baseline on those identical cases.
5. Record outcomes whether favorable or unfavorable. This is still exploratory, because issue labeling and model/prompt choices have been studied using the same larger official test source. Neither run constitutes an official leaderboard claim.

**Predetermined falsification and release interpretation (written before reading the v2 result):**
- H1: v2 should increase `question` recall **and** Macro-F1 against v1 on the new same-case holdout.
- H2: the prompt chosen from development cases should beat the frozen keyword baseline on holdout Macro-F1.
- If either hypothesis fails, report the failure prominently; do **not** change selected prompt based on holdout performance or call the model a superior autonomous classifier.
- Even if both point estimates improve, sample uncertainty, noisy owner labels and absence of production outcomes prohibit a production-readiness or ROI claim. A confidence interval overlapping zero also prohibits claiming a statistically established accuracy advantage.

The frozen implementation is [nlbse_llm_retest.py](nlbse_llm_retest.py); exact model image and downloaded GGUF are cryptographically pinned by the one-shot [CI workflow](../../../.github/workflows/ci.yml). The retest begins only when the owner moves PR #14 from Draft to Ready for Review; later pushes do **not** repeat the billable-duration inference step. Outcome must be recorded from executed CI output, not a local or hypothetical number.

## Executed v2 retest — real, disjoint original issue text

[Actions run #40, all jobs completed successfully](https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42425405686), source commit `e224c3e21128c4292b064a7f0a814a47db6f2afd`. The pinned model was downloaded and passed SHA-256 verification, and **256 genuine CPU model responses** were generated. Total measured runner-script time, excluding model download/startup, was **497.71 s**. There were no invalid or failed model responses on the 96-case test for either prompt.

**Developer selection (32 previously unseen cases):** v1 Macro-F1 **33.44%**; v2 **48.53%**. Per the precommitted selection rule, v2 was selected without looking at the new 96-case test performance.

**New 96-case holdout, identical cases and baseline for every method:**

| Metric | Rules | Original Qwen v1 | Selected Qwen v2 |
|---|---:|---:|---:|
| Accuracy | 46/96 = **47.92%** | 52/96 = **54.17%** | 54/96 = **56.25%** |
| Macro-F1 | **46.80%** | **52.28%** | **54.45%** |
| Bug recall | 8/24 | 23/24 | 22/24 |
| Feature recall | 19/24 | 14/24 | 17/24 |
| Question recall | 13/24 | 5/24 | **6/24** |
| Documentation recall | 6/24 | 10/24 | 9/24 |

The two predefined point-estimate hypotheses passed: v2 raised both `question` recall and Macro-F1 against v1 and exceeded the frozen keyword rule's Macro-F1 on the same 96 new cases. Crucially, the point estimates do **not** establish statistical dominance. v2 Accuracy − keyword Accuracy = **+8.33 pp**, paired stratified bootstrap 95% interval **[-2.08, +18.75] pp**. v2 vs v1 = **+2.08 pp**, interval **[-3.13, +7.29] pp**. Both intervals contain zero.

**Major operational limitation:** selected v2 still misses **18/24 question-labeled cases**, and thus must not make unattended routing or customer-critical decisions. Compared with the original first 96-case measurement, scores also vary strongly across two different diagnostic samples. Avoid extrapolating a population score, claiming robust cross-project generalization or hiding class failures behind aggregate Accuracy.

Machine-readable [complete v2 evidence with 96 paired labels, hashes, latency measurements and confusion matrices](evidence/nlbse-qwen-prompt-retest-ci40.json), plus the preserved [v1 first-96-case evidence](evidence/nlbse-qwen-real-v1-ci34.json). No third-party raw issue content is committed.

## Decision

The selected v2 prompt has higher observed Accuracy and Macro-F1 than this diagnostic baseline, but the sample is limited and the paired 95% accuracy interval crosses zero. **Do not claim statistically established superiority** or production-ready autonomous classification. The real system-integration evidence remains separately valid: Qwen → n8n → Python API → SQLite, with human-separated approval and negative paths proven in historical exact-commit GitHub Actions.

The website's optional browser-local Qwen demo is a **different inference runtime/quantization** and implements model classification only—not live n8n, persistence, approval or production operations. Verify actual device/browser behavior before treating it as a functioning public recruiter demo.
