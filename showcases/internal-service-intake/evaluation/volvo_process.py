#!/usr/bin/env python3
"""Audit the original Volvo IT BPI Challenge 2013 incident-event log.

Network required only to fetch. Both upstream 4TU and a public GitHub mirror
must match the MD5 independently published by 4TU before parsing. No raw data,
case identifiers, person identifiers or ticket text are committed.

IMPORTANT: impact is not a validated B2B urgency label. Completion timestamps
measure wall-clock duration, not active labor. No four service categories
exist in the source unless independent source labels prove otherwise.
"""
from collections import Counter
from datetime import datetime, timezone
from io import BytesIO
import gzip
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import urllib.request
import xml.etree.ElementTree as ET

NAME = "BPI_Challenge_2013_incidents.xes.gz"
ORIGINAL = "https://data.4tu.nl/file/0fc5c579-e544-4fab-9143-fab1f5192432/aa51ffbb-25fd-4b5a-b0b8-9aba659b7e8c"
MIRROR = ("https://raw.githubusercontent.com/DogukanDG/"
          "bpic2013-to-simod-csv/master/" + NAME)
ORIGINAL_MD5 = "d4809bd55e3e1c15b017ab4e58228297"
DOI = "https://doi.org/10.4121/uuid:500573e6-accc-4b0c-9576-aa5468b10cee"


def _stamp(value):
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
    except (ValueError, TypeError):
        return None


def _attrs(element):
    return {x.attrib.get("key"): x.attrib.get("value")
            for x in element if x.attrib.get("key")}


def _percentile(sorted_values, fraction):
    if not sorted_values:
        return None
    if fraction == 0.5:
        return round(statistics.median(sorted_values), 2)
    # Nearest rank for tails; median uses an interpolated sample median.
    index = max(0, min(len(sorted_values) - 1, (int((len(sorted_values) * fraction) + 0.999999999) - 1)))
    return round(sorted_values[index], 2)


