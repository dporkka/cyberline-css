"""No-JS core and opt-in ESM distribution contracts."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build import js_distributions
from scripts.package_release import FILES
from scripts.build_cloudflare_site import source_files


class ProgressiveJSContract(unittest.TestCase):
    def test_optional_esm_distributions_are_packageable_and_identical_to_source(self):
        js = js_distributions()
        self.assertEqual(js, {
            "syntyr.viz.js": "js/viz.js",
            "syntyr.motion.js": "js/motion.js",
        })
        for output, source in js.items():
            with self.subTest(output=output):
                self.assertEqual((ROOT / "src" / source).read_bytes(),
                                 (ROOT / "dist" / output).read_bytes())
                self.assertIn(f"dist/{output}", FILES)
                self.assertIn(f"dist/{output}", source_files())
                self.assertIn("export function enhance", (ROOT / "dist" / output).read_text())
        for path in ("dist/syntyr.core.css", "dist/syntyr.viz.css"):
            self.assertNotIn("syntyr.viz.js", (ROOT / path).read_text())

    def test_documented_opt_in_and_example(self):
        readme = (ROOT / "README.md").read_text()
        guide = (ROOT / "docs/progressive-js.md").read_text()
        page = (ROOT / "examples/progressive-js.html").read_text()
        self.assertIn("syntyr.viz.js", readme)
        self.assertIn("syntyr.motion.js", guide)
        self.assertIn("destroy()", guide)
        self.assertIn("refresh()", guide)
        self.assertIn('type="module"', page)
        self.assertIn("data-syn-point", page)
        self.assertIn("<table", page)

    def test_modules_remain_optional_and_independent(self):
        viz = (ROOT / "dist/syntyr.viz.js").read_text()
        motion = (ROOT / "dist/syntyr.motion.js").read_text()
        self.assertNotIn("import ", viz)
        self.assertNotIn("import ", motion)
        self.assertNotIn("new MutationObserver(", viz)
        self.assertNotIn("new MutationObserver(", motion)
        self.assertIn("export function enhanceViz(root)", viz)
        self.assertIn("export function enhanceMotion(root)", motion)
        self.assertIn("destroy()", viz)
        self.assertIn("destroy()", motion)


if __name__ == "__main__":
    unittest.main()
