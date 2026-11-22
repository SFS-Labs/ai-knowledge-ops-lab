"""Read-only reconciliation of synthetic HubSpot deals against a Stripe sandbox."""
import argparse
import hashlib
from datetime import datetime, timezone
from datetime import date
import csv
import json
import os
import re
from collections import defaultdict
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


def read_deals(path):
    """Normalize the shared CSV contract before fetching or publishing decisions."""
    with path.open(newline="", encoding="utf-8-sig") as source:
        reader = csv.DictReader(source)
        fields = reader.fieldnames or []
        if len(fields) != len(set(fields)) or not {"deal_id", "amount_minor", "currency"} <= set(fields):
            raise ValueError("CSV requires unique deal_id, amount_minor and currency columns")
        rows = list(reader)
    seen = set()
    for row in rows:
        if None in row or any(value is None for value in row.values()):
            raise ValueError("CSV row width does not match header")
        row["deal_id"] = row["deal_id"].strip()
        row["obligation_id"] = row.get("obligation_id", "").strip()
        row["currency"] = row["currency"].strip().lower()
        raw_amount = row["amount_minor"].strip()
        if not row["deal_id"] or not re.fullmatch(r"[0-9]+", raw_amount):
            raise ValueError("Deal ID and integer minor-unit amount are required")
        row["amount_minor"] = int(raw_amount)
        if row["amount_minor"] <= 0 or not re.fullmatch(r"[a-z]{3}", row["currency"]):
            raise ValueError("Expected positive amount and three-letter currency")
        for field in ("issue_due", "pay_due"):
            value = row.get(field, "").strip()
            row[field] = date.fromisoformat(value) if value else None
        if (row["issue_due"] is None) != (row["pay_due"] is None):
            raise ValueError("Scheduled obligations require both issue_due and pay_due")
        if row["issue_due"] is not None and row["pay_due"] < row["issue_due"]:
            raise ValueError("Payment cutoff cannot precede issue cutoff")
        key = row["deal_id"], row["obligation_id"]
        if key in seen:
            raise ValueError("Deal and obligation ID pairs must be unique")
        seen.add(key)
    return rows


def validate_invoices(invoices):
    """Reject malformed snapshots rather than classifying corrupt data as exceptions."""
    if not isinstance(invoices, list):
        raise ValueError("Expected an invoice list")
    seen = set()
    for invoice in invoices:
        if not isinstance(invoice, dict):
            raise ValueError("Expected invoice objects")
        invoice_id = invoice.get("id")
        if not isinstance(invoice_id, str) or not invoice_id or invoice_id in seen:
            raise ValueError("Invoice IDs must be nonempty and unique")
        seen.add(invoice_id)
        if invoice.get("livemode") is not False:
            raise ValueError("Expected sandbox invoices")
        if invoice.get("status") not in {"draft", "open", "paid", "uncollectible", "void"}:
            raise ValueError("Unsupported invoice state")
        if type(invoice.get("total")) is not int:
            raise ValueError("Invoice total must be integer minor units")
        if not isinstance(invoice.get("currency"), str) or not re.fullmatch(r"[a-z]{3}", invoice["currency"]):
            raise ValueError("Invalid invoice currency")
        metadata = invoice.get("metadata")
        if not isinstance(metadata, dict) or any(not isinstance(v, str) for v in metadata.values()):
            raise ValueError("Expected string-valued invoice metadata")


def stripe_invoices(key):
    params = {"limit": 100}
    seen = set()
    while True:
        url = "https://api.stripe.com/v1/invoices?" + urlencode(params)
        request = Request(url, headers={"Authorization": f"Bearer {key}"})
        with urlopen(request, timeout=20) as response:
            page = json.load(response)
        if not isinstance(page, dict) or not isinstance(page.get("data"), list) or type(page.get("has_more")) is not bool:
            raise ValueError("Invalid pagination response")
        if page["has_more"] and not page["data"]:
            raise ValueError("Incomplete pagination: empty continuation page")
        validate_invoices(page["data"])
        for invoice in page["data"]:
            if invoice["id"] in seen:
                raise ValueError("Repeated invoice in paginated response")
            seen.add(invoice["id"])
            if invoice["livemode"] is not False:
                raise ValueError("Expected sandbox invoices")
            yield invoice
        if not page["has_more"]:
            break
        params["starting_after"] = page["data"][-1]["id"]


