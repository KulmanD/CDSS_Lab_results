import unittest
from pathlib import Path

from evaluation import run_evaluation


class EvaluationTests(unittest.TestCase):
    def test_mvp_evaluation_dataset_matches_expected_outcomes(self):
        summary = run_evaluation(Path("../data/evaluation/mvp_cases.json"))

        self.assertEqual(summary["cases"], 25)
        self.assertEqual(summary["case_accuracy"], 1.0)
        self.assertEqual(summary["urgency_accuracy"], 1.0)
        self.assertEqual(summary["failures"], [])
        for metrics in summary["per_rule"].values():
            self.assertEqual(metrics["precision"], 1.0)
            self.assertEqual(metrics["recall"], 1.0)
            self.assertEqual(metrics["f1"], 1.0)


if __name__ == "__main__":
    unittest.main()
