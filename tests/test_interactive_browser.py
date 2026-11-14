"""Browser smoke tests for the public portfolio UI and mocked ElevenLabs client-tool event.

No live agent connection, API keys, external requests, paid inference or user data.
Run: python -m unittest discover -s tests -p 'test_interactive_browser.py' -v
Requires: playwright Python package and Chromium browser.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from playwright.sync_api import sync_playwright

HERE = Path(__file__).resolve()
REPO = HERE.parents[1]
HTML = REPO / "docs" / "interactive.html"
GATE_OFF = "const AGENT_PUBLIC_READY = false;"
GATE_ON = "const AGENT_PUBLIC_READY = true;"


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
                    status=200, content_type="application/javascript", body="window.__widgetStubLoaded=true;"
                ))
                page.goto(HTML.as_uri(), wait_until="domcontentloaded")
                self.assertIn("Systeme verbinden.", page.locator("h1").inner_text())
                if self.public_ready:
                    self.assertTrue(page.locator("#launch-agent").is_enabled())
                    self.assertEqual(page.locator("elevenlabs-convai").count(), 0)
                    self.assertEqual(requests, [], "Third-party widget loaded without visitor click")
                    page.locator("#launch-agent").click()
                    self.assertEqual(page.locator("elevenlabs-convai").count(), 1)
                    self.assertTrue(page.locator("#launch-agent").is_hidden())
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

    def test_widget_call_injects_exact_allowlisted_client_tool(self):
        page = self.browser.new_page(viewport={"width": 1280, "height": 920})
        # This fixture enables the widget block only in an offline file; remote widget JS never loads.
        page.route("https://unpkg.com/**", lambda route: route.fulfill(
            status=200, content_type="application/javascript", body="window.__widgetStubLoaded=true;"
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
          tools.open_project({project_key:"https://evil.example"});
          const rejected=(div.querySelector("a")?.href === valid.href);
          tools.open_project({project_key:"__proto__"});
          return {...valid,rejected,prototypeRejected:div.querySelector("a")?.href === valid.href};
        }""")
        self.assertNotIn("error", result)
        self.assertTrue(result["visible"])
        self.assertIn("Tender Intelligence", result["text"])
        self.assertTrue(result["href"].startswith(
            "https://github.com/SFS-Labs/tender-intelligence-case-study/"))
        self.assertEqual(result["newtab"], "_blank")
        self.assertTrue(result["rejected"])
        self.assertTrue(result["prototypeRejected"])
        page.close()


if __name__ == "__main__":
    unittest.main()
