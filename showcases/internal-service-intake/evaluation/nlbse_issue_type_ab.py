#!/usr/bin/env python3
"""Single-variable A/B re-evaluation: JSON field 'label' vs 'issue_type'.

Same frozen 96 NLBSE-2023 cases, Qwen GGUF/llama.cpp, temperature,
generation cap, source text and four-class values. The only instructed
change is the emitted output key. No production decision follows.
The 96 cases were already evaluated in CI #40: this is an exploratory
same-case paired sensitivity test, NOT new untouched benchmark evidence.
"""
import hashlib
import json
import math
import time
from pathlib import Path

import nlbse_llm_eval as v1
import nlbse_llm_retest as v2
from nlbse_source import keyword_baseline

OUTPUT_FIELD_V1 = "label"
OUTPUT_FIELD_B = "issue_type"
ISSUE_TYPE_SYSTEM_PROMPT = v2.V2_SYSTEM_PROMPT.replace(
    "single key named label", "single key named issue_type"
)
ISSUE_TYPE_SCHEMA = {
    "type": "object",
    "properties": {"issue_type": {"type": "string", "enum": list(v1.LABELS)}},
    "required": ["issue_type"], "additionalProperties": False
}
assert ISSUE_TYPE_SYSTEM_PROMPT != v2.V2_SYSTEM_PROMPT
assert ISSUE_TYPE_SYSTEM_PROMPT.replace("single key named issue_type", "single key named label") == v2.V2_SYSTEM_PROMPT
assert len(v1.LABELS) == 4


def call_with_issue_type(row):
    title, body = row["title"][:200], row["body"][:1100]
    messages = [
        {"role":"system","content":ISSUE_TYPE_SYSTEM_PROMPT},
        {"role":"user","content":"Issue title: "+title+"\\nIssue body: "+body}
    ]
    payload = {"messages":messages,"temperature":0,"max_tokens":56,"stream":False,
               "response_format":{"type":"json_schema","json_schema":{
                   "name":"issue_type", "schema":ISSUE_TYPE_SCHEMA}}}
    req = urllib.request.Request(
        v1.SERVER_URL, data=json.dumps(payload).encode(), method="POST",
        headers={"Content-Type":"application/json"})
    t0=time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            json_response=json.load(response)
        raw=json_response["choices"][0]["message"]["content"]
        if not isinstance(raw,str) or len(raw)>1024:
            raise ValueError("model_output_not_string_or_unbounded")
        parsed=json.loads(raw)
        pred=parsed.get("issue_type") if isinstance(parsed,dict) and set(parsed)=={"issue_type"} else None
        if pred not in v1.LABELS:
            pred="__invalid__"
        return pred, (None if pred != "__invalid__" else "invalid_schema"), hashlib.sha256(raw.encode()).hexdigest(), round(1000*(time.monotonic()-t0))
    except (OSError, ValueError, KeyError, IndexError, TypeError) as err:
        return "__invalid__",type(err).__name__,None,round(1000*(time.monotonic()-t0))



def exact_mcnemar(gold, first, second):
    """Two-sided exact McNemar on discordant paired accuracy outcomes."""
    improved = sum(a != y and b == y for y, a, b in zip(gold, first, second))
    worsened = sum(a == y and b != y for y, a, b in zip(gold, first, second))
    total = improved + worsened
    if not total:
        pvalue = 1.0
    else:
        k = min(improved, worsened)
        pvalue = min(1.0, 2.0 * sum(math.comb(total, i) for i in range(k+1)) / (2**total))
    return {"improved": improved, "worsened": worsened, "discordant": total,
            "pvalue_two_sided_exact": round(pvalue, 6)}


