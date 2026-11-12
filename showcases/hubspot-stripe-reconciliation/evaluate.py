"""Compare a tabular baseline and the workflow on identical 100-day snapshots."""
import json
from collections import Counter, defaultdict
from statistics import median
from time import perf_counter

from reconcile import reconcile
from simulate import DAYS, obligation_row, scenario

CRITICAL = {"missing_invoice", "amount_mismatch", "currency_mismatch",
            "multiple_invoices", "payment_overdue"}


def tabular_baseline(rows, invoices, day):
    """Executable equivalent of filter, pivot count and first-row lookup."""
    pivot = {}
    for invoice in invoices:
        if invoice["status"] == "void":
            continue
        fields = invoice["metadata"]
        key = (fields.get("hubspot_deal_id"), fields.get("obligation_id", ""))
        count, first = pivot.get(key, (0, invoice))
        pivot[key] = count + 1, first
    for row in rows:
        count, first = pivot.get((row["deal_id"], row.get("obligation_id", "")), (0, None))
        if count == 1:
            currency_ok = first["currency"] == row["currency"]
            amount_ok = first["total"] == row["amount_minor"]
            invoice_state = first["status"]
            conditions = (
                (not currency_ok, "currency_mismatch"),
                (not amount_ok, "amount_mismatch"),
                (invoice_state == "paid", "invoice_marked_paid"),
                (invoice_state == "open" and row.get("pay_due") is not None
                 and day >= row["pay_due"], "payment_overdue"),
            )
            yield next((status for condition, status in conditions if condition),
                       f"invoice_{invoice_state}")
        elif count:
            yield "multiple_invoices"
        else:
            yield "not_due" if row.get("issue_due") is not None and day < row["issue_due"] else "missing_invoice"


def table_alerts(rows, invoices, day):
    """Independent row-filter baseline exposing every failed rule."""
    active = defaultdict(list)
    for entry in invoices:
        if entry["status"] != "void":
            metadata = entry["metadata"]
            active[metadata.get("hubspot_deal_id"), metadata.get("obligation_id", "")].append(entry)
    for row in rows:
        matched = active[row["deal_id"], row.get("obligation_id", "")]
        checks = {
            "missing_invoice": (row.get("issue_due") is None or day >= row["issue_due"]) and
                all(entry["status"] == "draft" for entry in matched),
            "multiple_invoices": len(matched) > 1,
            "currency_mismatch": any(entry["currency"] != row["currency"] for entry in matched),
            "amount_mismatch": any(entry["total"] != row["amount_minor"] for entry in matched),
            "payment_overdue": row.get("pay_due") is not None and day >= row["pay_due"] and
                any(entry["status"] == "open" for entry in matched),
        }
        yield {name for name, failed in checks.items() if failed}


def reference_alerts(day, due, truth):
    outcome, paid = truth
    if day < due:
        return set()
    if outcome == "missing" or (outcome == "late" and day < due + 3):
        return {"missing_invoice"}
    alerts = set()
    if outcome == "wrong_amount":
        alerts.add("amount_mismatch")
    if outcome == "duplicate":
        alerts.add("multiple_invoices")
    if (paid is None or day < paid) and day >= due + 10:
        alerts.add("payment_overdue")
    return alerts


def reference(day, issue_day, scenario_truth):
    """Expected snapshot from the scenario manifest, without reading invoice rows."""
    outcome, paid_day = scenario_truth
    if day < issue_day:
        return "not_due"
    if outcome == "missing":
        return "missing_invoice"
    if outcome == "late" and day < issue_day + 3:
        return "missing_invoice"
    if outcome == "wrong_amount":
        return "amount_mismatch"
    if outcome == "duplicate":
        return "multiple_invoices"
    if paid_day is not None and day >= paid_day:
        return "invoice_marked_paid"
    return "payment_overdue" if day >= issue_day + 10 else "invoice_open"


