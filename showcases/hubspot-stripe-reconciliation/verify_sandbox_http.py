"""Bounded sandbox test setup/cleanup. The reconciliation CLI itself remains read-only."""
import argparse
import hashlib
import json
import os
import signal
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from prepare_sandbox_input import prepare

ROOT = Path(__file__).resolve().parent
ACCOUNT = "acct_1Uaj2tE19wsOrukR"
IDS = ("in_1UamitE19wsOrukR7goJaSyd", "in_1UamioE19wsOrukRDWKzG9Qn")
ORIGINAL_DEALS = ("539978132699", "539935357174")
ORIGINAL_CODE_HASH = "ca49feead8a1101b7ccd9198f42a297a737b5b92990fe0e25d59b0348d57c7a8"
FIELDS = ("id", "status", "livemode", "metadata", "total", "currency", "auto_advance",
          "amount_paid", "attempted", "status_transitions", "subtotal", "total_taxes")


def save(path, data):
    path.write_text(json.dumps(data, indent=2) + "\n")


def now():
    return datetime.now(timezone.utc).isoformat()


def request(path, fields=None):
    """Allow only account reads and metadata-only updates of the two approved invoices."""
    assert path == "/v1/account" or path in {"/v1/invoices/" + i for i in IDS}
    key = os.environ.get("STRIPE_API_KEY", "")
    assert key.startswith(("rk_test_", "sk_test_")), "Expected sandbox key"
    if fields is not None:
        assert path != "/v1/account"
        assert set(fields) <= {"metadata[hubspot_deal_id]", "metadata[obligation_id]"}
    data = urlencode(fields).encode() if fields is not None else None
    req = Request("https://api.stripe.com" + path, data=data,
                  headers={"Authorization": "Bearer " + key})
    try:
        with urlopen(req, timeout=20) as response:
            return json.load(response)
    except HTTPError as exc:
        raise RuntimeError(f"Stripe HTTP {exc.code}") from None
    except URLError:
        raise RuntimeError("Stripe network failure") from None


def read_invoice(invoice_id):
    obj = request("/v1/invoices/" + invoice_id)
    assert obj["id"] == invoice_id and obj["livemode"] is False
    return {k: obj[k] for k in FIELDS}


def verify_unchanged(before, after):
    assert {k: v for k, v in before.items() if k != "metadata"} == {
        k: v for k, v in after.items() if k != "metadata"}, "Non-metadata invoice fields changed"


def restore(output):
    backup_path = output / "metadata-backup.json"
    if not backup_path.exists():
        return
    backup = json.loads(backup_path.read_text())
    assert request("/v1/account")["id"] == ACCOUNT
    observations, failures = [], []
    for before in backup["invoices"]:
        try:
            current = read_invoice(before["id"])
            if current["metadata"] != before["metadata"]:
                request("/v1/invoices/" + before["id"], {
                    "metadata[hubspot_deal_id]": before["metadata"].get("hubspot_deal_id", ""),
                    "metadata[obligation_id]": before["metadata"].get("obligation_id", ""),
                })
            after = read_invoice(before["id"])
            assert after["metadata"] == before["metadata"], "Metadata restoration differs"
            verify_unchanged(before, after)
            observations.append(after)
        except Exception as exc:
            failures.append({"invoice_id": before["id"], "error_type": type(exc).__name__})
    record = {"checked_at_utc": now(), "restored": not failures,
              "read_after_restore": observations, "failures": failures}
    save(output / "restoration.json", record)
    assert not failures, "Metadata restore/read-back failed; see restoration.json"


