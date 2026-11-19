import json
import os
import unittest
import tempfile

import run as experiment_run


class TestExperimentEvidence(unittest.TestCase):
    def setUp(self) -> None:
        # Use a temporary directory for evidence to avoid filesystem issues.
        self.tmpdir = tempfile.TemporaryDirectory()
        os.environ["BOOKMAS_EVIDENCE_DIR"] = self.tmpdir.name

    def tearDown(self) -> None:
        self.tmpdir.cleanup()
        if "BOOKMAS_EVIDENCE_DIR" in os.environ:
            del os.environ["BOOKMAS_EVIDENCE_DIR"]

    def test_run_produces_evidence_file_with_required_schema(self) -> None:
        # Execute main to generate evidence
        experiment_run.main()

        evidence_path = os.path.join(self.tmpdir.name, "results.json")
        self.assertTrue(os.path.exists(evidence_path), "Evidence file not created")

        with open(evidence_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Top-level checks
        self.assertIsInstance(data, dict)
        self.assertEqual(data.get("chapter"), 9)
        self.assertEqual(
            data.get("experiment_id"),
            "exp-09-operational-resilience-ai-ewd-response",
        )
        self.assertIn("environment", data)
        self.assertIsInstance(data["environment"], dict)
        self.assertIn("os", data["environment"])
        self.assertIn("python", data["environment"])

        # Runs list must exist and be non-empty
        runs = data.get("runs")
        self.assertIsInstance(runs, list)
        self.assertGreaterEqual(len(runs), 4)  # 2 workloads x 2 variants

        # Track presence of baseline/treatment per workload
        seen = {}
        for run in runs:
            self.assertIsInstance(run, dict)
            variant = run.get("variant")
            workload_id = run.get("workload_id")
            run_id = run.get("run_id")
            success = run.get("success")

            self.assertIn(variant, {"baseline", "treatment"})
            self.assertIsInstance(workload_id, str)
            self.assertIsInstance(run_id, str)
            self.assertIsInstance(success, bool)

            # metrics schema: dict with only numeric values
            metrics = run.get("metrics")
            self.assertIsInstance(metrics, dict)
            self.assertGreater(len(metrics), 0)
            for k, v in metrics.items():
                self.assertIsInstance(k, str)
                # Must be a JSON number (int or float) only
                self.assertIsInstance(v, (int, float))

            key = (workload_id, variant)
            seen[key] = True

        # Ensure at least one baseline and one treatment run per workload we know about
        for workload_id in ["WL1_normal_operations", "WL3_abrupt_model_corruption"]:
            self.assertIn((workload_id, "baseline"), seen)
            self.assertIn((workload_id, "treatment"), seen)


if __name__ == "__main__":
    unittest.main()
