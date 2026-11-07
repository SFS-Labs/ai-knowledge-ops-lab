#!/usr/bin/env python3
"""Audit NLBSE'23 real, source-labeled issue-type test set, without republication.

Official competition test: 142,320 English GitHub issues with harmonized source
labels bug/feature/question/documentation. Original competing benchmark requires
FULL test set; use no subsampling for a claimed leaderboard-comparable score.
No 4x legacy service-area mapping, urgency, time or customer cost is inferred.
"""
import csv
from collections import Counter
import hashlib
from io import BytesIO, TextIOWrapper
import json
import tarfile
import urllib.request

OFFICIAL = ("https://tickettagger.blob.core.windows.net/datasets/"
            "nlbse23-issue-classification-test.csv.tar.gz")
SOURCE = "https://github.com/nlbse2023/issue-report-classification"
EXPECTED = {"bug":74781, "feature":52797, "question":8490,
            "documentation":6252}
MAX_ARCHIVE_SIZE = 120 * 1024 * 1024
MAX_EXTRACTED_SIZE = 350 * 1024 * 1024


def keyword_baseline(title, body):
    """One frozen, deliberately simple no-training English issue-type heuristic.

    Returns a label from the published NLBSE issue-type taxonomy; does not
    classify SLA urgency, old SFS service domains, or human author identity.
    """
    t = (str(title)[:450] + " " + str(body)[:1000]).lower()
    words = " " + t.replace("/", " ").replace("_", " ").replace("-", " ") + " "
    if any(k in words for k in (" documentation ", " docs ", " readme ", " wiki ", " typo ")):
        return "documentation"
    if any(k in words for k in (" exception ", " failure ", " bug ", " crash ", " broken ", " error ", " fails ", " not working ")):
        return "bug"
    if "?" in t or any(k in words for k in (" question ", " how do ", " how to ", " why does ", " help me ")):
        return "question"
    return "feature"


def classification_scores(confusion, labels, total):
    """Class-level precision/recall/F1; never infer model performance here."""
    by_class={}
    for cat in EXPECTED:
        tp=confusion.get((cat,cat),0)
        predicted=sum(v for (gold,pred),v in confusion.items() if pred==cat)
        actual=labels.get(cat,0)
        precision=(tp/predicted) if predicted else 0.
        recall=(tp/actual) if actual else 0.
        f1=(2*precision*recall/(precision+recall)) if precision+recall else 0.
        by_class[cat]={"support":actual,"predicted":predicted,
                       "precision":round(precision,5),"recall":round(recall,5),"f1":round(f1,5)}
    hits=sum(confusion.get((name,name),0) for name in EXPECTED)
    return {"accuracy":round(hits/total,5),"micro_F1":round(hits/total,5),
            "macro_F1":round(sum(by_class[x]["f1"] for x in EXPECTED)/len(EXPECTED),5),
            "class_metrics":dict(sorted(by_class.items())),
            "experiment_type":"SFS deterministic keyword baseline run on genuine NLBSE test text; NOT local LLM inference",
            "prompt_or_model_used":False}


