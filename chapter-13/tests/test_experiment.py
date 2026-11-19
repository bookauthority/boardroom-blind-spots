import json
import os
import shutil
import tempfile
import unittest


class ExperimentSchemaTest(unittest.TestCase):
    def setUp(self) -> None:
        # Create a temporary evidence directory
        self.tmpdir = tempfile.mkdtemp(prefix="evidence_")
        self.addCleanup(lambda: shutil.rmtree(self.tmpdir, ignore_errors=True))

    def _run_experiment(self) -> str:
        # Set environment variable so run.py writes into our temp dir
        os.environ["BOOKMAS_EVIDENCE_DIR"] = self.tmpdir

        # Import run.py as a module and invoke main()
        import importlib

        run_module = importlib.import_module("run")
        # Reload in case of stateful environments
        importlib.reload(run_module)
        run_module.main()

        evidence_path = os.path.join(self.tmpdir, "results.json")
        self.assertTrue(os.path.exists(evidence_path), "results.json not created")
        return evidence_path

    def test_evidence_schema_and_metrics(self) -> None:
        evidence_path = self._run_experiment()

        with open(evidence_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # Top-level keys
        self.assertIn("chapter", data)
        self.assertIn("experiment_id", data)
        self.assertIn("environment", data)
        self.assertIn("runs", data)

        self.assertEqual(data["chapter"], 13)
        self.assertEqual(
            data["experiment_id"], "chap13-crisis-mgmt-ai-failure-war-game-v1"
        )

        env = data["environment"]
        self.assertIsInstance(env, dict)
        self.assertIn("os", env)
        self.assertIn("python", env)

        runs = data["runs"]
        self.assertIsInstance(runs, list)
        self.assertGreaterEqual(len(runs), 6)  # 3 workloads x 2 variants

        # Track presence of variants per workload
        by_workload = {}
        for run in runs:
            self.assertIn("variant", run)
            self.assertIn("workload_id", run)
            self.assertIn("run_id", run)
            self.assertIn("success", run)
            self.assertIn("metrics", run)

            variant = run["variant"]
            workload_id = run["workload_id"]
            self.assertIn(variant, {"baseline", "treatment"})
            self.assertIsInstance(workload_id, str)

            # success is boolean
            self.assertIsInstance(run["success"], bool)

            metrics = run["metrics"]
            self.assertIsInstance(metrics, dict)
            # Required metric
            self.assertIn("time_to_decisive_containment_action", metrics)
            ttca = metrics["time_to_decisive_containment_action"]
            self.assertIsInstance(ttca, (int, float))

            by_workload.setdefault(workload_id, set()).add(variant)

        # Ensure each workload has both baseline and treatment
        for workload_id, variants in by_workload.items():
            self.assertIn("baseline", variants, f"No baseline run for {workload_id}")
            self.assertIn("treatment", variants, f"No treatment run for {workload_id}")

    def test_metrics_are_numeric_only(self) -> None:
        evidence_path = self._run_experiment()
        with open(evidence_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        for run in data["runs"]:
            metrics = run.get("metrics", {})
            for key, value in metrics.items():
                # All metric values must be finite JSON numbers (int or float)
                self.assertIsInstance(
                    value,
                    (int, float),
                    msg=f"Metric {key} must be numeric, got {type(value)}",
                )


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
