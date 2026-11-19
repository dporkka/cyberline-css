"""Optional distribution-compatible starters for designer/developer onboarding."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AdoptionStarterContract(unittest.TestCase):
    def test_tailwind_starter_uses_explicit_opt_in_package_exports(self):
        base = ROOT / "examples/tailwind-v4"
        pkg = json.loads((base / "package.json").read_text())
        self.assertIn("@tailwindcss/cli", pkg["devDependencies"])
        self.assertIn("tailwindcss", pkg["devDependencies"])
        self.assertEqual(pkg["dependencies"]["@syntyr/css"], "file:../..")
        css = (base / "src/app.css").read_text()
        self.assertIn('@import "tailwindcss";', css)
        self.assertIn('@import "@syntyr/css/core.css";', css)
        self.assertIn('@import "@syntyr/css/tailwind.css";', css)
        self.assertIn("bg-syntyr-surface", (base / "index.html").read_text())
        self.assertIn('data-syn-theme="grid"', (base / "index.html").read_text())
        self.assertIn("build", pkg["scripts"])
        self.assertTrue((base / "README.md").is_file())

    def test_astro_starter_preserves_static_html_no_app_javascript(self):
        base = ROOT / "examples/astro"
        pkg = json.loads((base / "package.json").read_text())
        self.assertEqual(pkg["dependencies"]["@syntyr/css"], "file:../..")
        self.assertIn("astro", pkg["dependencies"])
        self.assertIn("build", pkg["scripts"])
        page = (base / "src/pages/index.astro").read_text()
        self.assertIn("@syntyr/css/core.css", page)
        self.assertIn("syn-root", page)
        self.assertIn("syn-button", page)
        self.assertNotIn("<script", page.lower())
        self.assertTrue((base / "README.md").is_file())

    def test_examples_do_not_expand_root_runtime_dependencies(self):
        pkg = json.loads((ROOT / "package.json").read_text())
        for name in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
            self.assertNotIn(name, pkg)


if __name__ == "__main__":
    unittest.main()