def profile_rows(rows, *, require_published_counts=True):
    labels = Counter()
    confusion = Counter()
    n = 0
    seen_ids = {}
    duplicate_id_rows = 0
    duplicate_id_label_conflicts = 0
    empty_text = 0
    fields = None
    for row in rows:
        if fields is None:
            fields = sorted(row.keys())
        if not isinstance(row, dict):
            raise ValueError("invalid_row")
        # Source labels are normalized by NLBSE organizers, not by SFS.
        label = (row.get("labels") or row.get("label") or row.get("Label") or "").strip().lower()
        if label not in EXPECTED:
            raise ValueError("unexpected_source_label_" + label[:80])
        id_value = str(row.get("id") or row.get("Id") or row.get("issue_id") or "").strip()
        if not id_value:
            raise ValueError("missing_source_issue_id")
        if id_value in seen_ids:
            # Preserve the full official benchmark; report repeated IDs instead
            # of quietly dropping observations or falsely claiming IID samples.
            duplicate_id_rows += 1
            duplicate_id_label_conflicts += (seen_ids[id_value] != label)
        else:
            seen_ids[id_value] = label
        title = row.get("title") or row.get("Title") or ""
        body = row.get("body") or row.get("Body") or ""
        empty_text += not (str(title).strip() or str(body).strip())
        labels[label] += 1
        confusion[(label, keyword_baseline(title,body))] += 1
        n += 1
    if n == 0:
        raise ValueError("empty_issue_dataset")
    if require_published_counts and (n != sum(EXPECTED.values()) or dict(labels) != EXPECTED):
        raise ValueError("official_test_set_distribution_mismatch")
    return {
        "observed_issue_count": n,
        "observed_source_label_counts": dict(sorted(labels.items())),
        "observed_missing_title_and_body": empty_text,
        "unique_issue_ids": len(seen_ids),
        "repeated_issue_id_rows": duplicate_id_rows,
        "repeated_issue_id_label_conflicts": duplicate_id_label_conflicts,
        "independent_observation_claim": False,
        "header_fields": fields,
        "labels_are_source_harmonized": True,
        "observed_test_model_accuracy": None,
        "observed_urgency_or_volvo_linkage": None,
        "official_full_test_checked": bool(require_published_counts),
        "known_label_limit": "GitHub owner labels may be noisy and mapped from synonyms; repeated IDs mean rows are not necessarily independent, not adjudicated ground truth.",
        "observed_keyword_baseline": classification_scores(confusion, labels, n),
    }


def profile_csv_bytes(payload, *, require_published_counts=True):
    stream = TextIOWrapper(BytesIO(payload), encoding="utf-8-sig", newline="", errors="replace")
    try:
        # Public issue bodies can legitimately exceed Python CSV default (128 KiB).
        csv.field_size_limit(32 * 1024 * 1024)
        reader = csv.DictReader(stream)
        if not reader.fieldnames:
            raise ValueError("missing_csv_header")
        return profile_rows(reader, require_published_counts=require_published_counts)
    finally:
        stream.close()


def retrieve_and_profile():
    req = urllib.request.Request(OFFICIAL, headers={"User-Agent":"SFS-Research-Audit/1.0"})
    with urllib.request.urlopen(req, timeout=80) as f:
        archive = f.read(MAX_ARCHIVE_SIZE + 1)
    if len(archive) > MAX_ARCHIVE_SIZE:
        raise ValueError("nlbse_archive_exceeds_budget")
    sha = hashlib.sha256(archive).hexdigest()
    with tarfile.open(fileobj=BytesIO(archive), mode="r:gz") as tar:
        members = [m for m in tar.getmembers() if m.isfile() and m.name.lower().endswith(".csv")]
        if len(members) != 1 or members[0].size > MAX_EXTRACTED_SIZE:
            raise ValueError("unexpected_archive_members_or_size")
        csv_file = tar.extractfile(members[0])
        if csv_file is None:
            raise ValueError("missing_csv_data")
        raw = csv_file.read(MAX_EXTRACTED_SIZE + 1)
    if len(raw) > MAX_EXTRACTED_SIZE:
        raise ValueError("extracted_csv_exceeds_budget")
    report = profile_csv_bytes(raw)
    return {
        "source": {"publisher":"NLBSE 2023", "url":SOURCE,
                   "dataset_url":OFFICIAL,"sha256_downloaded_archive":sha,
                   "redistribution":"none; no raw GitHub issue text stored in this repository"},
        **report,
        "limitations":["Real software issue types, not the legacy 4 B2B service domains",
                       "No case-level linkage to Volvo or measured ticket economics",
                       "Dataset license for derived display excerpts requires independent review",
                       "No LLM-vs-rules performance experiment executed merely by source profiling"],
    }


if __name__ == "__main__":
    print("SFS_NLBSE_SOURCE_REPORT=" + json.dumps(retrieve_and_profile(),
                                               ensure_ascii=True,separators=(",",":")))
