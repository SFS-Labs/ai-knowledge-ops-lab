"""Contract test: only the system prompt differs from Qwen's frozen best German control."""
import io
import inspect
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/"showcases/internal-service-intake/evaluation"))
import nlbse_promptlab_taxonomy_ab as exp
import nlbse_questionmark_ab as original
import nlbse_llm_eval as v1

class MCPQwenPromptContract(unittest.TestCase):
    def test_mcp_taxonomy_rules_are_in_system_prompt(self):
        self.assertEqual(exp.TAXONOMY["version"],"2.0")
        self.assertEqual(set(exp.TAXONOMY["classes"]),set(v1.LABELS))
        for label,definition in exp.TAXONOMY["classes"].items():
            self.assertIn(f"{label}: {definition}",exp.PROMPTLAB_SYSTEM_PROMPT)
        for rule in exp.TAXONOMY["rules"]:
            self.assertIn(rule,exp.PROMPTLAB_SYSTEM_PROMPT)
        self.assertIn("A question mark or technical vocabulary alone is not decisive.",exp.PROMPTLAB_SYSTEM_PROMPT)
        self.assertIn('exactly the field "label"',exp.PROMPTLAB_SYSTEM_PROMPT)
        self.assertNotEqual(exp.PROMPTLAB_SYSTEM_PROMPT,original.QUESTIONMARK_PROMPT)

    def test_identical_request_code_except_prompt_name_and_function_name(self):
        a=inspect.getsource(original.call_with_questionmark_prompt).strip()
        b=inspect.getsource(exp.call_with_promptlab_prompt).strip()
        back=b.replace("def call_with_promptlab_prompt(row):","def call_with_questionmark_prompt(row):").replace("PROMPTLAB_SYSTEM_PROMPT","QUESTIONMARK_PROMPT")
        self.assertEqual(back,a)

    def test_both_variants_share_request_content_schema_and_decoding(self):
        submitted=[]
        def fake_urlopen(req, timeout):
            submitted.append(json.loads(req.data))
            return io.BytesIO(json.dumps({"choices":[{"message":{"content":'{"label":"feature"}'}}]}).encode())
        with patch.object(exp.urllib.request,"urlopen",side_effect=fake_urlopen):
            a=original.call_with_questionmark_prompt({"title":"More output?","body":"Can you add JSONL?"})
            b=exp.call_with_promptlab_prompt({"title":"More output?","body":"Can you add JSONL?"})
        self.assertEqual(a[0],"feature");self.assertEqual(b[0],"feature")
        self.assertEqual(len(submitted),2)
        self.assertEqual(submitted[0]["messages"][1],submitted[1]["messages"][1])
        for key in ("temperature","max_tokens","stream","response_format"):
            self.assertEqual(submitted[0][key],submitted[1][key])
        self.assertEqual(submitted[1]["messages"][0]["content"],exp.PROMPTLAB_SYSTEM_PROMPT)
        self.assertEqual(submitted[0]["messages"][0]["content"],original.QUESTIONMARK_PROMPT)
        self.assertEqual(submitted[0]["response_format"]["json_schema"]["schema"],v1.JSON_SCHEMA)
        self.assertEqual(submitted[0]["temperature"],0)
        self.assertEqual(submitted[0]["max_tokens"],56)

if __name__=="__main__":
    unittest.main()
