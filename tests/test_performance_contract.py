"""Contracts for an opt-in long-page render optimization and local performance harness."""
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/perf_benchmark.py"


class PerformanceContracts(unittest.TestCase):
    def test_defer_is_opt_in_and_does_not_change_core(self):
        recipes = (ROOT / "src/recipes.css").read_text()
        core = (ROOT / "dist/syntyr.core.css").read_text()
        self.assertIn(".syn-defer-section {", recipes)
        self.assertIn("content-visibility: auto;", recipes)
        self.assertIn("contain-intrinsic-size: auto var(--syn-defer-size, 36rem);", recipes)
        self.assertIn("@media print", recipes)
        self.assertIn("content-visibility: visible;", recipes)
        self.assertNotIn("syn-defer-section", core)

    def test_fixture_covers_both_density_and_below_fold_layout(self):
        self.assertTrue(SCRIPT.exists())
        spec = importlib.util.spec_from_file_location("perf_benchmark", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        html = module.make_fixture("/* test styles */", rows=17, sections=6, deferred=True)
        self.assertIn("/* test styles */", html)
        self.assertEqual(html.count("<tr>"), 17)
        self.assertEqual(html.count('class="syn-defer-section"'), 6)
        self.assertIn('class="syn-root syn-page"', html)
        self.assertNotIn('src="https:', html)
        regular = module.make_fixture("", rows=3, sections=2, deferred=False)
        self.assertNotIn("syn-defer-section", regular)

    def test_each_round_rotates_variant_order_to_reduce_position_bias(self):
        spec = importlib.util.spec_from_file_location("perf_benchmark", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        cases = ["unstyled", "core", "all"]
        self.assertEqual(module.trial_order(cases, 0), cases)
        self.assertEqual(module.trial_order(cases, 1), ["core", "all", "unstyled"])
        self.assertEqual(module.trial_order(cases, 2), ["all", "unstyled", "core"])

    def test_aggregated_benchmarks_use_medians_and_include_context(self):
        spec = importlib.util.spec_from_file_location("perf_benchmark", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        report = module.summarize(
            {"core": [
                {"navigation_ms": 50.0, "theme_toggle_ms": 20.0, "style_recalc_ms": 10.0},
                {"navigation_ms": 10.0, "theme_toggle_ms": 2.0, "style_recalc_ms": 4.0},
                {"navigation_ms": 30.0, "theme_toggle_ms": 8.0, "style_recalc_ms": 6.0},
            ]},
            rows=100, sections=10, runs=3, browser="chromium",
        )
        self.assertEqual(report["results"]["core"]["navigation_ms"], 30.0)
        self.assertEqual(report["results"]["core"]["theme_toggle_ms"], 8.0)
        self.assertEqual(report["fixture"]["rows"], 100)
        self.assertEqual(report["browser"], "chromium")


if __name__ == "__main__":
    unittest.main()
