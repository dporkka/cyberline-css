"""Long-lived public API and packaging invariants for low-entropy Syntyr."""
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build import distributions
from package_release import FILES
from build_cloudflare_site import source_files


class ArchitectureContract(unittest.TestCase):
    def test_optional_utilities_occupy_final_cascade_layer(self):
        expected = (
            "@layer syn.tokens, syn.base, syn.components, syn.semantic, "
            "syn.recipes, syn.geometry, syn.symbols, syn.effects, syn.motion, syn.utilities;"
        )
        self.assertIn(expected, (ROOT / "src/tokens.css").read_text())
        self.assertIn("@layer syn.utilities {", (ROOT / "src/utilities.css").read_text())
        self.assertIn(expected, (ROOT / "dist/syntyr.core.css").read_text())
        self.assertIn("@layer syn.utilities {", (ROOT / "dist/syntyr.utilities.css").read_text())
        self.assertNotIn(".syn-u-", (ROOT / "dist/syntyr.core.css").read_text())

    def test_public_css_artifacts_are_complete_across_distributions(self):
        canonical = set(distributions())
        self.assertEqual(
            {f"dist/{name}" for name in canonical},
            {path for path in FILES if path.startswith("dist/")},
        )
        self.assertIn("ARCHITECTURE.md", FILES)
        public = source_files()
        self.assertIn("ARCHITECTURE.md", public)
        self.assertEqual(
            {f"dist/{name}" for name in canonical},
            {path for path in public if path.startswith("dist/")},
        )

    def test_core_has_no_app_or_integrations_dependency(self):
        for name, paths in distributions().items():
            with self.subTest(name=name):
                self.assertTrue(all((ROOT / "src" / path).is_file() for path in paths))
                self.assertTrue(all(".." not in Path(path).parts for path in paths))
                self.assertTrue(all(not path.startswith("integrations/") for path in paths))
        for source in (ROOT / "src").rglob("*.css"):
            with self.subTest(source=source.name):
                css = source.read_text()
                self.assertNotIn("@import", css)
                self.assertNotIn("url(http", css.lower())


if __name__ == "__main__":
    unittest.main()
