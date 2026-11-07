#!/usr/bin/env python3
"""Structural pre-inference gate for future *genuinely independent* holdout.

It rejects obvious data recycling, incomplete class coverage and missing
label provenance. Passing this gate CANNOT prove semantic independence,
blinding, unbiased labeling, customer representativeness or validity.
"""
import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path

CATEGORIES = frozenset(("analytics", "automation", "integration", "incident-response"))
URGENCIES = frozenset(("low", "medium", "high"))
LANGUAGES = frozenset(("DE", "EN"))


def audit_holdout(rows: list[dict], *, min_per_cell: int = 20) -> dict:
    if not isinstance(min_per_cell, int) or min_per_cell < 1:
        raise ValueError("invalid_min_per_cell")
    if not isinstance(rows, list):
        raise ValueError("invalid_holdout")
    strata = Counter()
    ids, families, texts = set(), set(), set()
    disagreement_count = 0
    for i, row in enumerate(rows):
        if not isinstance(row, dict):
            raise ValueError(f"invalid_case_{i}")
        key = row.get("id")
        if not isinstance(key, str) or not key.startswith("HOLD-") or key in ids:
            raise ValueError(f"invalid_or_duplicate_id_{i}")
        ids.add(key)
        family = row.get("source_family")
        if not isinstance(family, str) or len(family.strip()) < 5 or family in families:
            raise ValueError(f"missing_or_duplicate_source_family_{i}")
        families.add(family)
        sentence = row.get("text")
        if not isinstance(sentence, str) or not 10 <= len(sentence.strip()) <= 1200:
            raise ValueError(f"invalid_text_{i}")
        normalized = " ".join(sentence.casefold().split())
        if normalized in texts:
            raise ValueError(f"duplicate_text_{i}")
        texts.add(normalized)
        lang, category, urgency = (row.get("language"), row.get("category"),
                                   row.get("urgency"))
        if lang not in LANGUAGES or category not in CATEGORIES or urgency not in URGENCIES:
            raise ValueError(f"invalid_stratum_{i}")
        if (row.get("adjudicated_category") != category
                or row.get("adjudicated_urgency") != urgency):
            raise ValueError(f"adjudicated_label_mismatch_{i}")
        labelers = row.get("labelers")
        if (not isinstance(labelers, list) or len(labelers) != 2
                or not all(isinstance(v, str) and v.strip() for v in labelers)
                or labelers[0] == labelers[1]):
            raise ValueError(f"invalid_labelers_{i}")
        for prefix in ("labeler_a", "labeler_b"):
            if (row.get(prefix + "_category") not in CATEGORIES
                    or row.get(prefix + "_urgency") not in URGENCIES):
                raise ValueError(f"missing_or_invalid_label_{prefix}_{i}")
        rationale = row.get("adjudication_reason")
        if not isinstance(rationale, str) or len(rationale.strip()) < 5:
            raise ValueError(f"missing_adjudication_reason_{i}")
        disagreement_count += (
            row["labeler_a_category"] != row["labeler_b_category"]
            or row["labeler_a_urgency"] != row["labeler_b_urgency"]
        )
        strata[(lang, category, urgency)] += 1
    expected = {(language, category, urgency)
                for language in LANGUAGES for category in CATEGORIES
                for urgency in URGENCIES}
    if set(strata) != expected or min(strata.values()) < min_per_cell:
        raise ValueError("missing_or_undersized_stratum")
    return {
        "cases": len(rows), "strata": len(strata),
        "min_per_stratum": min(strata.values()),
        "unique_source_families": len(families),
        "labeler_disagreement_cases": disagreement_count,
        "proves_independence_or_label_validity": False,
        "requires": "human source review, blind adjudication proof, and prior dataset hash lock",
    }


def inspect_locked_file(dataset: Path, expected_sha256: str) -> dict:
    payload = dataset.read_bytes()
    actual = hashlib.sha256(payload).hexdigest()
    if actual != expected_sha256.lower():
        raise ValueError("locked_sha256_mismatch")
    rows = [json.loads(line) for line in payload.decode("utf-8").splitlines()
            if line.strip()]
    return dict(audit_holdout(rows), sha256=actual,
                lock_scope="checksum matches supplied value, not proof the value predates inference")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Validate future independently adjudicated 480-case holdout before model runs")
    parser.add_argument("dataset", type=Path)
    parser.add_argument("--locked-sha256", required=True,
                        help="Checksum from a pre-inference, immutable protocol commit")
    args = parser.parse_args()
    print(json.dumps(inspect_locked_file(args.dataset, args.locked_sha256),
                     sort_keys=True, indent=2))
