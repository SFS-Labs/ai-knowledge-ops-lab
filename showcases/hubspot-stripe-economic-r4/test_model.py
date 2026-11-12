"""R4 economic extension tests; no external data, API tokens or dependencies."""
import dataclasses
import json
import subprocess
import sys
import unittest
from pathlib import Path

import model


class EconomicModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cells = model.load_cells()
        cls.parameters = model.base_parameters()

    def case(self, deals=6, incidence=28):
        return next(c for c in self.cells if c["deals_per_day"] == deals and c["incidence_pct"] == incidence)

    def test_frozen_r3_source_and_nine_cells(self):
        self.assertEqual(len(self.cells), 9)
        self.assertEqual(sum(c["evaluations_across_12_runs"] for c in self.cells), 6_631_538)
        self.assertEqual(self.case(6, 28)["evaluations_per_run_mean"], 491538 / 12)
        self.assertEqual(self.case(3, 5)["alert_pairs_median_per_run"], 22)
        self.assertEqual(self.case(18, 40)["alert_pairs_median_per_run"], 1179.5)

    def test_no_snapshot_as_invoice_or_alert_count(self):
        cell = self.case(6, 28)
        self.assertNotEqual(cell["evaluations_per_run_mean"], cell["alert_pairs_median_per_run"])
        self.assertEqual(cell["deals_per_100_days"], 600)
        self.assertEqual(cell["replicates"], 12)

    def test_common_exception_work_cancelled_symmetrically(self):
        baseline = model.calculate(self.case(), self.parameters)
        changed = model.calculate(self.case(), {**self.parameters, "common_review": 40})
        self.assertAlmostEqual(baseline["capacity_minutes"], changed["capacity_minutes"])
        self.assertGreater(changed["manual_minutes"], baseline["manual_minutes"])
        self.assertGreater(changed["automated_minutes"], baseline["automated_minutes"])

    def test_more_automation_triage_can_reverse_net_benefit(self):
        high = model.calculate(self.case(18, 40), self.parameters)
        self.assertLess(high["capacity_minutes"], 0)
        self.assertLess(high["net_economic_eur"], 0)
        self.assertIsNone(high["payback_days"])

    def test_zero_realization_never_fakes_savings(self):
        positive = model.calculate(self.case(18, 5), {**self.parameters, "utilization": 0})
        self.assertGreater(positive["capacity_minutes"], 0)
        self.assertEqual(positive["net_economic_eur"], -self.parameters["operating"])
        self.assertEqual(positive["verified_cash_savings_eur"], 0)
        self.assertIsNone(positive["payback_days"])

    def test_manual_time_and_extra_review_monotonic(self):
        cell = self.case(6, 5)
        low_time = model.calculate(cell, {**self.parameters, "m_per_eval": 0.005})
        high_time = model.calculate(cell, {**self.parameters, "m_per_eval": 0.06})
        self.assertGreater(high_time["capacity_minutes"], low_time["capacity_minutes"])
        low_review = model.calculate(cell, {**self.parameters, "extra_review": 0})
        high_review = model.calculate(cell, {**self.parameters, "extra_review": 8})
        self.assertGreater(low_review["capacity_minutes"], high_review["capacity_minutes"])

    def test_economic_break_even_recalculates_to_zero(self):
        cell = self.case(6, 28)
        initial = model.calculate(cell, self.parameters)
        threshold = initial["break_even_m_per_eval_economic"]
        recomputed = model.calculate(cell, {**self.parameters, "m_per_eval": threshold})
        self.assertAlmostEqual(recomputed["net_economic_eur"], 0, places=8)
        self.assertIsNone(recomputed["payback_days"])

    def test_equal_base_costs_two_variants_and_operating_differential(self):
        result = model.calculate(self.case(), self.parameters)
        self.assertAlmostEqual(result["capacity_minutes"], result["manual_minutes"]-result["automated_minutes"])
        self.assertAlmostEqual(result["capacity_eur"], result["capacity_minutes"] / 60 * self.parameters["wage"])
        self.assertAlmostEqual(result["net_full_use_eur"], result["capacity_eur"] - self.parameters["operating"])

    def test_reject_invalid_parameter_domains(self):
        with self.assertRaises(ValueError):
            model.calculate(self.case(), {**self.parameters, "utilization": 1.01})
        with self.assertRaises(ValueError):
            model.calculate(self.case(), {**self.parameters, "m_daily": -2})

    def test_report_is_deterministic_and_publicly_reproducible(self):
        result = model.compile_results()
        self.assertEqual(len(result["cells"]), 9)
        self.assertEqual(len(result["selected_sensitivities"]), 6)
        self.assertIn("kein gemessener", model.render_report(result).lower())
        for mode, suffix in (("--json", "RESULTS.json"), ("--report", "RESULTS.md")):
            actual = subprocess.check_output([sys.executable, str(Path(model.__file__)), mode], cwd=Path(model.__file__).parent)
            expected = (Path(model.__file__).parent / suffix).read_bytes()
            self.assertEqual(actual, expected, suffix + " does not reproduce byte-for-byte")


if __name__ == "__main__":
    unittest.main()
