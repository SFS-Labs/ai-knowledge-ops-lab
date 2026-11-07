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


def profile_rows(rows, *, require_published_counts=True):
    labels = Counter()
    n = 0
    seen_ids = set()
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
            raise ValueError("duplicated_source_issue_id")
        seen_ids.add(id_value)
        title = row.get("title") or row.get("Title") or ""
        body = row.get("body") or row.get("Body") or ""
        empty_text += not (str(title).strip() or str(body).strip())
        labels[label] += 1
        n += 1
    if n == 0:
        raise ValueError("empty_issue_dataset")
    if require_published_counts and (n != sum(EXPECTED.values()) or dict(labels) != EXPECTED):
        raise ValueError("official_test_set_distribution_mismatch")
    return {
        "observed_issue_count": n,
        "observed_source_label_counts": dict(sorted(labels.items())),
        "observed_missing_title_and_body": empty_text,
        "header_fields": fields,
        "labels_are_source_harmonized": True,
        "observed_test_model_accuracy": None,
        "observed_urgency_or_volvo_linkage": None,
        "official_full_test_checked": bool(require_published_counts),
        "known_label_limit": "GitHub owner labels may be noisy and mapped from synonyms; not adjudicated independent truth.",
    }


def profile_csv_bytes(payload, *, require_published_counts=True):
    stream = TextIOWrapper(BytesIO(payload), encoding="utf-8-sig", newline="", errors="replace")
    try:
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
