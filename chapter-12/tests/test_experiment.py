import json
import os
import shutil
import tempfile
import unittest

import run as experiment_run


class TestExperimentEvidenceSchema(unittest.TestCase):
    def setUp(self) -> None:
        # create a temporary evidence directory
        self.temp_dir = tempfile.mkdtemp()
        os.environ["BOOKMAS_EVIDENCE_DIR"] = self.temp_dir

    def tearDown(self) -> None:
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        if "BOOKMAS_EVIDENCE_DIR" in os.environ:
            del os.environ["BOOKMAS_EVIDENCE_DIR"]

    def test_run_and_schema(self) -> None:
        # Execute the experiment main entrypoint
        experiment_run.main()

        evidence_path = os.path.join(self.temp_dir, "results.json")
        self.assertTrue(os.path.exists(evidence_path), "results.json must be created")

        with open(evidence_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Top-level keys
        self.assertIn("chapter", data)
        self.assertIn("experiment_id", data)
        self.assertIn("environment", data)
        self.assertIn("runs", data)

        # Check fixed values
        self.assertEqual(data["chapter"], 12)
        self.assertEqual(data["experiment_id"], "exp-12-model-validation-reimagined-v1")

        # Environment schema
        env = data["environment"]
        self.assertIsInstance(env.get("os"), str)
        self.assertIsInstance(env.get("python"), str)

        runs = data["runs"]
        self.assertIsInstance(runs, list)
        self.assertGreaterEqual(len(runs), 4)

        # Track workload/variant presence
        seen = {}

        for run in runs:
            self.assertIn("variant", run)
            self.assertIn("workload_id", run)
            self.assertIn("run_id", run)
            self.assertIn("success", run)
            self.assertIn("metrics", run)

            variant = run["variant"]
            workload_id = run["workload_id"]
            self.assertIn(variant, ("baseline", "treatment"))

            key = (workload_id, variant)
            seen[key] = True

            # success is boolean
            self.assertIsInstance(run["success"], bool)

            # metrics must be a dict of numeric values only
            metrics = run["metrics"]
            self.assertIsInstance(metrics, dict)
            self.assertGreater(len(metrics), 0)
            for mname, mval in metrics.items():
                self.assertIsInstance(mname, str)
                # metrics must be numbers, not bool (bool is subclass of int, so check explicitly)
                self.assertFalse(isinstance(mval, bool), f"Metric {mname} must not be bool")
                self.assertIsInstance(mval, (int, float), f"Metric {mname} must be numeric")

        # Ensure at least one baseline and treatment run per workload
        workloads = set(w for w, _ in seen.keys())
        for workload in workloads:
            self.assertIn((workload, "baseline"), seen)
            self.assertIn((workload, "treatment"), seen)


if __name__ == "__main__":
    unittest.main()