def run(output):
    output.mkdir(parents=True, exist_ok=True)
    assert not (output / "metadata-backup.json").exists(), "Use a fresh output directory"
    source = ROOT / "evidence/hubspot-source.json"
    plan_path = ROOT / "evidence/installment-plan.json"
    prepare(source, plan_path, output)
    plan = json.loads(plan_path.read_text())
    assert hashlib.sha256((ROOT / "reconcile.py").read_bytes()).hexdigest() == ORIGINAL_CODE_HASH
    account = request("/v1/account")
    assert account["id"] == ACCOUNT, "Wrong sandbox account"
    before = [read_invoice(invoice_id) for invoice_id in IDS]
    for i, invoice in enumerate(before):
        assert invoice["status"] == "draft" and invoice["auto_advance"] is False
        assert invoice["amount_paid"] == 0 and invoice["attempted"] is False
        assert invoice["currency"] == "usd" and invoice["total"] == (100000, 190000)[i]
        assert invoice["metadata"] == {"hubspot_deal_id": ORIGINAL_DEALS[i],
                                         "sfs_fixture": "hubspot_reconciliation_20261112"}
    save(output / "metadata-backup.json", {"saved_at_utc": now(), "stripe_account": ACCOUNT, "invoices": before})
    during = []
    try:
        for invoice, installment in zip(before, plan["installments"], strict=True):
            assert invoice["id"] == installment["invoice_id"]
            request("/v1/invoices/" + invoice["id"], {
                "metadata[hubspot_deal_id]": plan["deal_id"],
                "metadata[obligation_id]": installment["obligation_id"],
            })
            updated = read_invoice(invoice["id"])
            verify_unchanged(invoice, updated)
            assert updated["metadata"] == {**invoice["metadata"], "hubspot_deal_id": plan["deal_id"],
                                            "obligation_id": installment["obligation_id"]}
            during.append(updated)
        save(output / "invoices-during.json", during)
        # Execute the original CLI as a subprocess, using its real HTTP adapter.
        # No fixture option, patched transport or MCP data substitutes this read.
        command = [sys.executable, str(ROOT / "reconcile.py"), str(output / "obligations.csv"),
                   "--as-of", plan["as_of"], "--audit", str(output / "audit.json")]
        completed = subprocess.run(command, capture_output=True, text=True, timeout=90)
        assert completed.returncode == 0, "Reconciliation CLI failed; audit retained"
        results = json.loads(completed.stdout)
        save(output / "results.json", results)
        audit = json.loads((output / "audit.json").read_text())
        assert audit["run_status"] == "complete" and audit["decisions_published"] is True
        assert audit["invoice_population"] == "pagination_completed"
        assert audit["deal_count"] == 2 and audit["invoice_count"] == 2
        assert audit["as_of"] == plan["as_of"] and audit["code_sha256"] == ORIGINAL_CODE_HASH
        assert results == [
            {"deal_id": plan["deal_id"], "obligation_id": "1", "status": "invoice_draft",
             "alerts": ["missing_invoice"], "invoice_ids": [IDS[0]]},
            {"deal_id": plan["deal_id"], "obligation_id": "2", "status": "amount_mismatch",
             "alerts": ["amount_mismatch", "missing_invoice"], "invoice_ids": [IDS[1]]},
        ], "Wrong assignment, status or complete alert set"
    finally:
        restore(output)
    summary = {"completed_at_utc": now(), "passed": True, "stripe_account": ACCOUNT,
               "livemode": False, "source_rows": 1, "obligation_rows": 2,
               "github_sha": os.environ.get("GITHUB_SHA"),
               "github_run_id": os.environ.get("GITHUB_RUN_ID"),
               "reconcile_code_sha256": ORIGINAL_CODE_HASH,
               "as_of": plan["as_of"], "metadata_restored_and_read_back": True,
               "pagination_completed": True, "atomic_snapshot_isolation": False,
               "data_path": "captured HubSpot MCP selection -> CSV transformation -> direct Stripe HTTP CLI",
               "sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                          for p in sorted(output.iterdir()) if p.is_file()}}
    save(output / "summary.json", summary)
    print("PASS: one HubSpot-derived deal; two installments; direct Stripe HTTP; exact alerts; complete audit; metadata restored/read back.")


def interrupted(_signum, _frame):
    raise RuntimeError("Verification interrupted; restoring metadata")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--restore-only", action="store_true")
    args = parser.parse_args()
    signal.signal(signal.SIGTERM, interrupted)
    if args.restore_only:
        restore(args.output)
    else:
        run(args.output)
