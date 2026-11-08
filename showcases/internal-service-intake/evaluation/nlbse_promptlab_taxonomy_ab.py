#!/usr/bin/env python3
"""Exploratory paired test: original user's best German questionmark prompt vs
an SFS Prompt Lab MCP taxonomy-derived Qwen system prompt.

This is NOT DSPy GEPA/MIPROv2 optimization, and the previous 96 NLBSE 2023
issues have already been inspected (not an independent holdout).
Both run on identical pinned Qwen2.5 GGUF, samples, decoding, schema, and input.
"""
import hashlib
import json
import math
import time
import urllib.request
from pathlib import Path

import nlbse_llm_eval as v1
import nlbse_llm_retest as v2
import nlbse_questionmark_ab as original
import nlbse_user_prompt_ab as german
from nlbse_source import keyword_baseline

PROMPTLAB_FILE = Path(__file__).with_name("nlbse_promptlab_taxonomy_prompt.txt")
TAXONOMY_SNAPSHOT = Path(__file__).with_name("nlbse_promptlab_taxonomy_v2_snapshot.json")
PROMPTLAB_SYSTEM_PROMPT = PROMPTLAB_FILE.read_text(encoding="utf-8").rstrip("\n")
TAXONOMY = json.loads(TAXONOMY_SNAPSHOT.read_text(encoding="utf-8"))
assert TAXONOMY["version"] == "2.0"
assert all(f"{k}: {v}" in PROMPTLAB_SYSTEM_PROMPT for k, v in TAXONOMY["classes"].items())
assert all(rule in PROMPTLAB_SYSTEM_PROMPT for rule in TAXONOMY["rules"])
assert "exactly the field \"label\"" in PROMPTLAB_SYSTEM_PROMPT
assert PROMPTLAB_SYSTEM_PROMPT != original.QUESTIONMARK_PROMPT

def call_with_promptlab_prompt(row):
    title, body = row["title"][:200], row["body"][:1100]
    messages = [
        {"role":"system","content":PROMPTLAB_SYSTEM_PROMPT},
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
    t0 = time.monotonic()
    data = v1.download_test_csv()
    dev, cases = v2.disjoint_samples(data)
    if len(dev) != 32 or len(cases) != 96:
        raise ValueError("frozen_NLBSE_96_sample_drift")
    gold, base, old, new, pairs = [], [], [], [], []
    for i, row in enumerate(cases):
        if time.monotonic() - t0 > 1800:
            raise TimeoutError("bounded_96_pair_time_budget")
        truth = row["label"]
        keyword = keyword_baseline(row["title"][:200], row["body"][:1100])
        control, errA, hashA, msA = original.call_with_questionmark_prompt(row)
        candidate, errB, hashB, msB = call_with_promptlab_prompt(row)
        gold.append(truth);base.append(keyword);old.append(control);new.append(candidate)
        pairs.append({
           "case_id_sha256_20":hashlib.sha256(row["id"].encode()).hexdigest()[:20],
           "truth":truth,"baseline":keyword,
           "german_questionmark":control,"promptlab_taxonomy":candidate,
           "control_error":errA,"candidate_error":errB,
           "control_output_sha256":hashA,"candidate_output_sha256":hashB,
           "control_latency_ms":msA,"candidate_latency_ms":msB
        })
        if (i+1)%12 == 0:
            print("SFS_PROMPTLAB_TAXONOMY_AB_PROGRESS="+json.dumps({"completed":i+1,"total":len(cases)}),flush=True)
    report = {
       "status":"REAL_QWEN_PAIRED_EXPLORATORY_AB",
       "scope":"REUSED_NLBSE_2023_96_NOT_INDEPENDENT_HOLDOUT",
       "n_cases":len(cases),"model_calls":2*len(cases),
       "model":v1.MODEL_ID,"model_sha256":v1.MODEL_SHA256,
       "dataset_sha256":v1.DATASET_SHA256,"sample_seed":v2.SEED,
       "source_mcp":"SFS Prompt Lab MCP get_taxonomy version "+TAXONOMY["version"],
       "mcp_source_is_optimized_prompt":False,
       "control_prompt_version":original.PROMPT_VERSION,
       "control_prompt_sha256":hashlib.sha256(original.QUESTIONMARK_PROMPT.encode()).hexdigest(),
       "candidate_prompt_sha256":hashlib.sha256(PROMPTLAB_SYSTEM_PROMPT.encode()).hexdigest(),
       "fixed_input":{"same_model":True,"same_sample":True,"same_issue_text":True,
                      "temperature":0,"max_tokens":56,"json_schema":v1.JSON_SCHEMA},
       "keyword":v1.scores(gold,base),
       "original_questionmark":v1.scores(gold,old),
       "mcp_taxonomy_prompt":v1.scores(gold,new),
       "paired_accuracy_delta":v1.paired_bootstrap_accuracy(gold,old,new),
       "mcnemar":german.exact_mcnemar(gold,old,new),
       "changed_predictions":sum(a!=b for a,b in zip(old,new)),
       "invalid_control":sum(x=="__invalid__" for x in old),
       "invalid_candidate":sum(x=="__invalid__" for x in new),
       "elapsed_wall_seconds":round(time.monotonic()-t0,2),
       "pairs":pairs,
       "limitations":[
        "The same 96 NLBSE 2023 issues and their labels have been reused across prompt experiments; this is exploratory, not independent generalization evidence.",
        "The candidate was hand-assembled using live MCP get_taxonomy rules and developer-domain disambiguation. It is NOT an automatically optimized GEPA/MIPROv2 output.",
        "MCP classification endpoint uses Cloudflare Llama3.3 70B, while this run tests pinned local Qwen2.5-1.5B; never compare their dev-set accuracies directly.",
        "Only Qwen GGUF CPU/llama.cpp is measured; browser WebLLM/iOS CORS not tested.",
        "No changes to production, separate B2B service-intake taxonomy or previously sealed independent holdout."
       ]
    }
    print("SFS_QWEN_PROMPTLAB_TAXONOMY_AB_REPORT="+json.dumps(report,sort_keys=True,separators=(",",":")),flush=True)
    Path("/tmp/sfs-qwen-promptlab-taxonomy-ab.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")


if __name__=="__main__":
    main()
