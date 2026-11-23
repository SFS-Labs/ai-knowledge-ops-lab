"""Source-backed portfolio publication smoke checks — offline stdlib only."""
from __future__ import annotations

import re
import unittest
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse, unquote

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
NEW_PAGES = ("work.html", "security-engineering.html", "agent-systems.html", "adversarial-evaluation.html")
EXISTING_PAGES = ("interactive.html", "recruiter.html")
ALL_PORTFOLIO_PAGES = tuple(sorted(p.name for p in DOCS.glob("*.html")))
REQUIRED_PORTFOLIO_PAGES = NEW_PAGES + EXISTING_PAGES + ("index.html", "hubspot-stripe.html", "live.html")
AGENT_SOURCE = DOCS / "portfolio-agent-evidence-2026-11-23.md"

class TagAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.ids = []
        self.has_main = False
        self.has_h1 = False
        self.has_stylesheet = False
        self.assets = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and "href" in a:
            self.links.append(a["href"])
        if tag == "script" and a.get("src"):
            self.assets.append(a["src"])
        if tag == "link" and a.get("rel") == "stylesheet":
            self.assets.append(a["href"])
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
                self.assertIn('href="interactive.html#launch-agent"', html)
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
        for path in ("security-engineering.html", "agent-systems.html", "adversarial-evaluation.html"):
            self.assertIn(f'href="{path}"', work)
            self.assertIn(f'href="{path}"', interactive)
            self.assertIn(f'href="{path}"', recruiter)

    def test_conversation_entry_is_direct_and_does_not_preload_widget(self):
        recruiter = (DOCS / "recruiter.html").read_text(encoding="utf-8")
        interactive = (DOCS / "interactive.html").read_text(encoding="utf-8")
        self.assertIn('href="interactive.html#launch-agent">Portfolio interaktiv erkunden</a>', recruiter)
        self.assertIn('id="launch-agent"', interactive)
        self.assertIn('KI-Guide öffnen: Sprechen oder Schreiben', interactive)
        self.assertIn('["elevenlabs-convai:call","elevenlabs-convai:message"]', interactive)
        self.assertIn('script.src="https://unpkg.com/@elevenlabs/convai-widget-embed"', interactive)
        self.assertIn('trigger.addEventListener("click",function()', interactive)
        self.assertIn('showWidgetError("Widget antwortet nicht', interactive)
        self.assertIn('role="status" aria-atomic="true"', interactive)
        self.assertIn('scroll-margin-top:', interactive)
        self.assertNotIn('Vor dem Klick laden', interactive)

    def test_recruiter_mobile_navigation_preserves_all_links(self):
        recruiter = (DOCS / "recruiter.html").read_text(encoding="utf-8")
        self.assertIn(".nav{flex-wrap:nowrap;max-width:100%;overflow-x:auto;", recruiter)
        self.assertIn('href="#profil">Profil</a>', recruiter)
        self.assertIn('href="https://github.com/SFS-Labs/SFS-Labs">GitHub</a>', recruiter)

    def test_all_portfolio_routes_and_assets_resolve_offline(self):
        self.assertTrue(set(REQUIRED_PORTFOLIO_PAGES).issubset(ALL_PORTFOLIO_PAGES))
        pages = {}
        for name in ALL_PORTFOLIO_PAGES:
            parser = TagAudit()
            parser.feed((DOCS / name).read_text(encoding="utf-8"))
            pages[name] = parser
        for name, page in pages.items():
            with self.subTest(page=name):
                if name != "interactive.html":
                    self.assertIn("interactive.html#launch-agent", page.links)
                    self.assertNotIn("interactive.html", page.links)
                    self.assertNotIn("elevenlabs-convai", (DOCS / name).read_text(encoding="utf-8"))
                for link in page.links + page.assets:
                    parsed = urlparse(link)
                    if parsed.scheme or parsed.netloc:
                        continue
                    local = unquote(parsed.path)
                    target = "index.html" if local in (".", "./", "/") else local.removeprefix("./") if local else name
                    resolved = (DOCS / target).resolve()
                    self.assertTrue(resolved.is_relative_to(DOCS.resolve()), link)
                    self.assertTrue(resolved.is_file(), f"{name}: missing {link}")
                    if parsed.fragment and target in pages:
                        self.assertIn(unquote(parsed.fragment), pages[target].ids, f"{name}: {link}")
        self.assertIn("launch-agent", pages["interactive.html"].ids)

    def test_evidence_claims_are_qualified(self):
        work = (DOCS / "work.html").read_text(encoding="utf-8")
        sec = (DOCS / "security-engineering.html").read_text(encoding="utf-8")
        agents = (DOCS / "agent-systems.html").read_text(encoding="utf-8")
        self.assertIn("133", sec)
        self.assertNotIn("Freebuff", sec)
        self.assertNotIn("Freebuff", work)
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
