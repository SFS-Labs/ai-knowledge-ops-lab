"""Hand-labeled cases independent of the simulation generator."""
import unittest
from datetime import date

from evaluate import tabular_baseline
from reconcile import reconcile


class ReconciliationReferenceTests(unittest.TestCase):
    def test_hand_labeled_batch(self):
        issue = date(2026, 11, 12)
        payment = date(2026, 11, 26)
        tomorrow = date(2026, 11, 27)
        cases = [
            ("installments", "first", issue, [("paid", "usd", 100)], "invoice_marked_paid"),
            ("installments", "second", issue, [("open", "usd", 100)], "payment_overdue"),
            ("future", "", tomorrow, [], "not_due"),
            ("missing", "", payment, [], "missing_invoice"),
            ("draft", "", issue, [("draft", "usd", 100)], "invoice_draft"),
            ("void", "", issue, [("void", "usd", 100)], "missing_invoice"),
            ("duplicate", "", issue, [("open", "usd", 100)] * 2, "multiple_invoices"),
            ("amount", "", issue, [("paid", "usd", 99)], "amount_mismatch"),
            ("currency", "", issue, [("paid", "eur", 100)], "currency_mismatch"),
            ("uncollectible", "", issue, [("uncollectible", "usd", 100)], "invoice_uncollectible"),
        ]
        rows, invoices, expected = [], [], []
        for deal, obligation, issue_due, entries, label in cases:
            rows.append({"deal_id": deal, "obligation_id": obligation, "amount_minor": 100,
                         "currency": "usd", "issue_due": issue_due,
                         "pay_due": max(issue_due, payment)})
            for index, (status, currency, amount) in enumerate(entries):
                metadata = {"hubspot_deal_id": deal}
                if obligation:
                    metadata["obligation_id"] = obligation
                invoices.append({"metadata": metadata, "id": f"{deal}-{obligation}-{index}",
                                 "status": status, "currency": currency, "total": amount})
            expected.append(label)

        results = list(reconcile(rows, invoices, payment))
        self.assertEqual([row["status"] for row in results], expected)
        self.assertEqual(results[0]["invoice_ids"], ["installments-first-0"])
        self.assertEqual(results[1]["invoice_ids"], ["installments-second-0"])
        self.assertEqual(list(tabular_baseline(rows, invoices, payment)), expected)
        from evaluate import table_alerts
        expected_alerts = [set(), {"payment_overdue"}, set(), {"missing_invoice"},
                           {"missing_invoice"}, {"missing_invoice"},
                           {"multiple_invoices", "payment_overdue"}, {"amount_mismatch"},
                           {"currency_mismatch"}, set()]
        self.assertEqual([set(row["alerts"]) for row in results], expected_alerts)
        self.assertEqual(list(table_alerts(rows, invoices, payment)), expected_alerts)


