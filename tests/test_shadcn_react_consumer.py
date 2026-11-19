"""Opt-in source contract for actual shadcn-generated React/Radix example."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples" / "syntyr-shadcn-react"


class ShadcnReactConsumer(unittest.TestCase):
    def test_generated_react_component_and_syntyr_dependency(self):
        package = json.loads((DEMO / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(package["dependencies"]["@syntyr/css"], "file:../..")
        self.assertIn("react", package["dependencies"])
        self.assertIn("vite", package["devDependencies"])
        # CLI tooling is for generation, not a shipped app dependency.
        self.assertNotIn("shadcn", package["dependencies"])
        self.assertNotIn("eslint", package["devDependencies"])
        self.assertNotIn('shadcn/tailwind.css', (DEMO / "src/index.css").read_text())
        config = json.loads((DEMO / "components.json").read_text(encoding="utf-8"))
        self.assertTrue(config["tailwind"]["cssVariables"])
        self.assertTrue(config["tsx"])
        button = (DEMO / "src/components/ui/button.tsx").read_text(encoding="utf-8")
        self.assertIn('data-slot="button"', button)
        self.assertIn("Slot", button)

    def test_scoped_theme_and_portal_compatibility(self):
        css = (DEMO / "src/index.css").read_text(encoding="utf-8")
        self.assertIn('@import "@syntyr/css/core.css";', css)
        self.assertIn('@import "@syntyr/css/shadcn.css";', css)
        src = (DEMO / "src/App.tsx").read_text(encoding="utf-8")
        self.assertIn("syn-root syn-shadcn", src)
        self.assertIn('data-syn-theme="noir"', src)
        self.assertIn("<Button", src)
        self.assertIn("asChild", src)
        self.assertTrue((DEMO / "README.md").is_file())


if __name__ == "__main__":
    unittest.main()
