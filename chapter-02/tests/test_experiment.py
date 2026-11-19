import json
import os
import unittest


class TestExperimentEvidenceSchema(unittest.TestCase):
    def setUp(self) -> None:
        # Ensure evidence directory exists
        self.evidence_dir = os.path.abspath("evidence_test")
        os.makedirs(self.evidence_dir, exist_ok=True)
        os.environ["BOOKMAS_EVIDENCE_DIR"] = self.evidence_dir

        # Run the experiment
        import run  # type: ignore

        run.main()

        self.results_path = os.path.join(self.evidence_dir, "results.json")
        self.assertTrue(os.path.exists(self.results_path), "results.json not created")
        with open(self.results_path, encoding="utf-8") as f:
            self.results = json.load(f)

    def test_top_level_structure(self) -> None:
        r = self.results
        self.assertIn("chapter", r)
        self.assertIsInstance(r["chapter"], int)
        self.assertEqual(r["chapter"], 2)

        self.assertIn("experiment_id", r)
        self.assertIsInstance(r["experiment_id"], str)
        self.assertEqual(r["experiment_id"], "ch02-ai-attack-surface-mapping-v1")

        self.assertIn("environment", r)
        self.assertIsInstance(r["environment"], dict)
        self.assertIn("os", r["environment"])
        self.assertIn("python", r["environment"])

        self.assertIn("runs", r)
        self.assertIsInstance(r["runs"], list)

    def test_runs_schema_and_variants(self) -> None:
        runs = self.results["runs"]
        self.assertGreaterEqual(len(runs), 6, "Expected at least 6 runs (3 workloads x 2 variants)")

        seen = {}
        for run in runs:
            # Required keys
            self.assertIn("variant", run)
            self.assertIn("workload_id", run)
            self.assertIn("run_id", run)
            self.assertIn("success", run)
            self.assertIn("metrics", run)

            # Types
            self.assertIn(run["variant"], ["baseline", "treatment"])
            self.assertIsInstance(run["workload_id"], str)
            self.assertIsInstance(run["run_id"], str)
            self.assertIsInstance(run["success"], bool)
            self.assertIsInstance(run["metrics"], dict)

            key = (run["workload_id"], run["variant"])
            seen[key] = True

            for mk, mv in run["metrics"].items():
                # Metric values must be plain numbers
                self.assertIsInstance(
                    mv,
                    (int, float),
                    msg=f"Metric {mk} must be numeric, got {type(mv)}",
                )

        # Ensure at least one baseline and one treatment per workload
        workloads = {
            "workload-1-ai-inventory-pipeline",
            "workload-2-decision-chain-and-exposure-mapping",
            "workload-3-concentration-and-materiality-heatmaps",
        }
        for wid in workloads:
            self.assertIn((wid, "baseline"), seen, f"Missing baseline run for {wid}")
            self.assertIn((wid, "treatment"), seen, f"Missing treatment run for {wid}")


if __name__ == "__main__":
    unittest.main()
