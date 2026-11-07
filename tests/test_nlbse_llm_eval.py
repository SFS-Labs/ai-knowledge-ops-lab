"""Deterministic contract tests; never represent these fixtures as real LLM evaluation."""
import csv
import importlib.util
import io
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

BASE = Path(__file__).resolve().parents[1] / "showcases/internal-service-intake/evaluation"
sys.path.insert(0,str(BASE))
spec=importlib.util.spec_from_file_location("nlbse_llm_eval",BASE/"nlbse_llm_eval.py")
runner=importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)

class PairedDiagnosticTests(unittest.TestCase):
    def csv_bytes(self, rows):
        s=io.StringIO()
        w=csv.DictWriter(s,fieldnames=["id","labels","title","body"])
        w.writeheader()
        w.writerows(rows)
        return s.getvalue().encode()

    def test_precommitted_class_balance_and_duplicate_exclusion(self):
        rows=[]
        for label in runner.LABELS:
            for i in range(4):
                rows.append({"id":label+str(i), "labels":label,
                             "title":"A synthetic test issue", "body":label+" example"})
        rows += [{"id":"duplicate","labels":"bug","title":"A","body":"B"},
                 {"id":"duplicate","labels":"feature","title":"A","body":"B"}]
        payload=self.csv_bytes(rows)
        first=runner.select_cases(payload, per_class=3)
        second=runner.select_cases(payload, per_class=3)
        self.assertEqual(first,second)
        self.assertEqual(12,len(first))
        self.assertEqual({3}, {sum(x["label"]==k for x in first) for k in runner.LABELS})
        self.assertNotIn("duplicate",[r["id"] for r in first])

    def test_micro_and_macro_count_invalid_as_wrong(self):
        gold=["bug","feature","question","documentation"]
        pred=["bug","bug","question","__invalid__"]
        score=runner.scores(gold,pred)
        self.assertEqual(.5, score["accuracy"])
        self.assertEqual(1, score["confusion"]["documentation"]["__invalid__"])
        self.assertEqual(0,score["by_class"]["documentation"]["recall"])
        self.assertEqual(1.0,runner.scores(gold,gold)["macro_f1"])

    def test_paired_bootstrap_is_deterministic(self):
        gold=list(runner.LABELS)*3
        baseline=["feature"]*12
        observed=list(gold)
        self.assertEqual(runner.paired_bootstrap_accuracy(gold,baseline,observed),
                         runner.paired_bootstrap_accuracy(gold,baseline,observed))

    def test_invalid_and_missing_fields_rejected(self):
        with self.assertRaises(ValueError):
            runner.select_cases(self.csv_bytes([{"id":"1","labels":"nope",
                                                  "title":"x","body":"y"}]),per_class=1)
        with self.assertRaises(ValueError):
            runner.scores(["bug"],[])

    def test_prompt_source_text_is_data_not_instructions(self):
        self.assertIn("untrusted DATA",runner.SYSTEM_PROMPT)
        self.assertEqual("nlbse-issue-type-v1",runner.PROMPT_VERSION)
        self.assertEqual(24,runner.PER_CLASS)
        self.assertEqual(96,runner.PER_CLASS*len(runner.LABELS))
        self.assertIn("2026-11-08",runner.SEED)

if __name__=="__main__":
    unittest.main()
