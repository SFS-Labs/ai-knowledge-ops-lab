"""Boundary tests for the import contract and study acceptance checks."""
import io
import json
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest.mock import patch

from reconcile import main, read_deals, stripe_invoices, validate_invoices


class ContractTests(unittest.TestCase):
    def read_csv(self, contents):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "deals.csv"
            path.write_text(contents)
            return read_deals(path)

    def test_blank_dates_preserve_single_invoice_contract(self):
        rows = self.read_csv("deal_id,amount_minor,currency,obligation_id,issue_due,pay_due\n D ,100, USD ,,,\n")
        self.assertEqual(rows, [{"deal_id": "D", "amount_minor": 100, "currency": "usd",
                                 "obligation_id": "", "issue_due": None, "pay_due": None}])
        from evaluate import table_alerts, tabular_baseline
        from reconcile import reconcile
        self.assertEqual(list(tabular_baseline(rows, [], None)), ["missing_invoice"])
        self.assertEqual(list(table_alerts(rows, [], None)), [{"missing_invoice"}])
        self.assertEqual(next(reconcile(rows, []))["alerts"], ["missing_invoice"])

    def test_reject_ambiguous_or_corrupt_csv(self):
        cases = [
            "deal_id,currency\nD,usd\n",
            "deal_id,amount_minor,currency,currency\nD,100,usd,eur\n",
            "deal_id,amount_minor,currency\nD,100\n",
            "deal_id,amount_minor,currency\nD,100,usd,extra\n",
            "deal_id,amount_minor,currency\nD,100,usd\n D ,200,usd\n",
            "deal_id,amount_minor,currency\nD,1.2,usd\n",
            "deal_id,amount_minor,currency\nD,0,usd\n",
            "deal_id,amount_minor,currency\nD,100,\n",
            "deal_id,amount_minor,currency,issue_due,pay_due\nD,100,usd,2026-11-12,\n",
            "deal_id,amount_minor,currency,issue_due,pay_due\nD,100,usd,2026-11-12,2026-11-11\n",
        ]
        for contents in cases:
            with self.subTest(contents=contents), self.assertRaises(ValueError):
                self.read_csv(contents)

    def test_two_installments_and_iso_dates(self):
        rows = self.read_csv("deal_id,obligation_id,amount_minor,currency,issue_due,pay_due\n"
                             "D,1,100,usd,2026-11-12,2026-11-26\n"
                             "D,2,100,usd,2026-12-12,2026-12-26\n")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["issue_due"], date(2026, 11, 12))

    def test_malformed_invoices_and_repeated_page(self):
        invoice = {"id": "I", "livemode": False, "metadata": {},
                   "status": "paid", "currency": "usd", "total": 100}
        for change in ({"livemode": True}, {"total": True}, {"total": 1.5},
                       {"metadata": None}, {"status": "unknown"}, {"id": ""}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_invoices([dict(invoice, **change)])
        with patch("reconcile.urlopen", side_effect=[
            io.BytesIO(json.dumps({"data": [invoice], "has_more": True}).encode()),
            io.BytesIO(json.dumps({"data": [invoice], "has_more": False}).encode()),
        ]), self.assertRaises(ValueError):
            list(stripe_invoices("sk_test_fixture"))

    def test_invalid_schedule_fails_before_network_and_decisions(self):
        with tempfile.TemporaryDirectory() as directory:
            source = Path(directory) / "deals.csv"
            audit = Path(directory) / "audit.json"
            source.write_text("deal_id,amount_minor,currency,issue_due,pay_due\n"
                              "D,100,usd,2026-11-12,2026-11-26\n")
            with patch("sys.argv", ["reconcile.py", str(source), "--audit", str(audit)]), \
                 patch.dict("os.environ", {"STRIPE_API_KEY": "sk_test_fixture"}), \
                 patch("reconcile.urlopen") as network, patch("sys.stdout", io.StringIO()) as output, \
                 patch("sys.stderr", io.StringIO()), self.assertRaises(SystemExit):
                main()
            network.assert_not_called()
            self.assertEqual(output.getvalue(), "")
            self.assertEqual(json.loads(audit.read_text())["run_status"], "incomplete")


class StudyAcceptanceTests(unittest.TestCase):
    def test_economic_units_and_materiality(self):
        from evaluate import economic_scenarios
        rows = list(economic_scenarios([{"metrics": {"workflow": {"unique_obligation_alert_pairs": 268}}}]))
        row = next(item for item in rows if item["manual_batch_minutes_per_day"] == 5
                   and item["extra_workflow_minutes_per_alert"] == 1)
        self.assertEqual(row["net_labor_minutes"], 172)
        self.assertEqual(row["net_capacity_eur"], 94.67)
        self.assertEqual(row["break_even_extra_minutes_per_alert"], 1.53)
        self.assertEqual(row["hurdle_100_eur_extra_minutes_per_alert"], .97)
        self.assertFalse(row["meets_illustrative_100_eur_hurdle"])

    def test_manifest_files_ignore_untracked_runtime_audits(self):
        import run_study
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "source.csv").write_text("original,source\n")
            (root / "audit.json").write_text('{"run_status":"complete"}')
            (root / "extra-output.jsonl").write_text("{}\n")
            (root / "evidence-manifest.json").write_text(
                json.dumps({"sha256": {"source.csv": "expected-original-hash"}}))
            with patch.object(run_study, "ROOT", root):
                self.assertEqual(
                    [p.relative_to(root).as_posix() for p in run_study.evidence_paths()],
                    ["source.csv"],
                )

    def test_event_without_exposure_remains_undefined(self):
        from evaluate import event_metrics
        counts = event_metrics({}, {})["currency_mismatch"]
        self.assertEqual(counts["occurred_events"], 0)
        self.assertEqual(counts["detected_events"], 0)
        self.assertIsNone(counts["max_detection_delay_days"])


if __name__ == "__main__":
    unittest.main()
