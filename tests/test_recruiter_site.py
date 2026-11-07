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

    def test_public_data_sources_and_legacy_pilot_are_not_confused(self):
        for keyword in ["bug", "feature", "question", "documentation",
                        "Volvo", "NLBSE", "synthetisch", "nicht auf Fallniveau",
                        "kein Ergebnis dieser öffentlichen Datensätze"]:
            self.assertIn(keyword.casefold(),self.page.casefold())
        self.assertIn("Originalarchiv",self.page)

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
        self.assertIn("195,00 €",self.page)
        self.assertIn("58,50",self.page)
        self.assertEqual(100*.20*10/60*58.5,195)

    def test_research_contract_has_two_different_source_populations(self):
        self.assertNotEqual(self.contract["streams"]["classification"]["id"],
                            self.contract["streams"]["operations"]["id"])
        self.assertEqual(142320,self.contract["streams"]["classification"]["published_test_count"])


if __name__=="__main__":
    unittest.main()
