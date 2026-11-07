"""Static scope and safety invariants for the optional browser-side model demo."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "docs/live.html").read_text(encoding="utf-8")
JS = (ROOT / "docs/live.js").read_text(encoding="utf-8")

class BrowserInferenceContractTests(unittest.TestCase):
    def test_real_inference_not_replay_or_paid_api(self):
        self.assertIn("CreateMLCEngine", JS)
        self.assertIn("chat.completions.create", JS)
        self.assertIn('response_format: { type: "json_object" }', JS)
        self.assertIn('temperature: 0', JS)
        self.assertIn('max_tokens: 56', JS)
        self.assertIn("JSON.parse(raw)", JS)
        self.assertIn("output.textContent = parsed.label", JS)
        for forbidden in ("replay.json","api.openai.com","Bearer ","X-API-Key",
                          "localStorage","sessionStorage","innerHTML","fetch("):
            self.assertNotIn(forbidden,JS)

    def test_no_claim_that_browser_executes_backend_or_approval(self):
        for fragment in ("nicht</strong> n8n-Orchestrierung","SQLite-Speicherung",
                         "kein genehmigtes Routing","gleiche Modellfamilie",
                         "Eine", "WebGPU", "BETA"):
            self.assertIn(fragment, HTML)
        self.assertIn('src="./live.js"',HTML)
        self.assertIn('href="./live.html"',(ROOT/"docs/index.html").read_text(encoding="utf-8"))

    def test_security_and_resource_limits(self):
        for item in ("connect-src 'self'", "script-src 'self'", "base-uri 'none'",
                     "form-action 'none'", "maxlength=\"1200\"", "disabled"):
            self.assertIn(item,HTML)
        for item in ("const LIMIT = 12", "isValidInput", "navigator.gpu.requestAdapter",
                     "classify.disabled = true", "model_id === select.value"):
            self.assertIn(item,JS)
        self.assertNotIn("webhook/internal-service-intake",JS)

if __name__=="__main__":
    unittest.main()
