"""Static recruiter proof must be understandable, reproducible and not misleading."""
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"docs"/"index.html"
CONTRACT=ROOT/"showcases"/"internal-service-intake"/"evaluation"/"research_contract.json"


class StaticRecruiterDemoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page=PAGE.read_text(encoding="utf-8")
        cls.contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.volvo=json.loads((CONTRACT.parent/"evidence"/"volvo-2013-source-audit-ci27.json").read_text(encoding="utf-8"))
        cls.nlbse=json.loads((CONTRACT.parent/"evidence"/"nlbse2023-full-test-ci29.json").read_text(encoding="utf-8"))

    def test_public_data_sources_and_legacy_pilot_are_not_confused(self):
        for keyword in ["bug", "feature", "question", "documentation",
                        "Volvo", "NLBSE", "synthetisch", "nicht auf Fallniveau",
                        "kein Ergebnis dieser öffentlichen Datensätze"]:
            self.assertIn(keyword.casefold(),self.page.casefold())
        self.assertIn("Originalarchiv",self.page)
        self.assertIn("9.454",self.page)

    def test_no_public_llm_or_client_secrets(self):
        for forbidden in ["api.openai.com", "webhook/internal-service-intake",
                          "localhost:5678", "fetch(", "XMLHttpRequest",
                          "cloudflareworkers.com"]:
            self.assertNotIn(forbidden,self.page)
        self.assertIn('connect-src \'none\'',self.page)

    def test_not_claiming_observed_savings_or_llm_benchmark(self):
        for keyword in ["KEIN REALISIERTER ROI", "kein Ergebnis",
                        "noch nicht gemessen", "kein produktives",
                        "kann null oder negativ sein"]:
            self.assertIn(keyword,self.page)

    def test_worked_cost_scenario_and_official_reference(self):
        self.assertIn("2.304,41 €",self.page)
        self.assertIn("58,50",self.page)
        self.assertAlmostEqual(9454*.05*5/60*58.5,2304.4125)

    def test_public_volvo_metric_is_proven_in_source_audit(self):
        self.assertTrue(self.volvo["source"]["verified_md5_match"])
        self.assertEqual(7554, self.volvo["observed"]["incident_cases"])
        self.assertEqual(65533, self.volvo["observed"]["events"])
        n=self.volvo["observed"]["total_observed_group_transitions"]
        self.assertEqual(9454, n)
        self.assertIn(f"{n:,}".replace(",", "."),self.page)
        self.assertAlmostEqual(n*.05*5/60*58.5,2304.4125)

    def test_no_causal_roi_inference_from_unlinked_datasets(self):
        self.assertIn("keine gemeinsame Fallbasis",self.page)
        self.assertIn("kein Ergebnis dieser öffentlichen Datensätze",self.page)
        self.assertNotIn("bewiesene Einsparungen",self.page)

    def test_nlbse_accuracy_and_duplicates_are_actually_audited(self):
        self.assertEqual(142320, self.nlbse["observed_issue_count"])
        self.assertEqual(541, self.nlbse["repeated_issue_id_rows"])
        self.assertEqual(5, self.nlbse["repeated_issue_id_label_conflicts"])
        self.assertAlmostEqual(.49251, self.nlbse["observed_keyword_baseline"]["accuracy"])
        self.assertFalse(self.nlbse["observed_keyword_baseline"]["prompt_or_model_used"])
        self.assertIn("49,25", self.page)
        self.assertIn("541", self.page)
        self.assertIn("Unser LLM wurde hier noch nicht getestet", self.page)

    def test_research_contract_has_two_different_source_populations(self):
        self.assertNotEqual(self.contract["streams"]["classification"]["id"],
                            self.contract["streams"]["operations"]["id"])
        self.assertEqual(142320,self.contract["streams"]["classification"]["published_test_count"])


if __name__=="__main__":
    unittest.main()
