"""Counterexamples for source provenance, safe mutation and error cleanup."""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import prepare_sandbox_input as transform
import verify_sandbox_http as live


class SourceEvidenceTests(unittest.TestCase):
    def test_captured_population_and_derived_csv(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory)
            result = transform.prepare(transform.ROOT / "evidence/hubspot-source.json",
                                       transform.ROOT / "evidence/installment-plan.json", output)
            self.assertEqual(result["source_amount_minor"], 200000)
            for name in ("hubspot-closed-won.csv", "obligations.csv", "transformation.json"):
                self.assertEqual((output / name).read_bytes(), (transform.ROOT / "evidence/derived" / name).read_bytes())

    def test_reject_incomplete_population_changed_source_and_ambiguous_currency(self):
        original = json.loads((transform.ROOT / "evidence/hubspot-source.json").read_text())
        changes = []
        source = copy.deepcopy(original)
        source["search"]["total"] = 2
        changes.append(source)
        source = copy.deepcopy(original)
        source["independent_get"]["objects"][0]["properties"]["amount"] = "1900"
        changes.append(source)
        source = copy.deepcopy(original)
        source["account"]["accountInformation"]["additionalCurrencies"] = ["EUR"]
        changes.append(source)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for source in changes:
                path = root / "source.json"
                path.write_text(json.dumps(source))
                with self.assertRaises(AssertionError):
                    transform.prepare(path, transform.ROOT / "evidence/installment-plan.json", root / "out")

    def test_reject_unbalanced_installment_plan(self):
        plan = json.loads((transform.ROOT / "evidence/installment-plan.json").read_text())
        plan["installments"][1]["amount_minor"] = 190000
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "plan.json"
            path.write_text(json.dumps(plan))
            with self.assertRaisesRegex(AssertionError, "conserve"):
                transform.prepare(transform.ROOT / "evidence/hubspot-source.json", path, root / "out")


class CleanupTests(unittest.TestCase):
    def test_failed_second_write_restores_both_with_readback(self):
        capture = json.loads((transform.ROOT / "evidence/stripe-preflight-mcp.json").read_text())
        initial = {i["id"]: {k: i[k] for k in live.FIELDS} for i in capture["invoices"]}
        state = copy.deepcopy(initial)
        writes = []
        def fake_request(path, fields=None):
            if path == "/v1/account":
                return {"id": live.ACCOUNT}
            invoice_id = path.rsplit("/", 1)[1]
            if fields is not None:
                # Simulate a write that reached Stripe but whose response failed.
                writes.append((invoice_id, dict(fields)))
                for name, value in fields.items():
                    key = name[len("metadata["):-1]
                    if value:
                        state[invoice_id]["metadata"][key] = value
                    else:
                        state[invoice_id]["metadata"].pop(key, None)
                if len(writes) == 2:
                    raise RuntimeError("Injected ambiguous second write failure")
            return copy.deepcopy(state[invoice_id])
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch.object(live, "request", side_effect=fake_request), patch.object(live.subprocess, "run") as cli:
                with self.assertRaisesRegex(RuntimeError, "Injected"):
                    live.run(root)
            cli.assert_not_called()
            self.assertEqual(state, initial)
            self.assertTrue(json.loads((root / "restoration.json").read_text())["restored"])
            self.assertEqual(len(json.loads((root / "restoration.json").read_text())["read_after_restore"]), 2)
            self.assertFalse((root / "summary.json").exists())

    def test_write_allowlist_blocks_finalization_and_nonmetadata_fields(self):
        with patch.dict("os.environ", {"STRIPE_API_KEY": "sk_test_fixture"}), patch.object(live, "urlopen") as network:
            with self.assertRaises(AssertionError):
                live.request("/v1/invoices/" + live.IDS[0] + "/finalize", {})
            with self.assertRaises(AssertionError):
                live.request("/v1/invoices/" + live.IDS[0], {"auto_advance": "true"})
            network.assert_not_called()


if __name__ == "__main__":
    unittest.main()
