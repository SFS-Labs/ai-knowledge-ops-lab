"""Decision-science gates: exact paired inference and conditional business loss.

These tests intentionally separate observed pilot evidence from pre-registered
prospective validation and never assume real customer cost data.
"""
import sys
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parents[1] / "showcases" / "internal-service-intake" / "evaluation"
sys.path.insert(0, str(HERE))
from study_statistics import exact_mcnemar_p, approximate_paired_sample_size  # noqa: E402
from economics import loss_proxy, critical_cost_ratio, evaluate_observed  # noqa: E402
from compare_routing import compare_recorded  # noqa: E402


class StudyStatisticsTests(unittest.TestCase):
    def test_exact_paired_mcnemar_on_frozen_exploratory_12_to_1(self):
        self.assertAlmostEqual(exact_mcnemar_p(12, 1), 0.00341796875, places=12)

    def test_mcnemar_balanced_or_no_discordance(self):
        self.assertEqual(1.0, exact_mcnemar_p(0, 0))
        self.assertEqual(1.0, exact_mcnemar_p(5, 5))

    def test_mcnemar_rejects_invalid_observation_counts(self):
        with self.assertRaises(ValueError):
            exact_mcnemar_p(-1, 5)

    def test_sample_planning_is_assumption_dependent_not_magic_n(self):
        proposed = approximate_paired_sample_size(
            minimum_effect=0.08, discordance_rate=0.30,
            alpha=0.05, power=0.80, design_effect=1.30)
        self.assertTrue(470 <= proposed <= 490)
        harder = approximate_paired_sample_size(
            minimum_effect=0.05, discordance_rate=0.30,
            alpha=0.05, power=0.80, design_effect=1.30)
        self.assertGreater(harder, proposed)


class EconomicSensitivityTests(unittest.TestCase):
    def test_observed_case_counts_unchanged(self):
        r = compare_recorded()
        self.assertEqual(32, r["labeled_cases"])
        self.assertEqual((10, 11, 22), (r["model_only"]["pair_correct"],
                                         r["rules_only"]["pair_correct"],
                                         r["hybrid"]["pair_correct"]))
        self.assertEqual((1, 5, 5), (r["model_only"]["missed_high"],
                                     r["rules_only"]["missed_high"],
                                     r["hybrid"]["missed_high"]))
        self.assertEqual((21, 0, 0), (r["model_only"]["false_high"],
                                     r["rules_only"]["false_high"],
                                     r["hybrid"]["false_high"]))

    def test_pilot_discordance_is_reported_as_post_hoc_not_confirmatory(self):
        report = compare_recorded()
        paired = report["hybrid_vs_rules_exploratory"]
        self.assertEqual(12, paired["hybrid_only_correct"])
        self.assertEqual(1, paired["rules_only_correct"])
        self.assertEqual(10, paired["both_correct"])
        self.assertEqual(9, paired["both_wrong"])
        self.assertAlmostEqual(0.00341796875, paired["exact_two_sided_p"])
        self.assertFalse(paired["confirmatory_validity"])

    def test_hybrid_vs_llm_critical_false_escalation_threshold(self):
        self.assertAlmostEqual(critical_cost_ratio(extra_misses=4,
                                                    avoided_false_escalations=21),
                               5.25, places=8)

    def test_sensitivity_reverses_winner_with_miss_cost(self):
        r = compare_recorded()
        cheap_miss = evaluate_observed(r, category_misroute_cost=5,
                                      missed_high_cost=3, false_high_cost=1,
                                      inference_cost=0.1)
        expensive_miss = evaluate_observed(r, category_misroute_cost=5,
                                          missed_high_cost=10, false_high_cost=1,
                                          inference_cost=0.1)
        self.assertEqual("hybrid", cheap_miss["lowest_cost_proxy_strategy"])
        self.assertEqual("model_only", expensive_miss["lowest_cost_proxy_strategy"])
        self.assertFalse(cheap_miss["proves_business_optimality"])
        self.assertFalse(expensive_miss["proves_business_optimality"])

    def test_loss_without_client_costs_is_not_claimed(self):
        counts = {"category_correct": 30, "missed_high": 5, "false_high": 0}
        with self.assertRaises(ValueError):
            loss_proxy(counts, n_labeled=32, llm_calls=32,
                       category_misroute_cost=-1, missed_high_cost=1,
                       false_high_cost=1, inference_cost=0.1)


if __name__ == "__main__":
    unittest.main()
