"""The interactive reference reuses catalog examples instead of duplicating snippets."""
import json
from html import unescape
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class InteractiveReferenceTests(unittest.TestCase):
    def test_catalog_examples_are_generated_from_canonical_gallery(self):
        result = subprocess.run([sys.executable, "scripts/build_playground_catalog.py", "--check"],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        source = (ROOT / "docs/playground-catalog.js").read_text()
        self.assertTrue(source.startswith("window.SYNTYR_PLAYGROUND_CATALOG = "))
        entries = json.loads(source.removeprefix("window.SYNTYR_PLAYGROUND_CATALOG = ").removesuffix(";\n"))
        self.assertGreaterEqual(len(entries), 8)
        self.assertEqual(len({entry["id"] for entry in entries}), len(entries))
        self.assertTrue(any(item["title"] == "Buttons" for item in entries))
        catalog = (ROOT / "docs/catalog.html").read_text()
        blocks = (ROOT / "docs/blocks.html").read_text()
        for entry in entries:
            original = blocks if entry.get("kind") == "block" else catalog
            identifier = entry["id"].removeprefix("block-") if entry.get("kind") == "block" else entry["id"]
            self.assertIn(identifier, original)
            self.assertIn(entry["html"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").splitlines()[0], original)
            self.assertTrue(entry["module"].startswith("syntyr."))
            self.assertTrue(entry["description"])

    def test_playground_exposes_search_preview_and_safe_editing(self):
        html = (ROOT / "docs/playground.html").read_text()
        script = (ROOT / "docs/playground.js").read_text()
        for element in ("playground-search", "playground-viewport", "playground-panel-radius",
                        "playground-panel-padding", "playground-reference", "playground-preview"):
            self.assertIn('id="' + element + '"', html)
        self.assertIn('src="playground-catalog.js"', html)
        self.assertIn('sandbox="allow-same-origin"', html)
        self.assertNotIn("allow-scripts", html)
        self.assertIn("Content-Security-Policy", script)
        self.assertIn("default-src 'none'", script)
        self.assertIn("URLSearchParams", script)
        self.assertIn("window.SYNTYR_PLAYGROUND_CATALOG", script)

    def test_catalog_can_open_any_example_in_playground(self):
        js = (ROOT / "docs/catalog.js").read_text()
        self.assertIn("playground.html#component=", js)
        self.assertIn('document.createElement("a")', js)
        self.assertIn("catalog-copy", js)

    def test_deployment_includes_generated_catalog(self):
        site = (ROOT / "scripts/build_cloudflare_site.py").read_text()
        self.assertIn('"playground-catalog.js"', site)
        index = (ROOT / "docs/index.html").read_text()
        self.assertIn('playground.html', index)


if __name__ == "__main__":
    unittest.main()
