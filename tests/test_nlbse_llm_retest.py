"""Bounded retest design tests; synthetic fixtures are NOT benchmark results."""
import csv
import importlib.util
from io import StringIO
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[1]/"showcases/internal-service-intake/evaluation"
sys.path.insert(0,str(ROOT))
import nlbse_llm_retest as candidate

class RetestProtocolTests(unittest.TestCase):
    @staticmethod
    def payload(rows):
        buf=StringIO()
        writer=csv.DictWriter(buf,fieldnames=["id","labels","title","body"])
        writer.writeheader()
        writer.writerows(rows)
        return buf.getvalue().encode()

    def test_disjoint_balanced_development_and_blind_holdout(self):
        rows=[{"id":f"{label}-{i}","labels":label,"title":"Synthetic example","body":"test"}
              for label in candidate.v1.LABELS for i in range(7)]
        rows += [{"id":"dup","labels":"bug","title":"A","body":"B"},
                 {"id":"dup","labels":"question","title":"C","body":"D"}]
        with patch.object(candidate.v1,"select_cases",return_value=[{"id":"feature-0"}]):
            dev,test=candidate.disjoint_samples(self.payload(rows),dev_per_class=2,test_per_class=3)
        self.assertEqual(8,len(dev))
        self.assertEqual(12,len(test))
        self.assertEqual(20,len(set(x["id"] for x in dev+test)))
        self.assertNotIn("feature-0", {x["id"] for x in dev+test})
        self.assertNotIn("dup", {x["id"] for x in dev+test})
        for cls in candidate.v1.LABELS:
            self.assertEqual(2,sum(x["label"]==cls for x in dev))
            self.assertEqual(3,sum(x["label"]==cls for x in test))
        with patch.object(candidate.v1,"select_cases",return_value=[{"id":"feature-0"}]):
            dev2,test2=candidate.disjoint_samples(self.payload(rows),dev_per_class=2,test_per_class=3)
        self.assertEqual((dev,test),(dev2,test2))

    def test_prompt_freeze_and_separate_metric_selection(self):
        self.assertEqual(8,candidate.DEV_PER_CLASS)
        self.assertEqual(24,candidate.TEST_PER_CLASS)
        self.assertIn("without reporting a concrete defect",candidate.V2_SYSTEM_PROMPT.lower())
        self.assertIn("README",candidate.V2_SYSTEM_PROMPT)
        self.assertIn("v2",candidate.V2_PROMPT_VERSION)
        self.assertNotEqual(candidate.V2_SYSTEM_PROMPT,candidate.v1.SYSTEM_PROMPT)
        self.assertEqual(96,4*candidate.TEST_PER_CLASS)

    def test_different_seed_from_first_diagnostic(self):
        self.assertNotEqual(candidate.SEED,candidate.v1.SEED)
        self.assertIn("BLIND",candidate.SEED)

if __name__=="__main__":
    unittest.main()
