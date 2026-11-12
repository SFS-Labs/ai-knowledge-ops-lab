#!/usr/bin/env python3
"""Real Qwen prompt A/B: operator's original German vs verbatim appended heuristics.

Only the system-prompt text is changed. All 96 previously examined cases,
model GGUF checksum, user text, JSON schema, runtime and decoding options
remain fixed. This exploratory paired sensitivity test is NOT a fresh holdout.
"""
import hashlib
import inspect
import json
import math
import time
import urllib.request
from pathlib import Path

import nlbse_llm_eval as v1
import nlbse_llm_retest as v2
import nlbse_user_prompt_ab as german
from nlbse_source import keyword_baseline

QUESTIONMARK_FILE = Path(__file__).with_name("nlbse_user_prompt_de_questionmark.txt")
QUESTIONMARK_PROMPT = QUESTIONMARK_FILE.read_text(encoding="utf-8").rstrip("\n")
SUFFIX = "\n\nAlles was ein Fragezeichen am Ende des Satzes hat, wird als Question kategorisiert.\n\nEin bug report ist wahrscheinlich deutlich technischer und beschreibender an der Ursache, an der vermuteten Ursache formuliert"
assert QUESTIONMARK_PROMPT == german.USER_SYSTEM_PROMPT + SUFFIX
PROMPT_VERSION = "sfs-operator-de-questionmark-bugstyle-v2"

def call_with_questionmark_prompt(row):
    title, body = row["title"][:200], row["body"][:1100]
    messages = [
        {"role":"system","content":QUESTIONMARK_PROMPT},
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




def main():
    start=time.monotonic()
    source=v1.download_test_csv()
    dev,cases=v2.disjoint_samples(source)
    if len(dev)!=32 or len(cases)!=96:
        raise ValueError("fixed_sample_drift")
    gold,baseline,control,treatment,records=[],[],[],[],[]
    for n,row in enumerate(cases):
        if time.monotonic()-start>1800:
            raise TimeoutError("bounded_96_pair_budget_exceeded")
        truth=row["label"]
        b=keyword_baseline(row["title"][:200],row["body"][:1100])
        old,eold,hold,told=german.call_with_user_prompt(row)
        new,enew,hnew,tnew=call_with_questionmark_prompt(row)
        gold.append(truth); baseline.append(b); control.append(old); treatment.append(new)
        records.append({
          "case_sha256_20":hashlib.sha256(row["id"].encode()).hexdigest()[:20],
          "truth":truth,"keyword":b,"german_original":old,"german_questionmark":new,
          "original_error":eold,"questionmark_error":enew,
          "original_response_sha256":hold,"questionmark_response_sha256":hnew,
          "original_latency_ms":told,"questionmark_latency_ms":tnew
        })
        if (n+1)%12==0:
            print("SFS_QUESTIONMARK_AB_PROGRESS="+json.dumps({"completed":n+1,"total":len(cases)}),flush=True)
    result={
       "status":"REAL_LLM_PAIRED_AB_EXECUTED",
       "scope":"REUSED_96_ORIGINAL_NLBSE_2023_ISSUES_EXPLORATORY_NOT_INDEPENDENT",
       "n_cases":len(cases),"real_model_calls":2*len(cases),
       "model":v1.MODEL_ID,"model_sha256":v1.MODEL_SHA256,
       "source_sha256":v1.DATASET_SHA256,"sample_seed":v2.SEED,
       "original_prompt_sha256":hashlib.sha256(german.USER_SYSTEM_PROMPT.encode()).hexdigest(),
       "candidate_prompt_sha256":hashlib.sha256(QUESTIONMARK_PROMPT.encode()).hexdigest(),
       "only_system_prompt_suffix_changed":True,
       "fixed_settings":{"temperature":0,"max_tokens":56,"json_schema":v1.JSON_SCHEMA,"same_user_message":True,"same_96_issues":True},
       "keyword":v1.scores(gold,baseline),
       "original_german":v1.scores(gold,control),
       "questionmark_german":v1.scores(gold,treatment),
       "paired_accuracy_delta":v1.paired_bootstrap_accuracy(gold,control,treatment),
       "paired_mcnemar":german.exact_mcnemar(gold,control,treatment),
       "changed_predictions":sum(a!=b for a,b in zip(control,treatment)),
       "invalid_original":sum(x=="__invalid__" for x in control),
       "invalid_candidate":sum(x=="__invalid__" for x in treatment),
       "elapsed_wall_seconds":round(time.monotonic()-start,2),
       "paired_records":records,
       "limitations":[
          "Same issue IDs already inspected in previous experiments, not new holdout data.",
          "Rule refers to sentence-final '?' rather than issue-level intent; bug reports and feature requests can contain questions.",
          "Ground truth NLBSE labels are noisy and not audited against original text.",
          "Browser Qwen runtime is different; iPhone Safari CORS not addressed.",
          "Not the separate business service_type extraction prompt or live n8n service."
       ]
    }
    print("SFS_QUESTIONMARK_REAL_LLM_AB="+json.dumps(result,sort_keys=True,separators=(",",":")),flush=True)
    Path("/tmp/sfs-questionmark-qwen-ab.json").write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
