import json
import os
import unittest
from pathlib import Path


class TestExperimentEvidenceSchema(unittest.TestCase):
    def setUp(self) -> None:
        # Ensure evidence directory exists and run the experiment
        self.evidence_dir = Path("/evidence")
        self.evidence_dir.mkdir(parents=True, exist_ok=True)

        # Remove any pre-existing results.json to avoid stale data
        results_file = self.evidence_dir / "results.json"
        if results_file.exists():
            results_file.unlink()

        os.environ["BOOKMAS_EVIDENCE_DIR"] = str(self.evidence_dir)

        # Import and run the experiment entrypoint
        import run as experiment_run  # type: ignore

        experiment_run.main()

    def test_results_file_exists(self) -> None:
        results_file = self.evidence_dir / "results.json"
        self.assertTrue(results_file.exists(), "results.json should be created")

    def test_evidence_schema_and_metrics(self) -> None:
        results_file = self.evidence_dir / "results.json"
        with results_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

        # Top-level required keys
        self.assertIn("chapter", data)
        self.assertIn("experiment_id", data)
        self.assertIn("environment", data)
        self.assertIn("runs", data)

        self.assertEqual(data["chapter"], 14)
        self.assertEqual(data["experiment_id"], "exp-ch14-boardroom-toolkits-v1")

        # Environment shape
        env = data["environment"]
        self.assertIn("os", env)
        self.assertIn("python", env)
        self.assertIsInstance(env["os"], str)
        self.assertIsInstance(env["python"], str)

        # Runs validation
        runs = data["runs"]
        self.assertIsInstance(runs, list)
        self.assertGreaterEqual(len(runs), 6)  # at least 2 per workload * 3 workloads

        # Track workloads seen per variant
        workloads_by_variant = {"baseline": set(), "treatment": set()}

        for run in runs:
            self.assertIn("variant", run)
            self.assertIn(run["variant"], ["baseline", "treatment"])
            self.assertIn("workload_id", run)
            self.assertIn("run_id", run)
            self.assertIn("success", run)
            self.assertIn("metrics", run)

            workloads_by_variant[run["variant"].lower()].add(run["workload_id"])

            # success should be boolean
            self.assertIsInstance(run["success"], bool)

            metrics = run["metrics"]
            self.assertIsInstance(metrics, dict)
            # Ensure at least one numeric metric
            self.assertGreaterEqual(len(metrics), 1)
            for key, value in metrics.items():
                # Metric values MUST be numbers (no strings, lists, dicts, None)
                self.assertIsInstance(
                    value,
                    (int, float),
                    msg=f"Metric {key} should be numeric, got {type(value)}",
                )

        # Verify that for each workload we have both baseline and treatment runs
        expected_workloads = {
            "W1-universal-bank-quarterly-pack",
            "W2-digital-bank-monthly-ops-review",
            "W3-asset-manager-annual-board-strategy",
        }

        self.assertTrue(
            expected_workloads.issubset(workloads_by_variant["baseline"]),
            "Each workload should have at least one baseline run",
        )
        self.assertTrue(
            expected_workloads.issubset(workloads_by_variant["treatment"]),
            "Each workload should have at least one treatment run",
        )


if __name__ == "__main__":
    unittest.main()
