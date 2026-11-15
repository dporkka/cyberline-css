"""Opt-in design-asset distribution and attribution contracts."""
import json
from pathlib import Path
import subprocess
import sys
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]


class DesignAssetContract(unittest.TestCase):
    def test_patterns_are_optional_and_scoped(self):
        sys.path.insert(0, str(ROOT))
        from scripts.build import distributions
        manifests = distributions()
        self.assertEqual(manifests["syntyr.patterns.css"], ("patterns.css",))
        self.assertNotIn("patterns.css", manifests["syntyr.core.css"])
        self.assertNotIn("patterns.css", manifests["syntyr.css"])
        self.assertIn("patterns.css", manifests["syntyr.all.css"])
        css = (ROOT / "src/patterns.css").read_text()
        for name in ("dots", "blueprint", "diagonal", "hatch", "scanlines"):
            with self.subTest(pattern=name):
                self.assertIn(".syn-root .syn-pattern--" + name, css)
                self.assertIn(".syn-root.syn-pattern--" + name, css)
        for banned in ("@import", "@font-face", "url(", "<script"):
            self.assertNotIn(banned, css)
        self.assertIn("@media (forced-colors: active)", css)
        self.assertIn("@media (prefers-contrast: more)", css)

    def test_icons_are_prebuilt_safe_svg_with_no_remote_runtime(self):
        icons = json.loads((ROOT / "blocks/icons.json").read_text())["icons"]
        for icon in icons:
            with self.subTest(icon=icon["id"]):
                path = ROOT / "assets/icons" / (icon["id"] + ".svg")
                self.assertTrue(path.is_file())
                markup = path.read_text()
                svg = ET.fromstring(markup)
                self.assertEqual(svg.tag, "{http://www.w3.org/2000/svg}svg")
                self.assertEqual(svg.attrib.get("viewBox"), "0 0 24 24")
                self.assertEqual(svg.attrib.get("fill"), "none")
                self.assertEqual(svg.attrib.get("stroke"), "currentColor")
                self.assertNotIn("http://", markup.replace("http://www.w3.org/2000/svg", ""))
                self.assertNotIn("https://", markup.replace("http://www.w3.org/2000/svg", ""))
                self.assertNotIn("<script", markup.lower())
                self.assertNotIn("onload=", markup.lower())
                self.assertNotIn("href=", markup.lower())
        process = subprocess.run([sys.executable, "scripts/export_icons.py", "--check"],
                                 cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(process.returncode, 0, process.stdout + process.stderr)

    def test_manifest_declares_origins_and_no_vendored_pack(self):
        data = json.loads((ROOT / "metadata/design-assets.json").read_text())
        self.assertEqual(data["license"], "MIT")
        self.assertEqual(data["origin"], "original Syntyr artwork")
        self.assertEqual(len(data["icons"]), 24)
        self.assertEqual(len(set(data["icons"])), 24)
        self.assertEqual(len(data["patterns"]), 5)
        self.assertTrue(all(x.startswith("syn-pattern--") for x in data["patterns"]))
        self.assertTrue(all(x["bundled"] is False for x in data["external_references"]))

    def test_site_and_release_include_attribution_and_optional_assets(self):
        sys.path.insert(0, str(ROOT))
        from scripts.build_cloudflare_site import source_files
        from scripts.package_release import FILES
        site = source_files()
        for path in ("dist/syntyr.patterns.css", "metadata/design-assets.json",
                     "assets/icons/search.svg", "assets/icons/shield.svg",
                     "THIRD_PARTY_NOTICES.md"):
            self.assertTrue(path in site, path)
            self.assertIn(path, FILES)
        self.assertNotIn("assets/icons/search.svg", (ROOT / "dist/syntyr.core.css").read_text())

    def test_public_docs_show_existing_themes_and_asset_licenses(self):
        guide = (ROOT / "docs/design-assets.md").read_text()
        self.assertIn('data-syn-theme="studio"', guide)
        self.assertIn('data-syn-theme="grid"', guide)
        self.assertIn('data-syn-theme="noir"', guide)
        self.assertIn("Lucide", guide)
        self.assertIn("ISC", guide)
        self.assertIn("third-party", guide.lower())
        self.assertIn("syntyr.patterns.css", guide)
        self.assertIn("prefers-reduced-motion", guide)
        self.assertIn("24 original", guide)
        readme = (ROOT / "README.md").read_text()
        self.assertIn("docs/design-assets.md", readme)


if __name__ == "__main__":
    unittest.main()
