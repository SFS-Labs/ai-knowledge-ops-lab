# Real Qwen inference on original NLBSE 2023 software issues

## Evidence and claim boundaries

- **Original data:** publicly distributed NLBSE 2023 held-out issue-type set, 142,320 labeled issue rows: bug, feature, question, documentation. Archive SHA256 `f625dc78af6139b94623004dcbe575b5dfb6dc3293b7e9fa2fa109352d1cdf0e`.
- **Data source:** https://github.com/nlbse2023/issue-report-classification
- **Label limitations:** source GitHub labels were normalized by benchmark organizers; they are not independently adjudicated ground truth. The published test CSV has no project ID column. The full original test also contains 541 repeated issue-ID rows and five conflicting labels; these are excluded entirely from the diagnostic sample.
- **Frozen model:** actual CPU inference using Qwen2.5-1.5B-Instruct GGUF Q4_K_M and pinned llama.cpp server; original model SHA256 `6a1a2eb6d15622bf3c96857206351ba97e1af16c30d7a74ee38970e434e9407e`.
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

The frozen implementation is [nlbse_llm_retest.py](nlbse_llm_retest.py); exact model image and downloaded GGUF are cryptographically pinned by the one-shot [CI workflow](../../../.github/workflows/ci.yml). The retest begins only when the owner moves PR #14 from Draft to Ready for Review; later pushes do **not** repeat the billable-duration inference step. Outcome must be recorded from executed CI output, not a local or hypothetical number.

## Decision

Until independently verified, **do not claim Qwen outperforms the baseline** or that a public model interaction demonstrates validated customer production quality. The real system-integration evidence remains separately valid: Qwen → n8n → Python API → SQLite, with human-separated approval and negative paths proven in historical exact-commit GitHub Actions.

The website's optional browser-local Qwen demo is a **different inference runtime/quantization** and implements model classification only—not live n8n, persistence, approval or production operations. Verify actual device/browser behavior before treating it as a functioning public recruiter demo.
