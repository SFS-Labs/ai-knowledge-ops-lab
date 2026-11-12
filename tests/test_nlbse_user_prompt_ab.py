"""Verify new operator prompt and exactly-controlled Qwen A/B wrapper."""
import inspect
import io
import json
import re
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"showcases/internal-service-intake/evaluation"))
import nlbse_user_prompt_ab as ab
import nlbse_llm_retest as v2
import nlbse_llm_eval as v1


class OperatorPromptABTests(unittest.TestCase):
    def test_full_verbatim_prompt_and_browser_prompt_match(self):
        value=ab.PROMPT_FILE.read_text(encoding="utf-8").rstrip("\n")
        self.assertEqual(value,ab.USER_SYSTEM_PROMPT)
        self.assertTrue(value.startswith("Du wirst ein diverses Set von GitHub Software-Anfragen"))
        self.assertTrue(value.endswith("Aber JSON ist wahrscheinlich strukturierter"))
        js=(ROOT/"docs/live.js").read_text(encoding="utf-8")
        found=re.search(r'const SYSTEM_PROMPT = ("(?:\\.|[^"\\])*");',js)
        self.assertIsNotNone(found)
        self.assertEqual(json.loads(found.group(1)),value)
        self.assertIn('const PROMPT_VERSION = "sfs-operator-de-verbatim-v1";',js)

    def test_request_code_unchanged_except_only_prompt(self):
        original=inspect.getsource(v2.call_with_v2_prompt).strip()
        changed=inspect.getsource(ab.call_with_user_prompt).strip()
        reverted=changed.replace("def call_with_user_prompt(row):","def call_with_v2_prompt(row):").replace("USER_SYSTEM_PROMPT","V2_SYSTEM_PROMPT")
        self.assertEqual(reverted,original)

    def test_new_prompt_same_inference_schema(self):
        requests=[]
        def fake_open(req, timeout):
            requests.append(json.loads(req.data))
            resp={"choices":[{"message":{"content":'{"label":"question"}'}}]}
            return io.BytesIO(json.dumps(resp).encode())
        with patch.object(v2.urllib.request, "urlopen", side_effect=fake_open):
            prediction,error,output_hash,latency=ab.call_with_user_prompt(
                {"title":"Help please","body":"How do I configure this library?"})
        self.assertEqual(prediction,"question")
        self.assertIsNone(error)
        self.assertTrue(output_hash)
        payload=requests[0]
        self.assertEqual(payload["temperature"],0)
        self.assertEqual(payload["max_tokens"],56)
        self.assertEqual(payload["messages"][0]["content"],ab.USER_SYSTEM_PROMPT)
        self.assertEqual(payload["response_format"]["json_schema"]["schema"],v1.JSON_SCHEMA)

    def test_pairwise_mcnemar(self):
        values=ab.exact_mcnemar(["bug","feature","question"],
                                ["feature","feature","feature"],
                                ["bug","feature","feature"])
        self.assertEqual(values["improvements"],1)
        self.assertEqual(values["regressions"],0)
        self.assertEqual(values["exact_p_two_sided"],1.0)


if __name__=="__main__":
    unittest.main()
