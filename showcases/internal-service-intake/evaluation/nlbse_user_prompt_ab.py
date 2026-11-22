#!/usr/bin/env python3
"""A/B real Qwen2.5 on fixed NLBSE 2023 issues: prior v2 vs operator's VERBATIM German prompt.

The control and candidate share the exact model, user message, JSON schema, input
truncation, temp, max output tokens, and per-class sampled issues. Control is
repeated afresh for paired inference. The old 96-case holdout is REUSED, so this
is exploratory prompt sensitivity, NOT unseen generalization evidence.
The app continues to require a validated {"label": "..."} contract.
"""
import hashlib
import json
import math
import time
import urllib.request
from pathlib import Path

import nlbse_llm_eval as v1
import nlbse_llm_retest as v2
from nlbse_source import keyword_baseline

PROMPT_FILE = Path(__file__).with_name("nlbse_user_prompt_de.txt")
USER_SYSTEM_PROMPT = PROMPT_FILE.read_text(encoding="utf-8").rstrip("\n")
PROMPT_VERSION = "sfs-operator-de-verbatim-v1"
assert USER_SYSTEM_PROMPT.startswith("Du wirst ein diverses Set")
assert "JSON ist wahrscheinlich strukturierter" in USER_SYSTEM_PROMPT

def call_with_user_prompt(row):
    title, body = row["title"][:200], row["body"][:1100]
    messages = [
        {"role":"system","content":USER_SYSTEM_PROMPT},
        {"role":"user","content":"Issue title: "+title+"\\nIssue body: "+body}
    ]
    payload = {"messages":messages,"temperature":0,"max_tokens":56,"stream":False,
               "response_format":{"type":"json_schema","json_schema":{
                   "name":"issue_type", "schema":v1.JSON_SCHEMA}}}
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
        pred=parsed.get("label") if isinstance(parsed,dict) and set(parsed)=={"label"} else None
        if pred not in v1.LABELS:
            pred="__invalid__"
        return pred, (None if pred != "__invalid__" else "invalid_schema"), hashlib.sha256(raw.encode()).hexdigest(), round(1000*(time.monotonic()-t0))
    except (OSError, ValueError, KeyError, IndexError, TypeError) as err:
        return "__invalid__",type(err).__name__,None,round(1000*(time.monotonic()-t0))



def exact_mcnemar(golds, original, candidate):
    improvements = sum(a != y and b == y for y,a,b in zip(golds,original,candidate))
    regressions = sum(a == y and b != y for y,a,b in zip(golds,original,candidate))
    different_correctness = improvements + regressions
    if different_correctness == 0:
        p = 1.0
    else:
        p = min(1.0, 2*sum(math.comb(different_correctness,i) for i in range(min(improvements,regressions)+1)) / 2**different_correctness)
    return {"improvements":improvements,"regressions":regressions,
            "different_correctness":different_correctness,"exact_p_two_sided":round(p,6)}


def main():
    t0 = time.monotonic()
    data = v1.download_test_csv()
    dev,test = v2.disjoint_samples(data)
    if len(dev)!=32 or len(test)!=96:
        raise ValueError("unexpected_sample_drift")
    old_ids={r["id"] for r in v1.select_cases(data)}
    if any(r["id"] in old_ids for r in test):
        raise ValueError("first_diagnostic_sample_overlap")
    gold,base,old,new,records=[],[],[],[],[]
    for i,row in enumerate(test):
        if time.monotonic()-t0>1800:
            raise TimeoutError("bounded_prompt_ab_time_budget")
        truth=row["label"]
        baseline=keyword_baseline(row["title"][:200],row["body"][:1100])
        a,ea,ha,ta=v2.call_with_v2_prompt(row)
        b,eb,hb,tb=call_with_user_prompt(row)
        gold.append(truth)
        base.append(baseline)
        old.append(a)
        new.append(b)
        records.append({
            "case_id_sha256_20":hashlib.sha256(row["id"].encode()).hexdigest()[:20],
            "truth":truth,"baseline":baseline,
            "v2_label":a,"user_prompt_label":b,
            "v2_error":ea,"user_prompt_error":eb,
            "v2_output_sha256":ha,"user_output_sha256":hb,
            "v2_latency_ms":ta,"user_latency_ms":tb
        })
        if (i+1)%12==0:
            print("SFS_USER_PROMPT_PROGRESS="+json.dumps({"completed":i+1,"total":len(test)}),flush=True)
    report={
        "status":"REAL_LLM_AB_EXECUTED",
        "scope":"REUSED_96_ISSUE_HOLDOUT_EXPLORATORY_NOT_OFFICIAL",
        "dataset_sha256":v1.DATASET_SHA256,"model":v1.MODEL_ID,"model_sha256":v1.MODEL_SHA256,
        "test_seed":v2.SEED,"n_cases":len(test),"model_calls":2*len(test),
        "control_prompt_version":v2.V2_PROMPT_VERSION,
        "control_prompt_sha256":hashlib.sha256(v2.V2_SYSTEM_PROMPT.encode()).hexdigest(),
        "candidate_prompt_version":PROMPT_VERSION,
        "candidate_prompt_sha256":hashlib.sha256(USER_SYSTEM_PROMPT.encode()).hexdigest(),
        "candidate_prompt_file":str(PROMPT_FILE.relative_to(Path(__file__).parents[3])),
        "fixed_generation":{"temperature":0,"max_tokens":56,"json_schema":v1.JSON_SCHEMA,
                            "same_model":True,"same_user_input":True,"same_cases":True},
        "baseline":v1.scores(gold,base),
        "original_v2":v1.scores(gold,old),
        "operator_de":v1.scores(gold,new),
        "operator_vs_original_accuracy_delta":v1.paired_bootstrap_accuracy(gold,old,new),
        "operator_vs_keyword_accuracy_delta":v1.paired_bootstrap_accuracy(gold,base,new),
        "mcnemar":exact_mcnemar(gold,old,new),
        "changed_predictions":sum(a!=b for a,b in zip(old,new)),
        "invalid_original":sum(x=="__invalid__" for x in old),
        "invalid_candidate":sum(x=="__invalid__" for x in new),
        "elapsed_seconds":round(time.monotonic()-t0,2),
        "pairs":records,
        "limitations":[
          "Reuse of the previously examined 96-case NLBSE 2023 test subset: not an untouched holdout.",
          "Identical llama.cpp GGUF CPU model; separate WebLLM browser quantization not evaluated.",
          "Static browser site is not the authenticated n8n production integration.",
          "No live client metrics, generalization proof, production ROI, or autonomous routing authority.",
          "No raw GitHub issue text is published."
        ]
    }
    print("SFS_QWEN_USER_PROMPT_AB_REPORT="+json.dumps(report,separators=(",",":"),sort_keys=True),flush=True)
    Path("/tmp/sfs-user-de-prompt-ab.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
