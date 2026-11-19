import json
import os
import types
import unittest

import run as experiment_run


class TestExperimentEvidenceSchema(unittest.TestCase):
    def setUp(self) -> None:
        # Ensure a clean evidence directory under /evidence for testing
        self.evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
        os.makedirs(self.evidence_dir, exist_ok=True)
        self.evidence_path = os.path.join(self.evidence_dir, "results.json")
        if os.path.exists(self.evidence_path):
            os.remove(self.evidence_path)

    def test_run_creates_valid_evidence_file(self):
        # Run the experiment main entry point
        self.assertTrue(isinstance(experiment_run.main, types.FunctionType))
        experiment_run.main()

        # Evidence file must exist
        self.assertTrue(os.path.exists(self.evidence_path))

        with open(self.evidence_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Top-level keys
        self.assertIn("chapter", data)
        self.assertIn("experiment_id", data)
        self.assertIn("environment", data)
        self.assertIn("runs", data)

        self.assertEqual(data["chapter"], 6)
        self.assertEqual(
            data["experiment_id"],
            "ch6-metrics-that-matter-ai-risk-indicators-v1",
        )

        env = data["environment"]
        self.assertIsInstance(env, dict)
        self.assertIn("os", env)
        self.assertIn("python", env)

        runs = data["runs"]
        self.assertIsInstance(runs, list)
        self.assertGreater(len(runs), 0)

        # Check that we have at least one baseline and one treatment run per workload
        variants_by_workload = {}
        for r in runs:
            self.assertIn("variant", r)
            self.assertIn("workload_id", r)
            self.assertIn("run_id", r)
            self.assertIn("success", r)
            self.assertIn("metrics", r)

            self.assertIn(r["variant"], ("baseline", "treatment"))
            self.assertIsInstance(r["run_id"], str)
            self.assertIsInstance(r["workload_id"], str)
            self.assertIsInstance(r["success"], bool)

            # Metrics must be a mapping with only numeric values
            metrics = r["metrics"]
            self.assertIsInstance(metrics, dict)
            self.assertGreaterEqual(len(metrics), 1)
            for key, value in metrics.items():
                self.assertIsInstance(key, str)
                # JSON numbers come back as int or float
                self.assertIsInstance(value, (int, float))

            wl = r["workload_id"]
            variants_by_workload.setdefault(wl, set()).add(r["variant"])

        for wl, variants in variants_by_workload.items():
            self.assertIn("baseline", variants, msg=f"Missing baseline for {wl}")
            self.assertIn("treatment", variants, msg=f"Missing treatment for {wl}")


if __name__ == "__main__":
    unittest.main()