class AlertAndCompletenessTests(unittest.TestCase):
    def test_all_alerts_and_cutoffs(self):
        from evaluate import table_alerts
        row = {"deal_id": "D", "obligation_id": "1", "amount_minor": 100,
               "currency": "usd", "issue_due": 2, "pay_due": 5}
        invoice = {"id": "I", "metadata": {"hubspot_deal_id": "D", "obligation_id": "1"},
                   "status": "open", "currency": "eur", "total": 99, "livemode": False}
        cases = [
            (5, [invoice], {"currency_mismatch", "amount_mismatch", "payment_overdue"}),
            (4, [dict(invoice, currency="usd", total=100)], set()),
            (5, [dict(invoice, currency="usd", total=100)], {"payment_overdue"}),
            (1, [dict(invoice, status="draft", currency="usd", total=100)], set()),
            (2, [dict(invoice, status="draft", currency="usd", total=100)], {"missing_invoice"}),
            (2, [dict(invoice, status="void")], {"missing_invoice"}),
            (2, [dict(invoice, status="void"), dict(invoice, id="replacement",
                                                   currency="usd", total=100)], set()),
        ]
        for day, invoices, expected in cases:
            with self.subTest(day=day, expected=expected):
                self.assertEqual(set(next(reconcile([row], invoices, day))["alerts"]), expected)
                self.assertEqual(next(table_alerts([row], invoices, day)), expected)

    def test_failed_second_page_and_retry(self):
        import io
        import json
        from unittest.mock import patch
        from urllib.error import URLError
        from reconcile import stripe_invoices
        invoice = {"id": "I1", "metadata": {"hubspot_deal_id": "D"},
                   "status": "paid", "currency": "usd", "total": 100, "livemode": False}
        first = {"data": [invoice], "has_more": True}
        last = {"data": [dict(invoice, id="I2")], "has_more": False}
        row = {"deal_id": "D", "amount_minor": 100, "currency": "usd"}
        def response(page):
            return io.BytesIO(json.dumps(page).encode())
        published = []
        with patch("reconcile.urlopen", side_effect=[response(first), URLError("injected")]):
            with self.assertRaises(URLError):
                published.extend(reconcile([row], stripe_invoices("sk_test_fixture")))
        self.assertEqual(published, [])
        with patch("reconcile.urlopen", side_effect=[response(first), response(last)]):
            self.assertEqual(len(list(stripe_invoices("sk_test_fixture"))), 2)
        with patch("reconcile.urlopen", return_value=response({"data": [], "has_more": True})):
            with self.assertRaises(ValueError):
                list(stripe_invoices("sk_test_fixture"))

    def test_recurrent_event_and_false_alarm_metrics(self):
        from evaluate import event_metrics
        key = ("D", "currency_mismatch")
        result = event_metrics({key: [1, 2, 5, 6, 99]}, {key: [2, 3, 5, 6]})["currency_mismatch"]
        self.assertEqual(result["occurred_events"], 3)
        self.assertEqual(result["detected_events"], 2)
        self.assertEqual(result["missed_events"], 1)
        self.assertEqual(result["false_alert_episodes"], 1)
        self.assertEqual(result["max_detection_delay_days"], 1)
        self.assertEqual(result["open_at_horizon"], 1)


    def test_cli_incomplete_audit_and_successful_retry(self):
        import io
        import json
        import tempfile
        from pathlib import Path
        from unittest.mock import patch
        from urllib.error import URLError
        from reconcile import main
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "deals.csv"
            audit = root / "audit.json"
            source.write_text("deal_id,amount_minor,currency\nD,100,usd\n")
            argv = ["reconcile.py", str(source), "--audit", str(audit)]
            def broken(_):
                yield {"id": "I", "metadata": {"hubspot_deal_id": "D"}, "status": "paid",
                       "currency": "usd", "total": 100}
                raise URLError("injected page failure")
            output = io.StringIO()
            with patch("sys.argv", argv), patch.dict("os.environ", {"STRIPE_API_KEY": "sk_test_fixture"}):
                with patch("reconcile.stripe_invoices", broken), patch("sys.stdout", output):
                    with self.assertRaises(SystemExit):
                        main()
                self.assertEqual(output.getvalue(), "")
                failed = json.loads(audit.read_text())
                self.assertEqual(failed["run_status"], "incomplete")
                self.assertFalse(failed["decisions_published"])
                with patch("reconcile.stripe_invoices", return_value=[]), patch("sys.stdout", output):
                    main()
                self.assertEqual(json.loads(audit.read_text())["run_status"], "complete")

    def test_sandbox_capture_through_paginated_http_adapter(self):
        import io
        import json
        from pathlib import Path
        from unittest.mock import patch
        from reconcile import stripe_invoices
        capture = json.loads((Path(__file__).parent / "fixtures/sandbox-review.json").read_text())
        self.assertFalse(capture["final_has_more"])
        pages = [{"data": [entry], "has_more": index == 0}
                 for index, entry in enumerate(capture["invoices"])]
        rows = [{"deal_id": capture["deal_id"], "obligation_id": str(i),
                 "amount_minor": 100000, "currency": "usd", "issue_due": 0, "pay_due": 10}
                for i in (1, 2)]
        with patch("reconcile.urlopen", side_effect=[
            io.BytesIO(json.dumps(page).encode()) for page in pages
        ]):
            results = list(reconcile(rows, stripe_invoices("sk_test_fixture"), 0))
        self.assertEqual(results[0]["alerts"], ["missing_invoice"])
        self.assertEqual(results[1]["alerts"], ["amount_mismatch", "missing_invoice"])
        self.assertTrue(all(len(row["invoice_ids"]) == 1 for row in results))


if __name__ == "__main__":
    unittest.main()
