"""Single-change contract tests for German questionmark/bug-report prompt suffix."""
import io
import inspect
import json
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"showcases/internal-service-intake/evaluation"))
import nlbse_questionmark_ab as experiment
import nlbse_user_prompt_ab as old
import nlbse_llm_eval as source


class QuestionMarkPromptTests(unittest.TestCase):
    def test_exact_only_verbally_supplied_suffix(self):
        self.assertEqual(experiment.QUESTIONMARK_PROMPT, old.USER_SYSTEM_PROMPT + experiment.SUFFIX)
        self.assertEqual(experiment.SUFFIX, "\n\nAlles was ein Fragezeichen am Ende des Satzes hat, wird als Question kategorisiert.\n\nEin bug report ist wahrscheinlich deutlich technischer und beschreibender an der Ursache, an der vermuteten Ursache formuliert")
        self.assertEqual(experiment.QUESTIONMARK_PROMPT,
                         experiment.QUESTIONMARK_FILE.read_text(encoding="utf-8").rstrip("\n"))

    def test_inference_request_identical_except_system_prompt(self):
        v1=inspect.getsource(old.call_with_user_prompt).strip()
        v2=inspect.getsource(experiment.call_with_questionmark_prompt).strip()
        recovered=v2.replace("def call_with_questionmark_prompt(row):","def call_with_user_prompt(row):").replace("QUESTIONMARK_PROMPT","USER_SYSTEM_PROMPT")
        self.assertEqual(v1, recovered)

    def test_json_validation_in_both_variants(self):
        seen=[]
        def fake_response(req, timeout):
            payload=json.loads(req.data)
            seen.append(payload)
            obj={"choices":[{"message":{"content":'{"label":"question"}'}}]}
            return io.BytesIO(json.dumps(obj).encode())
        example={"title":"Install question?","body":"How do I configure my system?"}
        with patch.object(experiment.urllib.request,"urlopen",side_effect=fake_response):
            a,ea,*_=old.call_with_user_prompt(example)
            b,eb,*_=experiment.call_with_questionmark_prompt(example)
        self.assertEqual((a,b,ea,eb),("question","question",None,None))
        self.assertEqual(len(seen),2)
        self.assertEqual(seen[0]["messages"][1],seen[1]["messages"][1])
        self.assertEqual(seen[0]["response_format"],seen[1]["response_format"])
        self.assertEqual(seen[0]["temperature"],0)
        self.assertEqual(seen[0]["max_tokens"],56)
        self.assertEqual(seen[0]["response_format"]["json_schema"]["schema"],source.JSON_SCHEMA)
        self.assertEqual(seen[1]["messages"][0]["content"],experiment.QUESTIONMARK_PROMPT)

    def test_browser_uses_full_new_prompt(self):
        js=(ROOT/"docs/live.js").read_text(encoding="utf-8")
        match=re.search(r'const SYSTEM_PROMPT = ("(?:\\.|[^"\\])*");',js)
        self.assertIsNotNone(match)
        self.assertEqual(json.loads(match.group(1)),experiment.QUESTIONMARK_PROMPT)
        self.assertIn("sfs-operator-de-questionmark-bugstyle-v2",js)
        page=(ROOT/"docs/live.html").read_text(encoding="utf-8")
        self.assertIn("Fragezeichen-/Bug-Report-Regeln",page)
        self.assertIn("nicht</strong> auf diese Variante",page)


if __name__=="__main__":
    unittest.main()
