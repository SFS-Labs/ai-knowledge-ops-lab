"""Exercise fail-closed behavior with the real CLI and recorded transport responses."""
import io
import json
import sys
from pathlib import Path
from tempfile import TemporaryDirectory
from urllib.error import URLError
from unittest.mock import patch
from contextlib import redirect_stderr, redirect_stdout

STUDY = Path(__file__).resolve().parent.parent / "hubspot-stripe-reconciliation"
sys.path.insert(0, str(STUDY))
import reconcile

EVIDENCE = STUDY / "evidence"
LIVE = EVIDENCE / "live-43177257680"
EXPECTED_KEYS = {("539935357174", "1"), ("539935357174", "2")}


def run_cycle(root, fault=None):
    csv_path = root / "obligations.csv"
    original = (EVIDENCE / "derived/obligations.csv").read_text()
    csv_path.write_text("\n".join(original.splitlines()[:-1]) + "\n" if fault == "crm_row_missing" else original)
    rows = reconcile.read_deals(csv_path)
    if {(row["deal_id"], row["obligation_id"]) for row in rows} != EXPECTED_KEYS:
        return {"status": "incomplete", "reason": "unexpected_crm_population", "decisions": 0, "network_calls": 0}
    invoices = json.loads((LIVE / "invoices-during.json").read_text())
    pages = [{"data": [invoices[0]], "has_more": True}, {"data": [invoices[1]], "has_more": False}]
    if fault == "stripe_page_missing":
        pages[1] = {"data": [], "has_more": True}
    responses = [io.BytesIO(json.dumps(page).encode()) for page in pages]
    if fault == "stripe_transport_error":
        responses[1] = URLError("injected temporary transport failure")
    audit_path = root / "audit.json"
    stdout = io.StringIO()
    with patch("sys.argv", ["reconcile.py", str(csv_path), "--as-of", "2026-11-12", "--audit", str(audit_path)]), \
         patch.dict("os.environ", {"STRIPE_API_KEY": "sk_test_fixture"}), \
         patch.object(reconcile, "urlopen", side_effect=responses) as network, \
         redirect_stdout(stdout), redirect_stderr(io.StringIO()):
        try:
            reconcile.main()
        except SystemExit as error:
            if error.code != 1:
                raise
    audit = json.loads(audit_path.read_text())
    observed = json.loads(stdout.getvalue()) if stdout.getvalue() else []
    if fault:
        assert audit["run_status"] == "incomplete" and not observed
    else:
        assert audit["run_status"] == "complete"
        assert observed == json.loads((LIVE / "results.json").read_text())
    return {"status": audit["run_status"], "decisions": len(observed), "network_calls": network.call_count}


def main():
    faults = {3: "crm_row_missing", 6: "stripe_page_missing", 9: "stripe_transport_error"}
    cycles = []
    for index in range(1, 11):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            fault = faults.get(index)
            first = run_cycle(root, fault)
            assert first["status"] == ("incomplete" if fault else "complete")
            retry = run_cycle(root) if fault else None
            assert not fault or (first["decisions"] == 0 and retry["status"] == "complete")
            cycles.append({"cycle": index, "fault": fault, "initial": first, "retry": retry})
    print(json.dumps({"environment": "offline adapter replay; HTTP transport mocked", "cycles": cycles}, indent=2))


if __name__ == "__main__":
    main()