def main():
    started = time.monotonic()
    original_csv = v1.download_test_csv()
    dev, test = v2.disjoint_samples(original_csv)
    if len(dev) != 32 or len(test) != 96:
        raise ValueError("frozen_original_sampling_drift")
    original_first_ids = {row["id"] for row in v1.select_cases(original_csv)}
    if original_first_ids.intersection(row["id"] for row in test):
        raise ValueError("leaked_first_diagnostic")
    old, new, gold, baseline, records = [], [], [], [], []
    for i, row in enumerate(test):
        if time.monotonic() - started > 1800:
            raise TimeoutError("bounded_ab_job_time_budget")
        truth = row["label"]
        baseline_label = keyword_baseline(row["title"][:200], row["body"][:1100])
        old_label, old_error, old_hash, old_ms = v2.call_with_v2_prompt(row)
        new_label, new_error, new_hash, new_ms = call_with_issue_type(row)
        gold.append(truth)
        baseline.append(baseline_label)
        old.append(old_label)
        new.append(new_label)
        records.append({
            "case_id_sha256_20": hashlib.sha256(row["id"].encode()).hexdigest()[:20],
            "truth": truth, "baseline": baseline_label,
            "old_label_key_prediction": old_label, "issue_type_key_prediction": new_label,
            "old_error": old_error, "new_error": new_error,
            "old_output_sha256": old_hash, "new_output_sha256": new_hash,
            "old_latency_ms": old_ms, "new_latency_ms": new_ms
        })
        if (i+1) % 12 == 0:
            print("SFS_QWEN_KEY_AB_PROGRESS=" + json.dumps({"completed":i+1,"total":len(test)}), flush=True)
    result = {
        "scope": "EXPLORATORY_SAME_96_REUSED_NLBSE_HOLDOUT_NOT_INDEPENDENT",
        "experimental_change": "ONLY JSON key name label -> issue_type, both system-prompt output field and JSON-Schema/parser",
        "source_archive_sha256": v1.DATASET_SHA256,
        "model": v1.MODEL_ID, "model_sha256": v1.MODEL_SHA256,
        "sample_seed": v2.SEED,
        "old_prompt_version": v2.V2_PROMPT_VERSION,
        "old_system_prompt_sha256": hashlib.sha256(v2.V2_SYSTEM_PROMPT.encode()).hexdigest(),
        "new_system_prompt_sha256": hashlib.sha256(ISSUE_TYPE_SYSTEM_PROMPT.encode()).hexdigest(),
        "unchanged": {
            "model": True, "sample": True, "title_slice":200, "body_slice":1100,
            "input_text": True, "temperature":0, "max_tokens":56,
            "four_class_values":list(v1.LABELS), "json_schema_shape":True
        },
        "n_test_cases":len(test), "calls_per_variant":len(test),
        "total_real_llm_calls":2*len(test),
        "baseline":v1.scores(gold, baseline),
        "control_label":v1.scores(gold, old),
        "treatment_issue_type":v1.scores(gold, new),
        "issue_type_minus_label_accuracy":v1.paired_bootstrap_accuracy(gold, old, new),
        "issue_type_vs_keyword_accuracy":v1.paired_bootstrap_accuracy(gold,baseline,new),
        "exact_mcnemar_key_only":exact_mcnemar(gold,old,new),
        "invalid_control":sum(p=="__invalid__" for p in old),
        "invalid_treatment":sum(p=="__invalid__" for p in new),
        "pairs":records,
        "elapsed_wall_seconds":round(time.monotonic()-started, 2),
        "limitations":[
            "Holdout reused from previously inspected CI #40; NOT fresh generalization evidence.",
            "A key rename is schema/format engineering; it is not new training or a stronger model.",
            "GGUF llama.cpp output is not the browser WebLLM model; does not fix mobile CORS.",
            "Balanced diagnostic sample of 96 not entire NLBSE competition benchmark.",
            "No customer outcome, ROI or autonomous-routing safety established."
        ]
    }
    print("SFS_QWEN_ISSUE_TYPE_AB_REPORT="+json.dumps(result,sort_keys=True,separators=(",",":")),flush=True)
    Path("/tmp/sfs-qwen-issue-type-ab.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")


if __name__ == "__main__":
    main()
