import json
import os
import sys
import types
import unittest


class TestExperimentEvidenceSchema(unittest.TestCase):
    def setUp(self) -> None:
        # Ensure /evidence exists
        self.evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
        os.makedirs(self.evidence_dir, exist_ok=True)

        # Import run as module and execute main
        if "run" in sys.modules:
            # Force reload to avoid caching side effects between tests
            import importlib

            importlib.reload(sys.modules["run"])
        else:
            __import__("run")

        run_module = sys.modules["run"]
        self.assertIsInstance(run_module, types.ModuleType)

        # Execute main to produce evidence
        run_module.main()

        # Load evidence
        evidence_path = os.path.join(self.evidence_dir, "results.json")
        self.assertTrue(os.path.exists(evidence_path), "Evidence file not created at /evidence/results.json")
        with open(evidence_path, "r", encoding="utf-8") as f:
            self.evidence = json.load(f)

    def test_top_level_structure(self):
        ev = self.evidence
        self.assertIn("chapter", ev)
        self.assertEqual(ev["chapter"], 7)
        self.assertIn("experiment_id", ev)
        self.assertEqual(ev["experiment_id"], "ch7-scenario-ai-model-collapse-stresstest-v1")
        self.assertIn("environment", ev)
        self.assertIsInstance(ev["environment"], dict)
        self.assertIn("os", ev["environment"])
        self.assertIn("python", ev["environment"])
        self.assertIn("runs", ev)
        self.assertIsInstance(ev["runs"], list)

    def test_runs_schema_and_variants(self):
        runs = self.evidence["runs"]
        self.assertGreaterEqual(len(runs), 10, "Expected at least 10 runs (5 workloads * 2 variants)")

        seen = {}
        for r in runs:
            self.assertIn("variant", r)
            self.assertIn(r["variant"], ["baseline", "treatment"])
            self.assertIn("workload_id", r)
            self.assertIsInstance(r["workload_id"], str)
            self.assertIn("run_id", r)
            self.assertIsInstance(r["run_id"], str)
            self.assertIn("success", r)
            self.assertIsInstance(r["success"], bool)
            self.assertIn("metrics", r)
            self.assertIsInstance(r["metrics"], dict)

            key = (r["workload_id"], r["variant"])
            seen[key] = True

            # Metrics must all be numeric scalar values.
            for mname, mval in r["metrics"].items():
                self.assertIsInstance(
                    mval, (int, float), f"Metric {mname} must be numeric for run {r['run_id']}"
                )

        workloads = [
            "W1_micro_level_ai_failure_scenarios",
            "W2_firm_wide_common_cause_ai_failure_scenarios",
            "W3_systemic_ai_feedback_loop_scenarios",
            "W4_reverse_stress_testing_from_ai_perspective",
            "W5_tabletop_exercise_and_communication_outputs",
        ]
        for wid in workloads:
            self.assertIn((wid, "baseline"), seen, f"Missing baseline run for {wid}")
            self.assertIn((wid, "treatment"), seen, f"Missing treatment run for {wid}")

    def test_ai_attributed_loss_non_negative(self):
        for r in self.evidence["runs"]:
            metrics = r["metrics"]
            self.assertIn("ai_attributed_loss", metrics)
            self.assertGreaterEqual(
                metrics["ai_attributed_loss"], 0.0, "ai_attributed_loss must be non-negative"
            )

    def test_import_engine_and_model(self):
        # Basic import tests to ensure modules load and functions exist.
        import experiment.engine as engine
        import experiment.model as model

        self.assertTrue(hasattr(engine, "run_all_workloads"))
        self.assertTrue(callable(engine.run_all_workloads))
        self.assertTrue(hasattr(model, "generate_synthetic_portfolio"))
        self.assertTrue(callable(model.generate_synthetic_portfolio))


if __name__ == "__main__":
    unittest.main()
