"""Unit contract: the A/B only changes the emitted JSON field name."""
import io
import inspect
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

EVAL = Path(__file__).resolve().parents[1] / "showcases/internal-service-intake/evaluation"
sys.path.insert(0, str(EVAL))
import nlbse_issue_type_ab as ab
import nlbse_llm_retest as v2


class IssueTypeABTests(unittest.TestCase):
    def test_prompt_diff_is_exactly_field_name(self):
        self.assertEqual(ab.ISSUE_TYPE_SYSTEM_PROMPT,
                         v2.V2_SYSTEM_PROMPT.replace("single key named label", "single key named issue_type"))
        self.assertNotEqual(ab.ISSUE_TYPE_SYSTEM_PROMPT, v2.V2_SYSTEM_PROMPT)
        self.assertEqual(ab.ISSUE_TYPE_SCHEMA["required"], ["issue_type"])
        self.assertEqual(set(ab.ISSUE_TYPE_SCHEMA["properties"]), {"issue_type"})
        self.assertEqual(set(ab.ISSUE_TYPE_SCHEMA["properties"]["issue_type"]["enum"]), set(ab.v1.LABELS))

    def test_inference_functions_are_exact_copies_excluding_four_field_edits(self):
        original = inspect.getsource(v2.call_with_v2_prompt)
        altered = inspect.getsource(ab.call_with_issue_type)
        recovered = (altered.replace("def call_with_issue_type(row):", "def call_with_v2_prompt(row):")
                     .replace("ISSUE_TYPE_SYSTEM_PROMPT", "V2_SYSTEM_PROMPT")
                     .replace('"schema":ISSUE_TYPE_SCHEMA', '"schema":v1.JSON_SCHEMA')
                     .replace('parsed.get("issue_type")', 'parsed.get("label")')
                     .replace('set(parsed)=={"issue_type"}', 'set(parsed)=={"label"}'))
        self.assertEqual(original.strip(), recovered.strip())

    def test_inference_accepts_only_issue_type_and_valid_labels(self):
        records = []
        def fake_open(req, timeout):
            records.append(json.loads(req.data))
            body = {"choices":[{"message":{"content":'{"issue_type":"question"}'}}]}
            return io.BytesIO(json.dumps(body).encode())
        row={"title":"Install this?", "body":"How do I configure the application?"}
        with patch.object(v2.urllib.request,"urlopen",side_effect=fake_open):
            pred,error,digest,latency = ab.call_with_issue_type(row)
        self.assertEqual(("question",None),(pred,error))
        self.assertIsInstance(digest,str)
        self.assertEqual(records[0]["temperature"],0)
        self.assertEqual(records[0]["max_tokens"],56)
        self.assertEqual(records[0]["response_format"]["json_schema"]["schema"], ab.ISSUE_TYPE_SCHEMA)
        self.assertEqual(records[0]["messages"][0]["content"],ab.ISSUE_TYPE_SYSTEM_PROMPT)

    def test_exact_discordant_pair_logic(self):
        gold=["bug","feature","question"]
        a=["question","feature","bug"]
        b=["bug","feature","bug"]
        out=ab.exact_mcnemar(gold,a,b)
        self.assertEqual(out["improved"],1)
        self.assertEqual(out["worsened"],0)
        self.assertEqual(out["pvalue_two_sided_exact"],1.0)


if __name__=="__main__":
    unittest.main()
