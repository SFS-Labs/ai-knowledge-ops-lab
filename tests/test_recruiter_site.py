"""Recruiter page must communicate verifiable real LLM engineering first.

Two distinct validations exist: the local Qwen→n8n E2E and later, separate
NLBSE keyword benchmark. Never conflate the two or suggest no LLM was tested.
"""
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs" / "index.html"
CONTRACT = ROOT / "showcases" / "internal-service-intake" / "evaluation" / "research_contract.json"


class RecruiterEngineeringPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = PAGE.read_text(encoding="utf-8")
        cls.contract = json.loads(CONTRACT.read_text(encoding="utf-8"))
        parent = CONTRACT.parent / "evidence"
        cls.nlbse = json.loads((parent / "nlbse2023-full-test-ci29.json").read_text(encoding="utf-8"))
        cls.volvo = json.loads((parent / "volvo-2013-source-audit-ci27.json").read_text(encoding="utf-8"))

    def test_first_screen_explains_real_delivery_not_a_story(self):
        hero = self.page.split('<section class="shell hero"', 1)[1].split('</section>', 1)[0]
        for term in ("Mathias Steinbach", "AI-Service-Intake", "Qwen", "n8n",
                     "Python-API", "SQLite", "Modellinferenz", "Ende-zu-Ende",
                     "36", "4 / 4", "124"):
            self.assertIn(term, hero)
        for forbidden in ("Die Trefferquote stieg", "Ich habe trotzdem weitergefragt",
                          "Unser LLM wurde hier noch nicht getestet",
                          "keine Kundendaten, kein Live-LLM",
                          "49,25 %", "2.304,41"):
            self.assertNotIn(forbidden, hero)
        # Compact, meaningful first impression, without source URLs being counted.
        clean = re.sub(r'\bhttps://[^\s"]+', '', re.sub(r'<[^>]+>', ' ', hero))
        self.assertLessEqual(len(clean.split()), 230)

    def test_technical_implementation_is_concrete_and_verified(self):
        for term in ("lokalen Workflow", "Qwen", "n8n", "Python-API",
                     "SQLite", "36", "LLM-Inferenzen", "124",
                     "CI-Jobs", "Approval", "Restart", "Fail-closed"):
            self.assertIn(term, self.page)
        for url in ("/actions/runs/42399345922", "/actions/runs/42413698800",
                    "/actions/runs/42421588733"):
            self.assertIn(url, self.page)

    def test_problem_implementation_validation_decision_in_one_minute(self):
        for label in ("Problem &amp; Systemdesign", "Integration &amp; Betrieb",
                      "Tests &amp; Entscheidung", "Unstrukturierte Anfrage",
                      "Fehlerpfade", "Priorisierungsrisiko"):
            self.assertIn(label.casefold(), self.page.casefold())
        self.assertIn("5 von 9", self.page)

    def test_business_example_is_concrete_not_fictional_customer_claim(self):
        self.assertIn("Seit dem Update lassen sich keine Rechnungen exportieren", self.page)
        self.assertIn("Anwendungsbeispiel", self.page)
        self.assertIn("kein historisches Kundenticket", self.page)
        self.assertIn("Geschäftliche Frage", self.page)

    def test_bounded_pilot_is_available_as_evidence_not_a_sales_claim(self):
        for term in ("32 gelabelten", "synthetischen", "10/32", "11/32",
                     "22/32", "5 von 9", "explorativ", "NLBSE", "Volvo"):
            self.assertIn(term.casefold(), self.page.casefold())
        self.assertGreaterEqual(self.page.count("<details>"), 3)

    def test_separate_benchmarks_are_not_misrepresented(self):
        self.assertEqual(142320, self.nlbse["observed_issue_count"])
        self.assertEqual(541, self.nlbse["repeated_issue_id_rows"])
        self.assertEqual(9454, self.volvo["observed"]["total_observed_group_transitions"])
        self.assertEqual(142320, self.contract["streams"]["classification"]["published_test_count"])
        self.assertIn("Datensätze sind nicht miteinander verknüpft", self.page)
        self.assertIn("Keyword-Heuristik", self.page)
        self.assertIn("kein vollwertiger Vergleich", self.page)
        self.assertNotIn("Unser LLM wurde hier noch nicht getestet", self.page)

    def test_no_public_inference_or_tracking_requests(self):
        for forbidden in ("api.openai.com", "webhook/internal-service-intake",
                          "localhost:5678", "<script", "fetch(", "XMLHttpRequest",
                          "sfs-decision-evidence.sfs-labs-core.workers.dev"):
            self.assertNotIn(forbidden, self.page)
        self.assertIn("connect-src 'none'", self.page)
        self.assertIn("form-action 'none'", self.page)

    def test_real_attribution_contact_and_mobile_readability(self):
        for term in ("Mathias Steinbach", "AI-gestützt",
                     "mailto:contact@sfs-labs.dev", 'id="kontakt"',
                     "HYBRID_DECISION_RECORD.md", "RESEARCH_DESIGN.md",
                     "@media(max-width:770px)", "focus-visible",
                     "prefers-reduced-motion"):
            self.assertIn(term, self.page)


if __name__ == "__main__":
    unittest.main()
