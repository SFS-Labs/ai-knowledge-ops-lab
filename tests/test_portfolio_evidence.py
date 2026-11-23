"""Source-backed portfolio publication smoke checks — offline stdlib only."""
from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
NEW_PAGES = ("work.html", "security-engineering.html", "agent-systems.html")
EXISTING_PAGES = ("interactive.html", "recruiter.html")
AGENT_SOURCE = DOCS / "portfolio-agent-evidence-2026-11-23.md"

class TagAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = []
        self.has_main = False
        self.has_h1 = False
        self.has_stylesheet = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "main":
            self.has_main = True
        if tag == "h1":
            self.has_h1 = True
        if tag == "link" and a.get("rel") == "stylesheet":
            if a.get("href") == "portfolio-evidence.css":
                self.has_stylesheet = True

class PortfolioEvidence(unittest.TestCase):
    def test_new_pages_are_source_backed_and_navigable(self):
        for filename in NEW_PAGES:
            with self.subTest(filename=filename):
                p = DOCS / filename
                html = p.read_text(encoding="utf-8")
                parsed = TagAudit()
                parsed.feed(html)
                self.assertTrue(parsed.has_main and parsed.has_h1)
                self.assertTrue(parsed.has_stylesheet)
                self.assertEqual(len(parsed.ids), len(set(parsed.ids)))
                self.assertIn('href="interactive.html"', html)
                self.assertIn("https://github.com/SFS-Labs/", html)
                for link in parsed.links:
                    parsed_url = urlparse(link)
                    if parsed_url.scheme or link.startswith("#") or link.startswith("mailto:"):
                        continue
                    local = DOCS / parsed_url.path
                    self.assertTrue(local.exists(), f"{p.name}: missing {link}")

    def test_all_entrypoints_have_full_work_and_source_links(self):
        recruiter = (DOCS / "recruiter.html").read_text(encoding="utf-8")
        interactive = (DOCS / "interactive.html").read_text(encoding="utf-8")
        work = (DOCS / "work.html").read_text(encoding="utf-8")
        self.assertIn('href="work.html"', recruiter)
        self.assertIn('href="work.html"', interactive)
        for path in ("security-engineering.html", "agent-systems.html"):
            self.assertIn(f'href="{path}"', work)
            self.assertIn(f'href="{path}"', interactive)
            self.assertIn(f'href="{path}"', recruiter)

    def test_evidence_claims_are_qualified(self):
        work = (DOCS / "work.html").read_text(encoding="utf-8")
        sec = (DOCS / "security-engineering.html").read_text(encoding="utf-8")
        agents = (DOCS / "agent-systems.html").read_text(encoding="utf-8")
        self.assertIn("133", sec)
        self.assertIn("Blindtest", sec)
        self.assertIn("NICHT", sec.upper())
        self.assertIn("keine", agents.lower())
        self.assertIn("nicht", work.lower())
        self.assertIn("no", AGENT_SOURCE.read_text(encoding="utf-8").lower())

    def test_no_private_repo_links_or_sensitive_payloads_in_new_pages(self):
        for filename in NEW_PAGES:
            s=(DOCS / filename).read_text(encoding="utf-8").lower()
            for forbidden in ("sfs-personal-restricted", "/sfs-assurance-core", "private-genotype", "sk_live_"):
                self.assertNotIn(forbidden, s)

if __name__ == "__main__":
    unittest.main()