def reconcile(deals, invoices, as_of=None):
    by_key = defaultdict(list)
    for invoice in invoices:
        metadata = invoice["metadata"]
        deal_id = metadata.get("hubspot_deal_id")
        if deal_id and invoice["status"] != "void":
            by_key[deal_id, metadata.get("obligation_id", "")].append(invoice)
    for deal in deals:
        deal_id = deal["deal_id"].strip()
        obligation_id = (deal.get("obligation_id") or "").strip()
        amount = int(deal["amount_minor"])
        if not deal_id or amount <= 0:
            raise ValueError("Each obligation needs a deal ID and a positive amount")
        matches = by_key[deal_id, obligation_id]
        issue_due = deal.get("issue_due")
        pay_due = deal.get("pay_due")
        if (issue_due is not None or pay_due is not None) and as_of is None:
            raise ValueError("An as-of date is required for scheduled obligations")
        if not matches:
            status = "not_due" if issue_due is not None and as_of < issue_due else "missing_invoice"
        elif len(matches) != 1:
            status = "multiple_invoices"
        else:
            invoice = matches[0]
            if invoice["currency"] != deal["currency"].strip().lower():
                status = "currency_mismatch"
            elif invoice["total"] != amount:
                status = "amount_mismatch"
            elif invoice["status"] == "paid":
                status = "invoice_marked_paid"
            elif invoice["status"] == "open" and pay_due is not None and as_of >= pay_due:
                status = "payment_overdue"
            else:
                status = f'invoice_{invoice["status"]}'
        alerts = set()
        due = issue_due is None or as_of >= issue_due
        finalized = [invoice for invoice in matches if invoice["status"] != "draft"]
        if due and not finalized:
            alerts.add("missing_invoice")
        if len(matches) > 1:
            alerts.add("multiple_invoices")
        for invoice in matches:
            if invoice["currency"] != deal["currency"].strip().lower():
                alerts.add("currency_mismatch")
            if invoice["total"] != amount:
                alerts.add("amount_mismatch")
            if invoice["status"] == "open" and pay_due is not None and as_of >= pay_due:
                alerts.add("payment_overdue")
        result = {"deal_id": deal_id, "status": status, "alerts": sorted(alerts),
                  "invoice_ids": [invoice["id"] for invoice in matches]}
        if obligation_id:
            result["obligation_id"] = obligation_id
        yield result

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("deals", type=Path)
    parser.add_argument("--as-of", type=date.fromisoformat)
    parser.add_argument("--invoice-fixture", type=Path, help="Read synthetic invoice JSON locally")
    parser.add_argument("--audit", type=Path, help="Write run completeness and input hashes")
    args = parser.parse_args()
    audit = {"started_at": datetime.now(timezone.utc).isoformat(),
             "run_status": "incomplete", "decisions_published": False,
             "invoice_population": "unverified", "as_of": str(args.as_of),
             "code_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             "deal_population": "caller_supplied_csv_unverified",
             "snapshot_isolation": "not_guaranteed"}
    key = os.environ.get("STRIPE_API_KEY", "")
    try:
        if args.invoice_fixture is None and not key.startswith(("rk_test_", "sk_test_")):
            raise ValueError("Set STRIPE_API_KEY to a restricted or secret sandbox key")
        deals = read_deals(args.deals)
        if args.as_of is None and any(row["issue_due"] is not None for row in deals):
            raise ValueError("An as-of date is required for scheduled obligations")
        if args.invoice_fixture is None:
            invoices = list(stripe_invoices(key))
            audit["invoice_population"] = "pagination_completed"
        else:
            invoices = json.loads(args.invoice_fixture.read_text(encoding="utf-8"))
            audit["invoice_population"] = "fixture_only"
        validate_invoices(invoices)
        audit["deal_count"] = len(deals)
        audit["invoice_count"] = len(invoices)
        for label, data in (("deals", deals), ("invoices", invoices)):
            audit[label + "_sha256"] = hashlib.sha256(
                json.dumps(data, sort_keys=True, default=str).encode()).hexdigest()
        report = list(reconcile(deals, invoices, args.as_of))
        audit.update(run_status="complete", decisions_published=True)

    except HTTPError as exc:
        audit["error"] = {"type": "HTTPError", "status": exc.code}
        parser.exit(1, f"Stripe API returned HTTP {exc.code}\n")
    except URLError:
        audit["error"] = {"type": "URLError"}
        parser.exit(1, "Could not reach the Stripe API\n")
    except (OSError, KeyError, ValueError) as exc:
        audit["error"] = {"type": type(exc).__name__}
        parser.exit(1, f"Invalid input or response: {exc}\n")
    finally:
        audit["finished_at"] = datetime.now(timezone.utc).isoformat()
        if args.audit:
            args.audit.write_text(json.dumps(audit, indent=2) + "\n")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