def evaluate(seed, volume, issue_rate):
    deals, events, truth = scenario(seed, volume, issue_rate)
    obligations = []
    invoices = {}
    metrics = {"workflow": Counter(), "table": Counter()}
    history = {method: defaultdict(list) for method in ("reference", "workflow", "table")}
    timing = []
    for day in range(DAYS):
        obligations.extend(deals[day])
        invoices.update((invoice["id"], invoice) for _, invoice in events[day])
        rows = [obligation_row(item) for item in obligations]
        start = perf_counter()
        workflow = list(reconcile(rows, invoices.values(), day))
        timing.append(1000 * (perf_counter() - start))
        baseline = table_alerts(rows, invoices.values(), day)
        baseline_status = tabular_baseline(rows, invoices.values(), day)
        for item, actual, table, table_status in zip(obligations, workflow, baseline, baseline_status, strict=True):
            expected = reference_alerts(day, item.due_day, truth[item.key])
            expected_status = reference(day, item.due_day, truth[item.key])
            for alert in expected:
                history["reference"][item.key, alert].append(day)
            for method, observed, status in (("workflow", set(actual["alerts"]), actual["status"]),
                                             ("table", table, table_status)):
                counts = metrics[method]
                counts["obligation_day_evaluations"] += 1
                counts["exact_alert_set_matches"] += observed == expected
                counts["exact_status_matches"] += status == expected_status
                counts["missed_critical_alert_snapshots"] += len(expected - observed)
                counts["false_alert_snapshots"] += len(observed - expected)
                for alert in observed:
                    history[method][item.key, alert].append(day)
    for method, counts in metrics.items():
        counts["unique_obligation_alert_pairs"] = len(history[method])
        counts["by_alert"] = event_metrics(history["reference"], history[method])
    return {"seed": seed, "deals": volume * DAYS, "obligations": len(obligations),
            "issue_window_not_reached": sum(item.due_day >= DAYS for item in obligations),
            "payment_window_not_reached": sum(item.due_day + 10 >= DAYS for item in obligations),
            "median_local_core_ms": round(median(timing), 3),
            "metrics": metrics}


def intervals(days):
    """Contiguous positive snapshots define one observable exception episode."""
    spans = []
    for day in days:
        if spans and day == spans[-1][1] + 1:
            spans[-1][1] = day
        else:
            spans.append([day, day])
    return spans


def event_metrics(expected, observed):
    result = {}
    for alert in sorted(CRITICAL):
        counts = Counter({name: 0 for name in (
            "occurred_events", "detected_events", "missed_events", "open_at_horizon",
            "false_alert_episodes", "emitted_alert_episodes")})
        delays = []
        for key in expected.keys() | observed.keys():
            if key[1] != alert:
                continue
            truth_days = set(expected.get(key, []))
            found_days = set(observed.get(key, []))
            for start, end in intervals(sorted(truth_days)):
                counts["occurred_events"] += 1
                hits = sorted(day for day in found_days if start <= day <= end)
                counts["detected_events"] += bool(hits)
                counts["missed_events"] += not hits
                counts["open_at_horizon"] += end == DAYS - 1
                if hits:
                    delays.append(hits[0] - start)
            # A false-positive episode is a consecutive sequence of false-positive snapshots.
            counts["false_alert_episodes"] += len(intervals(sorted(found_days - truth_days)))
            counts["emitted_alert_episodes"] += len(intervals(sorted(found_days)))
        counts["max_detection_delay_days"] = max(delays) if delays else None
        result[alert] = dict(counts)
    return result


def economic_scenarios(runs):
    """Illustrative input assumptions, in minutes and EUR per 100 days."""
    alerts = median(run["metrics"]["workflow"]["unique_obligation_alert_pairs"]
                    for run in runs)
    for export_and_refresh in (2, 5, 8):
        for extra_review in (0, 1, 3):
            # Equal common exception effort cancels. Only incremental review remains.
            saved_minutes = DAYS * export_and_refresh - 60 - alerts * extra_review
            yield {"manual_batch_minutes_per_day": export_and_refresh,
                   "extra_workflow_minutes_per_alert": extra_review,
                   "net_labor_minutes": round(saved_minutes, 1),
                   "net_capacity_eur": round(saved_minutes / 60 * 40 - 20, 2),
                   "meets_illustrative_100_eur_hurdle": saved_minutes / 60 * 40 - 20 >= 100,
                   "hurdle_100_eur_extra_minutes_per_alert": (
                       round((DAYS * export_and_refresh - 60 - 120 / 40 * 60) / alerts, 2)
                       if alerts else None),
                   "break_even_extra_minutes_per_alert": (
                       round((DAYS * export_and_refresh - 60 - 20 / 40 * 60) / alerts, 2)
                       if alerts else None)}


if __name__ == "__main__":
    for name, volume, rate in (("low", 3, .05), ("default", 6, .28), ("stress", 18, .40)):
        runs = [evaluate(seed, volume, rate) for seed in range(20261112, 20261124)]
        print(json.dumps({"scenario": name, "daily_deals": volume, "injected_rate": rate,
                          "runs": runs, "economics": list(economic_scenarios(runs))}))
