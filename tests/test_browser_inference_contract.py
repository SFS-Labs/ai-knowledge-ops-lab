"""Static and prompt-provenance invariants for the optional browser Qwen demo."""
from pathlib import Path
import json
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "docs/live.html").read_text(encoding="utf-8")
JS = (ROOT / "docs/live.js").read_text(encoding="utf-8")


class BrowserInferenceContractTests(unittest.TestCase):
    def test_real_inference_not_replay_or_paid_api(self):
        for term in ("CreateMLCEngine", "chat.completions.create",
                     'response_format: { type: "json_object" }',
                     "temperature: 0", "max_tokens: 56", "JSON.parse(raw)",
                     "output.textContent = parsed.label"):
            self.assertIn(term, JS)
        for forbidden in ("replay.json", "api.openai.com", "Bearer ", "X-API-Key",
                          "localStorage", "sessionStorage", "innerHTML", "fetch("):
            self.assertNotIn(forbidden, JS)

    def test_accurate_scope_and_navigation(self):
        for fragment in ("nicht</strong> n8n-Orchestrierung", "SQLite-Speicherung",
                         "kein genehmigtes Routing", "gleiche Modellfamilie",
                         "WebGPU", "BETA"):
            self.assertIn(fragment, HTML)
        self.assertIn('src="./live.js"', HTML)
        self.assertIn('href="./live.html"',
                      (ROOT / "docs/index.html").read_text(encoding="utf-8"))

    def test_exact_development_selected_prompt(self):
        sys.path.insert(0, str(ROOT / "showcases/internal-service-intake/evaluation"))
        from nlbse_llm_retest import V2_SYSTEM_PROMPT, V2_PROMPT_VERSION
        lines = [s for s in JS.splitlines() if s.startswith("const SYSTEM_PROMPT = ")]
        self.assertEqual(1, len(lines))
        self.assertTrue(lines[0].endswith(";"))
        encoded = lines[0][len("const SYSTEM_PROMPT = "):-1]
        self.assertEqual(json.loads(encoded), V2_SYSTEM_PROMPT)
        self.assertIn(V2_PROMPT_VERSION, JS)
        for term in ("54/96", "46/96", "6/24", "Quantisierung"):
            self.assertIn(term, HTML)

    def test_security_and_resource_limits(self):
        for term in ("connect-src 'self'", "script-src 'self'", "base-uri 'none'",
                     "form-action 'none'", 'maxlength="1200"', "disabled",
                     "script-src 'self' 'wasm-unsafe-eval'"):
            self.assertIn(term, HTML)
        self.assertNotIn(" 'unsafe-eval'", HTML)
        for term in ("const LIMIT = 12", "isValidInput", "navigator.gpu.requestAdapter",
                     "classify.disabled = true", "model_id === select.value"):
            self.assertIn(term, JS)
        self.assertNotIn("webhook/internal-service-intake", JS)


if __name__ == "__main__":
    unittest.main()
