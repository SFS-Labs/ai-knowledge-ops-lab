"""Replay a seeded, read-only HubSpot–Stripe billing scenario."""
import argparse
import json
import random
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, timedelta

from reconcile import reconcile

DAYS = 100
DEALS_PER_DAY = 6
OUTCOMES = ("normal", "late", "missing", "wrong_amount", "duplicate", "unpaid")
WEIGHTS = (72, 8, 6, 6, 3, 5)


@dataclass(frozen=True)
class Obligation:
    key: str
    deal_id: str
    customer_id: str
    amount: int
    due_day: int


def business_dates(start):
    dates = []
    while len(dates) < DAYS:
        if start.weekday() < 5:
            dates.append(start)
        start += timedelta(days=1)
    return dates


def scenario(seed, deals_per_day=DEALS_PER_DAY, issue_rate=0.28):
    rng = random.Random(seed)
    deals = defaultdict(list)
    events = defaultdict(list)
    expected = {}
    weights = (1 - issue_rate, *(issue_rate * weight / 28 for weight in WEIGHTS[1:]))

    for day in range(DAYS):
        for index in range(deals_per_day):
            deal_id = f"D{day + 1:03d}-{index + 1}"
            customer_id = f"C{rng.randrange(1, 61):03d}"
            installments = 2 if rng.random() < 0.35 else 1
            for installment in range(installments):
                key = f"{deal_id}/{installment + 1}"
                amount = rng.randint(5, 75) * 10000
                due = day + 2 + 10 * installment
                obligation = Obligation(key, deal_id, customer_id, amount, due)
                deals[day].append(obligation)
                outcome = rng.choices(OUTCOMES, weights)[0]
                expected[key] = (outcome, None)
                if outcome == "missing":
                    continue
                issued = due + 3 if outcome == "late" else due
                total = amount - 10000 if outcome == "wrong_amount" else amount
                for copy in range(2 if outcome == "duplicate" else 1):
                    invoice = {
                        "id": f"I-{key}-{copy + 1}",
                        "metadata": {"hubspot_deal_id": deal_id, "obligation_id": key},
                        "status": "open",
                        "currency": "usd",
                        "total": total,
                        "livemode": False,
                    }
                    events[issued].append((key, invoice))
                    if outcome in ("normal", "late"):
                        paid = issued + rng.randint(2, 7)
                        expected[key] = (outcome, paid)
                        events[paid].append((key, dict(invoice, status="paid")))
    return deals, events, expected


def obligation_row(item):
    return {"deal_id": item.deal_id, "obligation_id": item.key,
            "amount_minor": item.amount, "currency": "usd",
            "issue_due": item.due_day, "pay_due": item.due_day + 10}


def replay(seed, start, paced=False):
    new_deals, events, expected = scenario(seed)
    obligations = []
    invoices = defaultdict(dict)
    previous = {}
    customers = set()
    observed_issues = set()
    changes_total = 0
    started = time.monotonic()

    for day, as_of in enumerate(business_dates(start)):
        if paced:
            time.sleep(max(0, started + day * 300 - time.monotonic()))
        obligations.extend(new_deals[day])
        customers.update(x.customer_id for x in new_deals[day])
        for key, invoice in events[day]:
            invoices[key][invoice["id"]] = invoice

        changes = []
        totals = Counter()
        alert_totals = Counter()
        decisions = reconcile(
            [obligation_row(item) for item in obligations],
            (invoice for group in invoices.values() for invoice in group.values()),
            day,
        )
        for item, result in zip(obligations, decisions, strict=True):
            status = result["status"]
            totals[status] += 1
            alert_totals.update(result["alerts"])
            if result["alerts"]:
                observed_issues.add(item.key)
            if previous.get(item.key) != status:
                changes.append({"deal_id": item.deal_id, "obligation": item.key,
                                "from": previous.get(item.key), "to": status})
                previous[item.key] = status
        changes_total += len(changes)
        yield {"day": day + 1, "as_of": as_of.isoformat(), "new_deals": DEALS_PER_DAY,
               "invoice_events": len(events[day]), "status_counts": dict(totals), "alert_counts": dict(alert_totals),
               "changes": changes}

    yield {"summary": {"seed": seed, "business_days": DAYS, "deals": DAYS * DEALS_PER_DAY,
                       "customers": len(customers), "invoice_obligations": len(obligations),
                       "invoices_issued": sum(map(len, invoices.values())),
                       "obligations_flagged": len(observed_issues),
                       "status_changes": changes_total,
                       "scenario_outcomes": dict(Counter(outcome for outcome, _ in expected.values()))}}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=20261112)
    parser.add_argument("--start", type=date.fromisoformat, default=date(2026, 7, 1))
    parser.add_argument("--paced", action="store_true", help="Advance one business day every five minutes")
    parser.add_argument("--summary-only", action="store_true")
    args = parser.parse_args()
    for record in replay(args.seed, args.start, args.paced):
        if not args.summary_only or "summary" in record:
            print(json.dumps(record, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
