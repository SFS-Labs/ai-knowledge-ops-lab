"""Browser smoke tests for the public portfolio UI and mocked ElevenLabs client-tool event.

No live agent connection, API keys, external requests, paid inference or user data.
Run: python -m unittest discover -s tests -p 'test_interactive_browser.py' -v
Requires: playwright Python package and Chromium browser.
"""
from __future__ import annotations

import tempfile
import os
import unittest
from pathlib import Path
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None  # Optional dependency: generic repository CI skips Chromium-specific checks.

HERE = Path(__file__).resolve()
REPO = HERE.parents[1]
HTML = REPO / "docs" / "interactive.html"
GATE_OFF = "const AGENT_PUBLIC_READY = false;"
GATE_ON = "const AGENT_PUBLIC_READY = true;"


@unittest.skipUnless(sync_playwright is not None, "Playwright not installed in core offline CI")
class InteractiveBrowserSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        cls.browser = cls.pw.chromium.launch(headless=True)
        cls.temp = tempfile.TemporaryDirectory(prefix="sfs-interactive-test-")
        source = HTML.read_text(encoding="utf-8")
        assert source.count(GATE_OFF) + source.count(GATE_ON) == 1, "Public launch gate invalid."
        cls.public_ready = GATE_ON in source
        cls.fixture = Path(cls.temp.name) / "interactive-widget-probe.html"
        cls.fixture.write_text(source.replace(GATE_OFF, GATE_ON, 1), encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()
        cls.temp.cleanup()

    def test_portfolio_examples_and_correct_widget_gate(self):
        for width, height in ((1440, 900), (390, 844)):
            with self.subTest(width=width):
                page = self.browser.new_page(viewport={"width": width, "height": height})
                requests = []
                page.on("request", lambda request: requests.append(request.url) if "unpkg.com" in request.url else None)
                page.route("https://unpkg.com/**", lambda route: route.fulfill(
                    status=200, content_type="application/javascript", body="window.__widgetStubLoaded=true;customElements.define(\'elevenlabs-convai\',class extends HTMLElement {});"
                ))
                page.goto(HTML.as_uri(), wait_until="domcontentloaded")
                self.assertIn("Systeme verbinden.", page.locator("h1").inner_text())
                if self.public_ready:
                    self.assertTrue(page.locator("#launch-agent").is_enabled())
                    self.assertEqual(page.locator("elevenlabs-convai").count(), 0)
                    self.assertEqual(requests, [], "Third-party widget loaded without visitor click")
                    page.locator("#launch-agent").click()
                    self.assertEqual(page.locator("elevenlabs-convai").count(), 1)
                    self.assertEqual(page.locator("elevenlabs-convai").get_attribute("agent-id"), "agent_7701m848yn67eqsbb1tyxshf3h13")
                    page.locator("#launch-agent").wait_for(state="hidden", timeout=3000)
                    self.assertEqual(len(requests), 1, "Widget must be loaded exactly once after click")
                else:
                    self.assertTrue(page.locator("#launch-agent").is_disabled())
                    self.assertEqual(page.locator("elevenlabs-convai").count(), 0)
                page.locator("[data-example=tests]").click()
                self.assertIn("technischen Tests", page.locator("#question").inner_text())
                self.assertIn("135", page.locator("#answer").inner_text())
                self.assertIn("github.com", page.locator("#answerlink").get_attribute("href"))
                self.assertLessEqual(
                    page.evaluate("document.documentElement.scrollWidth - window.innerWidth"), 1,
                    "Horizontal overflow on %spx viewport" % width
                )
                page.close()

    def test_public_github_inventory_is_opt_in_and_private_safe(self):
        """All public repos require one deliberate API request; private/fake records never render."""
        import json
        url = "https://api.github.com/users/SFS-Labs/repos?per_page=100&sort=pushed"
        fixtures = [
            {"name": "ctf-skills", "owner": {"login": "SFS-Labs"}, "private": False,
             "html_url": "https://github.com/SFS-Labs/ctf-skills", "pushed_at": "2026-11-23T12:00:00Z"},
            {"name": "agent-toolkit", "owner": {"login": "SFS-Labs"}, "private": False,
             "html_url": "https://github.com/SFS-Labs/agent-toolkit", "pushed_at": "2026-11-22T12:00:00Z"},
            {"name": "new-public-ai-integration-repo", "owner": {"login": "SFS-Labs"}, "private": False,
             "html_url": "https://github.com/SFS-Labs/new-public-ai-integration-repo",
             "pushed_at": "2026-11-23T13:00:00Z"},
            {"name": "private-repo-fixture", "owner": {"login": "SFS-Labs"}, "private": True,
             "html_url": "https://github.com/SFS-Labs/private-repo-fixture", "pushed_at": "2026-11-23T12:00:00Z"},
            {"name": "fake-upstream", "owner": {"login": "Elsewhere"}, "private": False,
             "html_url": "https://github.com/Elsewhere/fake-upstream", "pushed_at": "2026-11-23T12:00:00Z"},
        ]
        page = self.browser.new_page(viewport={"width": 1280, "height": 960})
        hits = []
        page.route("https://api.github.com/**", lambda route: (
            hits.append(route.request.url),
            route.fulfill(status=200, content_type="application/json",
                          headers={"Access-Control-Allow-Origin": "*"},
                          body=json.dumps(fixtures))
        ))
        try:
            page.goto((REPO / "docs" / "work.html").as_uri(), wait_until="domcontentloaded")
            self.assertEqual(hits, [], "GitHub must not be requested before visitor opt-in")
            page.locator("#refresh-public-repositories").click()
            page.locator("#public-repository-list li").first.wait_for(timeout=5000)
            self.assertEqual(hits, [url], "One public account API call per explicit inventory click")
            self.assertEqual(page.locator("#public-repository-list li").count(), 3)
            rendered = page.locator("#public-repository-list").inner_text()
            self.assertIn("ctf-skills", rendered)
            self.assertIn("Atlan-Agent-Toolkit im SFS-Labs-Portfolio", rendered)
            self.assertIn("new-public-ai-integration-repo", rendered)
            self.assertIn("Weiteres öffentliches SFS-Labs-Portfolio-Repository", rendered)
            self.assertNotIn("private-repo-fixture", rendered)
            self.assertNotIn("fake-upstream", rendered)
            self.assertIn("3 öffentliche Repositories", page.locator("#public-repository-status").inner_text())
        finally:
            page.close()

    def test_live_production_widget_bootstrap(self):
        """Opt-in external smoke: real production GitHub Pages and real ElevenLabs widget JS.

        Does not initiate a conversation, request microphone access, or spend inference credits.
        """
        url = os.environ.get("SFS_INTERACTIVE_PRODUCTION_URL")
        if not url:
            self.skipTest("External production GitHub Pages URL not configured")
        page = self.browser.new_page(viewport={"width": 1280, "height": 860})
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=25000)
            button = page.locator("#launch-agent")
            self.assertTrue(button.is_enabled(), "Production gate must be active")
            self.assertEqual(page.locator("elevenlabs-convai").count(), 0)
            button.click()
            page.locator("elevenlabs-convai").wait_for(state="attached", timeout=10000)
            page.wait_for_function(
                "() => Boolean(customElements.get('elevenlabs-convai'))",
                timeout=25000
            )
            self.assertEqual(
                page.locator("elevenlabs-convai").get_attribute("agent-id"),
                "agent_7701m848yn67eqsbb1tyxshf3h13"
            )
            page.locator("#launch-agent").wait_for(state="hidden", timeout=6000)
            self.assertIn("Widget bereit", page.locator("#agentstatus").inner_text())
        finally:
            page.close()

    def test_production_pages_and_project_navigation(self):
        """Every published new page should be HTTP 200 and reachable from the actual work index.

        This is a real external HTTP/browser check; it does not invoke a paid agent call.
        """
        interactive = os.environ.get("SFS_INTERACTIVE_PRODUCTION_URL")
        if not interactive:
            self.skipTest("External production GitHub Pages URL not configured")
        self.assertTrue(
            interactive.startswith("https://sfs-labs.github.io/ai-knowledge-ops-lab/"),
            "Do not silently test Cloudflare preview instead of published production"
        )
        base = interactive.rsplit("/", 1)[0] + "/"
        page = self.browser.new_page(viewport={"width": 1280, "height": 850})
        expected = {
            "interactive.html": "SFS Interactive",
            "work.html": "Ausgewählte Arbeiten",
            "security-engineering.html": "Cybersecurity",
            "adversarial-evaluation.html": "Adversarial Evaluation",
            "agent-systems.html": "Agent Systems",
            "recruiter.html": "Mathias Steinbach",
            "hubspot-stripe.html": "HubSpot",
        }
        try:
            for filename, title in expected.items():
                with self.subTest(filename=filename):
                    response = page.goto(base + filename, wait_until="domcontentloaded", timeout=25000)
                    self.assertIsNotNone(response, filename)
                    self.assertEqual(response.status, 200, filename)
                    self.assertIn(title, page.title())
                    self.assertGreater(page.locator("a[href]").count(), 0)
            response = page.goto(base + "work.html", wait_until="domcontentloaded")
            self.assertEqual(response.status, 200)
            for filename in ("interactive.html", "security-engineering.html",
                             "adversarial-evaluation.html", "agent-systems.html"):
                self.assertGreater(
                    page.locator('a[href="' + filename + '"]').count(), 0,
                    "Portfolio index lacks public navigation to " + filename
                )
            page.locator('a[href="security-engineering.html"]').first.click()
            page.wait_for_url(base + "security-engineering.html")
            self.assertIn("Cybersecurity", page.title())
        finally:
            page.close()

    def test_new_cybersecurity_sources_and_widget_target(self):
        source = HTML.read_text(encoding="utf-8")
        self.assertIn("const AGENT_PUBLIC_READY = true;", source)
        self.assertIn("agent_7701m848yn67eqsbb1tyxshf3h13", source)
        self.assertIn('href="adversarial-evaluation.html"', source)
        self.assertNotIn("Freebuff", source)
        self.assertIn("benchmark_engineering", source)

    def test_widget_fallback_when_external_script_never_registers_custom_element(self):
        """A successful CDN response that never registers the element must not freeze CTA."""
        page=self.browser.new_page(viewport={"width":1280,"height":860})
        page.route("https://unpkg.com/**",lambda route:route.fulfill(
            status=200,content_type="application/javascript",body="window.__loadedWithoutWidget=true;"
        ))
        try:
            page.goto(self.fixture.as_uri(),wait_until="domcontentloaded")
            page.locator("#launch-agent").click()
            page.wait_for_function(
                "() => document.querySelector('#launch-agent').disabled === false",
                timeout=14000
            )
            self.assertEqual(page.locator("elevenlabs-convai").count(),0)
            self.assertIn("erneut laden",page.locator("#agentstatus").inner_text())
            self.assertIn("Erneut versuchen",page.locator("#launch-agent").inner_text())
        finally:
            page.close()

    def test_widget_bootstrap_local_timing_and_keyboard_focus(self):
        page = self.browser.new_page(viewport={"width": 390, "height": 844})
        page.route("https://unpkg.com/**", lambda route: route.fulfill(
            status=200, content_type="application/javascript",
            body="customElements.define('elevenlabs-convai',class extends HTMLElement {});"
        ))
        try:
            page.goto(self.fixture.as_uri(), wait_until="domcontentloaded")
            self.assertEqual(page.evaluate("performance.getEntriesByName('sfs:widget-bootstrap').length"), 0)
            self.assertTrue(page.locator("#launch-ready").is_hidden())
            page.locator("#launch-agent").focus()
            page.keyboard.press("Enter")
            page.locator("#launch-agent").wait_for(state="hidden")
            self.assertTrue(page.locator("#launch-ready").is_visible())
            self.assertIn("Sprechblase unten rechts", page.locator("#launch-ready").inner_text())
            self.assertEqual(page.evaluate("document.activeElement.id"), "launch-ready")
            self.assertEqual(page.evaluate("performance.getEntriesByName('sfs:widget-bootstrap').length"), 1)
            self.assertGreaterEqual(page.evaluate("performance.getEntriesByName('sfs:widget-bootstrap')[0].duration"), 0)
            self.assertEqual(page.locator("elevenlabs-convai").count(), 1)
        finally:
            page.close()

    def test_failed_widget_load_can_retry_and_does_not_duplicate(self):
        page = self.browser.new_page(viewport={"width": 390, "height": 844})
        attempts = []
        def route_widget(route):
            attempts.append(route.request.url)
            if len(attempts) == 1:
                route.abort()
            else:
                route.fulfill(status=200, content_type="application/javascript",
                              body="customElements.define('elevenlabs-convai',class extends HTMLElement {});")
        page.route("https://unpkg.com/**", route_widget)
        try:
            page.goto(self.fixture.as_uri(), wait_until="domcontentloaded")
            trigger = page.locator("#launch-agent")
            trigger.focus()
            page.keyboard.press("Enter")
            page.wait_for_function("() => document.querySelector('#launch-agent').textContent.includes('Erneut versuchen')")
            self.assertEqual(page.evaluate("document.activeElement.id"), "launch-agent")
            self.assertTrue(page.locator("#launch-ready").is_hidden())
            self.assertEqual(page.locator("elevenlabs-convai").count(), 0)
            self.assertEqual(page.evaluate("performance.getEntriesByName('sfs:widget-error').length"), 1)
            trigger.click()
            trigger.wait_for(state="hidden")
            self.assertEqual(len(attempts), 2)
            self.assertTrue(page.locator("#launch-ready").is_visible())
            self.assertEqual(page.locator("elevenlabs-convai").count(), 1)
            self.assertEqual(page.evaluate("performance.getEntriesByName('sfs:widget-error').length"), 0)
            self.assertEqual(page.evaluate("performance.getEntriesByName('sfs:widget-bootstrap').length"), 1)
        finally:
            page.close()

    def test_mobile_recruiter_navigation_no_page_overflow(self):
        for width in (320, 375, 390, 430):
            with self.subTest(width=width):
                page = self.browser.new_page(viewport={"width": width, "height": 844})
                try:
                    page.goto((REPO / "docs" / "recruiter.html").as_uri(), wait_until="domcontentloaded")
                    self.assertLessEqual(page.evaluate("document.documentElement.scrollWidth - innerWidth"), 1)
                    nav = page.locator("header nav")
                    self.assertEqual(nav.evaluate("(el) => getComputedStyle(el).flexWrap"), "nowrap")
                    self.assertEqual(nav.locator("a").count(), 6)
                    nav.locator("a").last.focus()
                    self.assertEqual(page.evaluate("document.activeElement.textContent"), "GitHub")
                finally:
                    page.close()

    def test_recruiter_entrypoint_links_the_interactive_page(self):
        recruiter=(REPO / "docs" / "recruiter.html").read_text(encoding="utf-8")
        self.assertIn('class="primary" href="interactive.html#launch-agent"', recruiter)
        self.assertIn('<nav class="nav">', recruiter)
        self.assertIn('<a href="interactive.html">SFS Interactive</a>', recruiter)
        self.assertIn('<a href="work.html">Alle Arbeiten</a>', recruiter)

    def test_widget_call_injects_exact_allowlisted_client_tool(self):
        page = self.browser.new_page(viewport={"width": 1280, "height": 920})
        # This fixture enables the widget block only in an offline file; remote widget JS never loads.
        page.route("https://unpkg.com/**", lambda route: route.fulfill(
            status=200, content_type="application/javascript", body="window.__widgetStubLoaded=true;customElements.define(\'elevenlabs-convai\',class extends HTMLElement {});"
        ))
        page.goto(self.fixture.as_uri(), wait_until="domcontentloaded")
        self.assertEqual(page.locator("elevenlabs-convai").count(), 0)
        page.locator("#launch-agent").click()
        self.assertEqual(page.locator("elevenlabs-convai").count(), 1)
        result = page.evaluate("""() => {
          const widget = document.querySelector("elevenlabs-convai");
          const event = new CustomEvent("elevenlabs-convai:call", {detail:{config:{}}});
          widget.dispatchEvent(event);
          const tools=event.detail.config.clientTools;
          if (!tools || typeof tools.open_project !== "function") return {error:"missing tool"};
          tools.open_project({project_key:"tender_intelligence"});
          const div=document.querySelector("#active-evidence");
          const proof=div.querySelector("a");
          const valid={visible:!div.hidden,text:proof?.textContent||"",href:proof?.href||"",newtab:proof?.target};
          tools.open_project({project_key:"security_engineering"});
          const securityHref=div.querySelector("a")?.href || "";
          tools.open_project({project_key:"benchmark_engineering"});
          const benchmarkHref=div.querySelector("a")?.href || "";
          const linksMatch=securityHref.endsWith("/security-engineering.html") && benchmarkHref.endsWith("/adversarial-evaluation.html");
          tools.open_project({project_key:"tender_intelligence"});
          tools.open_project({project_key:"https://evil.example"});
          const rejected=(div.querySelector("a")?.href === valid.href);
          tools.open_project({project_key:"__proto__"});
          return {...valid,rejected,linksMatch,securityHref,benchmarkHref,prototypeRejected:div.querySelector("a")?.href === valid.href};
        }""")
        self.assertNotIn("error", result)
        # Exercise the text-mode handler separately. Mocked event contract, not live vendor verification.
        self.assertTrue(page.evaluate("""() => {
          const widget = document.querySelector("elevenlabs-convai");
          const event = new CustomEvent("elevenlabs-convai:message", {detail:{config:{}}});
          widget.dispatchEvent(event);
          const tools = event.detail.config.clientTools;
          if (!tools || typeof tools.open_project !== "function") return false;
          tools.open_project({project_key:"tender_intelligence"});
          return document.querySelector("#active-evidence a").href.includes("tender-intelligence-case-study");
        }"""))
        self.assertTrue(result["visible"])
        self.assertTrue(result["linksMatch"], "New Cybersecurity/benchmark client-tool keys must open exact trusted relative sources")
        self.assertTrue(result["securityHref"].endswith("/security-engineering.html"))
        self.assertTrue(result["benchmarkHref"].endswith("/adversarial-evaluation.html"))
        self.assertIn("Tender Intelligence", result["text"])
        self.assertTrue(result["href"].startswith(
            "https://github.com/SFS-Labs/tender-intelligence-case-study/"))
        self.assertEqual(result["newtab"], "_blank")
        self.assertTrue(result["rejected"])
        self.assertTrue(result["prototypeRejected"])
        page.close()


if __name__ == "__main__":
    unittest.main()
