"""Recruiter-first presentation gate: candidate, decision, counterexample and evidence.

These checks keep the public work sample from drifting back into SaaS-style
landing-page language or importing unrelated research benchmark performance.
"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"docs"/"index.html"
CONTRACT=ROOT/"showcases"/"internal-service-intake"/"evaluation"/"research_contract.json"


class _HeroText(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_hero=False
        self.stack_depth=0
        self.words=[]

    def handle_starttag(self,tag,attrs):
        attrs=dict(attrs)
        if tag=="section" and "hero" in attrs.get("class","").split():
            self.in_hero=True
            self.stack_depth=1
        elif self.in_hero:
            if tag in ("section","div","p","h1","span","a","aside","strong"):
                self.stack_depth+=1

    def handle_data(self,data):
        if self.in_hero:
            self.words.extend(data.split())

    def handle_endtag(self,tag):
        if tag=="section" and self.in_hero:
            self.in_hero=False


class RecruiterDecisionPageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page=PAGE.read_text(encoding="utf-8")
        cls.contract=json.loads(CONTRACT.read_text(encoding="utf-8"))
        cls.volvo=json.loads((CONTRACT.parent/"evidence"/"volvo-2013-source-audit-ci27.json").read_text(encoding="utf-8"))
        cls.nlbse=json.loads((CONTRACT.parent/"evidence"/"nlbse2023-full-test-ci29.json").read_text(encoding="utf-8"))

    def test_candidate_not_company_is_the_sender(self):
        head=self.page[:self.page.index('<section class="shell hero"')]
        self.assertIn("Mathias Steinbach",head)
        self.assertIn("AI Implementation",head)
        self.assertIn("kundennahes Engineering",head)
        self.assertNotIn("Scale",head)
        self.assertNotIn("SFS LABS / DECISION ENGINEERING",head)

    def test_first_20_seconds_show_hypothesis_and_counterexample(self):
        hero=self.page.split('<section class="shell hero"',1)[1].split("</section>",1)[0]
        self.assertIn("Die Trefferquote stieg",hero)
        self.assertIn("Fünf von neun dringlichen Testfällen",hero)
        self.assertIn("teuer werden könnte",hero)
        self.assertIn("vollständige CI erfolgreich",hero)
        self.assertNotIn("Unser LLM wurde hier noch nicht getestet",hero)
        self.assertNotIn("keine Kundendaten, kein Live-LLM",hero)
        self.assertNotIn("49,25 %",hero)
        self.assertNotIn("2.304,41",hero)
        self.assertLessEqual(len(re.findall(r"\b\w+\b",re.sub(r"<[^>]+>"," ",hero))),210)

    def test_three_claims_form_a_verifiable_decision(self):
        for v in ("Erst eine funktionierende Strecke", "Dann den eigenen Ansatz angegriffen",
                  "Die Frage neu gestellt", "wirtschaftlich", "menschliche Freigabe"):
            self.assertIn(v.casefold(),self.page.casefold())

    def test_nontechnical_example_is_honest_and_concrete(self):
        self.assertIn("Seit dem Update lassen sich keine Rechnungen exportieren",self.page)
        self.assertIn("Illustrativer Servicefall",self.page)
        self.assertIn("kein Kundenticket",self.page)
        self.assertIn("betriebliche Dringlichkeit",self.page)

    def test_bounded_case_and_evidence_are_deferred_not_hidden(self):
        for term in ("32 gelabelten", "synthetischen", "10/32","11/32",
                     "22/32","5 von 9","explorativ","CI #31",
                     "NLBSE","Volvo","49,25 %","9.454"):
            self.assertIn(term.casefold(),self.page.casefold())
        self.assertGreaterEqual(self.page.count("<details>"),3)

    def test_source_data_are_not_falsely_merged(self):
        self.assertEqual(142320,self.nlbse["observed_issue_count"])
        self.assertEqual(541,self.nlbse["repeated_issue_id_rows"])
        self.assertEqual(9454,self.volvo["observed"]["total_observed_group_transitions"])
        self.assertEqual(142320,self.contract["streams"]["classification"]["published_test_count"])
        self.assertIn("Datensätze sind nicht miteinander verknüpft",self.page)
        self.assertNotIn("realisierten ROI",self.page)
        self.assertNotIn("Unser LLM wurde hier noch nicht getestet",self.page)

    def test_no_external_calls_public_endpoints_or_data_collection(self):
        for forbidden in ("api.openai.com","webhook/internal-service-intake",
                          "localhost:5678","<script","fetch(","XMLHttpRequest",
                          "sfs-decision-evidence.sfs-labs-core.workers.dev"):
            self.assertNotIn(forbidden,self.page)
        self.assertIn("connect-src 'none'",self.page)
        self.assertIn("form-action 'none'",self.page)

    def test_contact_and_real_evidence_are_easy_to_reach(self):
        self.assertIn('id="kontakt"',self.page)
        self.assertIn("mailto:contact@sfs-labs.dev",self.page)
        self.assertIn("https://github.com/SFS-Labs/ai-knowledge-ops-lab/actions/runs/42413698800",self.page)
        self.assertIn("HYBRID_DECISION_RECORD.md",self.page)
        self.assertIn("RESEARCH_DESIGN.md",self.page)

    def test_mobile_typography_and_accessibility(self):
        self.assertIn('name="viewport"',self.page)
        self.assertIn("@media(max-width:770px)",self.page)
        self.assertIn("prefers-reduced-motion",self.page)
        self.assertIn("focus-visible",self.page)
        self.assertIn('lang="de"',self.page)


if __name__=="__main__":
    unittest.main()
