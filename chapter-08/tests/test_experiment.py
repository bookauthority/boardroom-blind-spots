import json
import os
import unittest


class TestExperimentEvidence(unittest.TestCase):
    def setUp(self) -> None:
        # Ensure evidence exists by running run.py if needed
        self.evidence_dir = os.environ.get("BOOKMAS_EVIDENCE_DIR", "/evidence")
        os.makedirs(self.evidence_dir, exist_ok=True)
        self.evidence_path = os.path.join(self.evidence_dir, "results.json")
        if not os.path.exists(self.evidence_path):
            import run  # noqa: F401  # triggers main when executed as script
            # Directly call main rather than relying on import side effects
            run.main()  # type: ignore[attr-defined]

        with open(self.evidence_path, "r", encoding="utf-8") as f:
            self.evidence = json.load(f)

    def test_top_level_schema(self) -> None:
        ev = self.evidence
        self.assertIsInstance(ev, dict)
        self.assertIn("chapter", ev)
        self.assertEqual(ev["chapter"], 8)
        self.assertIn("experiment_id", ev)
        self.assertEqual(
            ev["experiment_id"],
            "exp-8-guardrails-controls-training-deployment-autonomy",
        )
        self.assertIn("environment", ev)
        self.assertIsInstance(ev["environment"], dict)
        self.assertIn("os", ev["environment"])
        self.assertIn("python", ev["environment"])
        self.assertIn("runs", ev)
        self.assertIsInstance(ev["runs"], list)

    def test_runs_have_required_fields_and_numeric_metrics(self) -> None:
        runs = self.evidence["runs"]
        self.assertGreaterEqual(len(runs), 10)  # 5 workloads * 2 variants

        variants_by_workload = {}
        for run in runs:
            self.assertIn("variant", run)
            self.assertIn(run["variant"], ("baseline", "treatment"))
            self.assertIn("workload_id", run)
            self.assertIn("run_id", run)
            self.assertIsInstance(run["success"], bool)
            self.assertIn("metrics", run)
            self.assertIsInstance(run["metrics"], dict)

            # All metric values must be numeric
            for key, value in run["metrics"].items():
                self.assertIsInstance(
                    value,
                    (int, float),
                    msg=f"Metric {key} must be numeric, got {type(value)}",
                )

            wid = run["workload_id"]
            variants_by_workload.setdefault(wid, set()).add(run["variant"])

        # Ensure at least one baseline and one treatment run per workload
        expected_workloads = {
            "WL1_normal_traffic",
            "WL2_data_drift_and_model_stress",
            "WL3_policy_violation_and_misuse_attempts",
            "WL4_adverse_event_and_feedback_loop_spike",
            "WL5_kill_switch_operational_test",
        }
        self.assertEqual(set(variants_by_workload.keys()), expected_workloads)
        for wid, variants in variants_by_workload.items():
            self.assertIn("baseline", variants, msg=f"Missing baseline for {wid}")
            self.assertIn("treatment", variants, msg=f"Missing treatment for {wid}")


if __name__ == "__main__":  # pragma: no cover
    unittest.main()
