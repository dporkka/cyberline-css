"""The checked-in gallery manifest must be derived from existing public sources."""
from html import unescape
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GalleryManifestTests(unittest.TestCase):
    def test_manifest_is_reproducible_and_matches_public_catalog(self):
        generated = ROOT / "metadata/component-gallery.v1.json"
        self.assertTrue(generated.is_file())
        contract = json.loads(generated.read_text(encoding="utf-8"))
        curated = json.loads((ROOT / "metadata/components.json").read_text(encoding="utf-8"))
        self.assertEqual(contract["schema_version"], 1)
        self.assertEqual(contract["source_version"], (ROOT / "VERSION").read_text().strip())
        self.assertEqual(contract["components"], curated["components"])
        self.assertEqual(contract["recipes"], curated["recipes"])
        self.assertEqual(contract["themes"], json.loads((ROOT / "metadata/syntyr-api.json").read_text())["themes"])
        self.assertEqual(contract["completeness"], "curated-examples")
        examples = contract["examples"]
        page = (ROOT / "docs/catalog.html").read_text(encoding="utf-8")
        self.assertEqual(len(examples), page.count('<article class="catalog-card syn-panel"'))
        self.assertEqual(len({item["id"] for item in examples}), len(examples))
        for example in examples:
            self.assertIn(f'id="{example["id"]}"', page)
            self.assertTrue(example["title"])
            self.assertTrue(example["keywords"])
            self.assertTrue(example["category"])
            self.assertIn(example["module"], {"syntyr.core.css", "syntyr.recipes.css", "syntyr.geometry.css", "syntyr.viz.css"})
            self.assertTrue(example["html"].strip())
            self.assertNotIn("<script", example["html"].lower())
            self.assertTrue(example["elements"])
            if example["module"] == "syntyr.core.css":
                self.assertEqual(example["required_stylesheets"][0], "syntyr.core.css")
            else:
                self.assertEqual(example["required_stylesheets"][:2],
                                 ["syntyr.core.css", example["module"]])
            for cls in example["classes"]:
                self.assertIn("." + cls, (ROOT / "dist/syntyr.all.css").read_text())
        result = subprocess.run(
            [sys.executable, "scripts/build_component_gallery.py", "--check"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_gallery_is_discoverable_in_both_distributions_and_npm(self):
        from scripts.build_cloudflare_site import source_files
        from scripts.package_release import FILES
        name = "metadata/component-gallery.v1.json"
        self.assertIn(name, set(source_files()))
        self.assertIn(name, FILES)
        pkg = json.loads((ROOT / "package.json").read_text())
        self.assertEqual(pkg["exports"]["./gallery.json"], "./" + name)
        self.assertIn(name, pkg["files"])
        self.assertIn("component-gallery.v1.json", (ROOT / "docs/editor-integration.md").read_text())

    def test_published_manifest_has_cross_origin_read_header(self):
        from scripts.build_cloudflare_site import HEADERS
        self.assertIn(
            "/metadata/component-gallery.v1.json\n  Access-Control-Allow-Origin: *",
            HEADERS,
        )

    def test_release_package_refuses_stale_gallery(self):
        from scripts import package_release
        import inspect
        source = inspect.getsource(package_release.package)
        self.assertIn('scripts/build_component_gallery.py', source)
        self.assertIn('"--check"', source)

    def test_gallery_theme_and_preview_controls_preserve_no_js_examples(self):
        page = (ROOT / "docs/catalog.html").read_text(encoding="utf-8")
        script = (ROOT / "docs/catalog.js").read_text(encoding="utf-8")
        self.assertIn('id="catalog-theme"', page)
        self.assertIn('id="catalog-preview-size"', page)
        self.assertIn('id="catalog-controls" class="catalog-controls" hidden', page)
        for theme in ("studio", "grid", "noir", "industrial", "terminal", "corporate", "minimal"):
            self.assertIn(f'<option value="{theme}"', page)
            self.assertIn(f'data-syn-theme="{theme}"', (ROOT / "src/tokens.css").read_text())
        self.assertIn('addEventListener("change"', script)
        self.assertIn("data-catalog-preview", script)
        self.assertGreaterEqual(page.count("class=\"catalog-preview\""), 16)


if __name__ == "__main__":
    unittest.main()