def summarize_stream(binary):
    cases = 0
    events_total = 0
    first = None
    last = None
    spans = []
    handoffs = []
    event_counts = []
    severity = Counter()
    activities = Counter()
    event_attributes = Counter()
    trace_attributes = Counter()
    missing_timestamps = 0
    cases_no_group = 0
    cases_no_impact = 0
    event_impact_set = set()
    group_count = 0
    for action, elem in ET.iterparse(binary, events=("end",)):
        if elem.tag.rsplit("}", 1)[-1] != "trace":
            continue
        cases += 1
        events = []
        initial = {}
        for child in elem:
            tag = child.tag.rsplit("}", 1)[-1]
            if tag == "event":
                props = _attrs(child)
                events.append(props)
                event_attributes.update(props.keys())
                activities.update([props.get("concept:name", "<missing>")])
                event_impact_set.update([props["impact"]] if props.get("impact") else [])
            elif child.attrib.get("key"):
                initial[child.attrib["key"]] = child.attrib.get("value")
                trace_attributes.update([child.attrib["key"]])
        events_total += len(events)
        event_counts.append(len(events))
        parsed = [(_stamp(e.get("time:timestamp")), e)
                  for e in events]
        missing_timestamps += sum(t is None for t, _ in parsed)
        parsed = sorted(((t, e) for t, e in parsed if t is not None), key=lambda row: row[0])
        if parsed:
            c_first, c_last = parsed[0][0], parsed[-1][0]
            spans.append((c_last - c_first).total_seconds() / 3600)
            if first is None or c_first < first:
                first = c_first
            if last is None or c_last > last:
                last = c_last
        # Incident impact is an event-level variable and may change over time.
        # Use the earliest observed impact as the *historical impact*, not truth.
        impact = next((e.get("impact") for _, e in parsed if e.get("impact")), None)
        severity[impact or "<missing>"] += 1
        if not impact:
            cases_no_impact += 1
        prior = None
        count = 0
        nonempty_groups = 0
        for _, e in parsed:
            group = e.get("org:group")
            if group:
                nonempty_groups += 1
                if prior is not None and prior != group:
                    count += 1
                prior = group
        if not nonempty_groups:
            cases_no_group += 1
        group_count += count
        handoffs.append(count)
        elem.clear()
    if not cases or not events_total:
        raise ValueError("empty_source")
    spans.sort()
    handoffs_sorted = sorted(handoffs)
    return {
        "observed": {
            "incident_cases": cases, "events": events_total,
            "first_event_utc": first.isoformat() if first else None,
            "last_event_utc": last.isoformat() if last else None,
            "unique_event_impact_values": sorted(event_impact_set),
            "first_recorded_impact_counts": dict(sorted(severity.items())),
            "activity_event_counts": dict(activities.most_common(20)),
            "total_observed_group_transitions": group_count,
            "mean_group_transitions_per_case": round(statistics.mean(handoffs), 3),
            "median_group_transitions_per_case": _percentile(handoffs_sorted, .5),
            "p90_group_transitions_per_case": _percentile(handoffs_sorted, .9),
            "fraction_cases_with_at_least_one_transition": round(sum(x > 0 for x in handoffs) / cases, 4),
            "median_observed_elapsed_hours": _percentile(spans, .5),
            "p90_observed_elapsed_hours": _percentile(spans, .9),
            "max_observed_elapsed_hours": _percentile(spans, 1),
            "median_events_per_case": statistics.median(event_counts),
            "missing_event_timestamps": missing_timestamps,
            "cases_missing_group": cases_no_group,
            "cases_missing_first_impact": cases_no_impact,
            "event_attribute_names": sorted(event_attributes),
            "trace_attribute_names": sorted(trace_attributes),
        },
        "interpretation_warnings": [
            "Events capture observed historical operations, not their counterfactuals.",
            "Change of org:group is a proxy for handoff, not measured additional labor.",
            "Elapsed time between first and last event is not active work time.",
            "impact in Volvo is not validated urgency or a four-class service type.",
            "Dataset does not establish free-text service categories analytics/automation/integration/incident-response.",
            "This log cannot prove that AI would have prevented any observed handoff.",
            "This report discloses real anonymous aggregate statistics only; source terms require attribution.",
        ],
    }


def get_verified_source(urls=(ORIGINAL, MIRROR)):
    for url in urls:
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "SFSResearch/1.0 source-validation"})
            with urllib.request.urlopen(req, timeout=35) as handle:
                payload = handle.read(4_000_000)
            if hashlib.md5(payload).hexdigest() == ORIGINAL_MD5:
                return payload, url
        except Exception as exc:
            print("SFS_VOLVO_FETCH_ATTEMPT=" + json.dumps({"domain": url.split("/")[2], "status": type(exc).__name__}), file=sys.stderr)
    raise RuntimeError("verified_volvo_source_unavailable_or_checksum_mismatch")


def load_report():
    local = os.getenv("SFS_VOLVO_LOCAL_FILE")
    if local:
        raw = Path(local).read_bytes()
        source = "local_original_archive"
        if hashlib.md5(raw).hexdigest() != ORIGINAL_MD5:
            raise ValueError("original_source_MD5_mismatch")
    else:
        raw, source = get_verified_source()
    data = summarize_stream(gzip.GzipFile(fileobj=BytesIO(raw)))
    return {
        "source": {
            "name": "BPI Challenge 2013, incidents",
            "publisher": "4TU.ResearchData",
            "author": "Ward Steeman / Volvo IT",
            "year": 2013,
            "doi": DOI,
            "original_md5": ORIGINAL_MD5,
            "verified_md5_match": True,
            "downloaded_from": source,
            "redistribution": "Raw data NOT redistributed by SFS",
            "license": "4TU General Terms of Use (consult original terms before publishing extracts)",
            "data_kind": "Historical incident-event logs; not actual text of the intake request",
        },
        **data,
    }


if __name__ == "__main__":
    print("SFS_VOLVO_REPORT=" + json.dumps(load_report(), separators=(",", ":")))
