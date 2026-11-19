"""Syntyr DX artifacts are generated, scoped, and optional."""
from pathlib import Path
import json
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]

class DeveloperExperienceTests(unittest.TestCase):
    def test_editor_metadata_is_current_and_machine_readable(self):
        result = subprocess.run(
            [sys.executable, "scripts/export_api_metadata.py", "--check"],
            cwd=ROOT, capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        api = json.loads((ROOT / "metadata/syntyr-api.json").read_text())
        self.assertIn("syn-button", [item["name"] for item in api["classes"]])
        self.assertIn("--syn-accent", [item["name"] for item in api["tokens"]])
        self.assertIn("syn-u-flex", [item["name"] for item in api["classes"]])
        self.assertIn("grid", api["themes"])
        self.assertIn("auto", api["themes"])
        self.assertEqual(len(api["classes"]), len(set(c["name"] for c in api["classes"])))
        self.assertEqual(len(api["tokens"]), len(set(c["name"] for c in api["tokens"])))
        html = json.loads((ROOT / "metadata/syntyr.html-custom-data.json").read_text())
        css = json.loads((ROOT / "metadata/syntyr.css-custom-data.json").read_text())
        self.assertEqual(html["version"], 1.1)
        self.assertEqual(css["version"], 1.1)
        self.assertIn("data-syn-theme", [a["name"] for a in html["globalAttributes"]])
        self.assertIn("--syn-accent", [p["name"] for p in css["properties"]])
        snippets = json.loads((ROOT / "metadata/syntyr.code-snippets").read_text())
        self.assertTrue(any("syn-button" in k for k in snippets))

    def test_editor_metadata_attributes_defining_source_modules(self):
        from scripts.export_api_metadata import collect
        classes = {entry["name"]: entry["module"] for entry in collect()["classes"]}
        self.assertEqual(classes["syn-app-shell"], "recipes.css")
        self.assertEqual(classes["syn-terminal"], "recipes.css")
        self.assertEqual(classes["syn-page"], "base.css")
        self.assertEqual(classes["syn-root"], "base.css")
        self.assertEqual(classes["syn-button"], "components/buttons.css")
        tokens = {entry["name"]: entry["module"] for entry in collect()["tokens"]}
        for token in ("--syn-accent", "--syn-bg", "--syn-accent-2", "--syn-accent-soft"):
            self.assertEqual(tokens[token], "tokens.css", token)
        self.assertNotIn("print.css", {classes["syn-app-shell"], classes["syn-terminal"]})

    def test_compositional_utilities_are_optional_and_scoped(self):
        utilities = (ROOT / "src/utilities.css").read_text()
        for cls in ("syn-u-w-full", "syn-u-max-reading", "syn-u-overflow-auto",
                    "syn-u-text-center", "syn-u-min-w-0", "syn-u-wrap"):
            self.assertIn(f".{cls}", utilities)
        self.assertIn("@layer syn.utilities", utilities)
        self.assertNotIn(".syn-u-w-full", (ROOT / "src/components/layout.css").read_text())

    def test_component_tokens_control_real_properties(self):
        panel = (ROOT / "src/components/layout.css").read_text()
        button = (ROOT / "src/components/buttons.css").read_text()
        for property_name in ("--syn-panel-padding", "--syn-panel-radius", "--syn-panel-border-width"):
            self.assertIn(f"var({property_name}", panel)
        self.assertIn("var(--syn-button-padding-inline", button)
        self.assertIn("var(--syn-button-border-width", button)

    def test_playground_is_docs_only_sandboxed_and_published(self):
        page = (ROOT / "docs/playground.html").read_text()
        js = (ROOT / "docs/playground.js").read_text()
        for element_id in ("playground-example", "playground-theme", "playground-markup",
                           "playground-preview", "playground-render", "playground-copy", "playground-status"):
            self.assertIn(f'id="{element_id}"', page)
        self.assertIn('sandbox="allow-same-origin"', page)
        self.assertIn("Content-Security-Policy", js)
        self.assertIn("srcdoc", js)
        self.assertIn("textContent", js)
        self.assertIn("playground.html", (ROOT / "docs/index.html").read_text())
        self.assertIn("playground.html", (ROOT / "README.md").read_text())
        self.assertIn("https://syntyr-css.pages.dev/docs/playground.html",
                      (ROOT / "README.md").read_text())
        # The public source list is tested by the existing Cloudflare integration suite.
        self.assertIn('"playground.html"', (ROOT / "scripts/build_cloudflare_site.py").read_text())
        self.assertIn('"playground.js"', (ROOT / "scripts/build_cloudflare_site.py").read_text())
        from scripts.package_release import FILES
        for name in ("metadata/syntyr-api.json", "metadata/syntyr.html-custom-data.json",
                     "metadata/syntyr.css-custom-data.json", "metadata/syntyr.code-snippets"):
            self.assertIn(name, FILES)
        for file in (ROOT / "dist").glob("*.css"):
            self.assertNotIn("playground.js", file.read_text())

if __name__ == "__main__":
    unittest.main()
