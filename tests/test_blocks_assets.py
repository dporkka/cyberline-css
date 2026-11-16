"""Copy-owned block/asset catalog contract. No consumer JavaScript or build tool."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "blocks/manifest.json"
ALLOWED = {"core", "recipes", "geometry", "symbols", "viz", "motion", "effects", "utilities"}


class InspectHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.attributes = []

    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attributes.append(dict(attrs))


class BlocksAssetsTests(unittest.TestCase):
    def test_independent_copy_owned_blocks(self):
        blocks = json.loads(MANIFEST.read_text(encoding="utf-8"))["blocks"]
        self.assertGreaterEqual(len(blocks), 23)
        self.assertEqual(len({b["id"] for b in blocks}), len(blocks))
        self.assertGreaterEqual(len({b["category"] for b in blocks}), 3)
        for block in blocks:
            with self.subTest(block=block["id"]):
                self.assertRegex(block["id"], r"^[a-z][a-z0-9-]+$")
                self.assertTrue(block["title"] and block["description"] and block["tags"])
                self.assertTrue(set(block["modules"]).issubset(ALLOWED))
                self.assertIn("core", block["modules"])
                source = (ROOT / "blocks" / "snippets" / (block["id"] + ".html")).read_text(encoding="utf-8")
                parser = InspectHTML()
                parser.feed(source)
                self.assertTrue(any("syn-root" in a.get("class", "").split() for a in parser.attributes))
                self.assertNotIn("script", parser.tags)
                self.assertNotIn("iframe", parser.tags)
                self.assertNotIn("onclick", " ".join(k for a in parser.attributes for k in a))
                self.assertNotIn('href="#"', source)
                self.assertNotIn("javascript:", source.lower())
                self.assertNotIn("http://", source)
                self.assertNotIn("https://", source)
                self.assertNotIn("data:image", source)
                self.assertIn("</", source)
                self.assertNotIn("syntyr.all.css", source)

    def test_gallery_is_generated_and_progressively_enhanced(self):
        result = subprocess.run(
            [sys.executable, "scripts/build_blocks.py", "--check"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        page = (ROOT / "docs/blocks.html").read_text(encoding="utf-8")
        parsed = InspectHTML()
        parsed.feed(page)
        ids = [a["data-block-id"] for a in parsed.attributes if "data-block-id" in a]
        self.assertEqual(len(ids), len(json.loads(MANIFEST.read_text(encoding="utf-8"))["blocks"]))
        self.assertEqual(len(set(ids)), len(ids))
        self.assertIn('src="blocks.js"', page)
        self.assertIn('href="blocks-assets.css"', page)
        self.assertIn('id="blocks-search"', page)
        self.assertIn('id="blocks-results"', page)
        self.assertIn("Copy HTML", page)
        self.assertIn("<details", page)
        self.assertIn('id="blocks-theme"', page)
        self.assertIn("without JavaScript", page)

    def test_repeated_source_and_copy_controls_have_contextual_names(self):
        page = (ROOT / "docs/blocks.html").read_text(encoding="utf-8")
        parser = InspectHTML()
        parser.feed(page)
        copy_labels = [attrs.get("aria-label", "") for attrs in parser.attributes
                       if "data-block-copy" in attrs]
        self.assertEqual(len(copy_labels), len(json.loads(MANIFEST.read_text(encoding="utf-8"))["blocks"]))
        self.assertEqual(len(set(copy_labels)), len(copy_labels))
        self.assertTrue(all(name.startswith("Copy HTML for ") for name in copy_labels))
        for block in json.loads(MANIFEST.read_text(encoding="utf-8"))["blocks"]:
            self.assertIn("View HTML source for " + block["title"] + "</summary>", page)
        for icon in json.loads((ROOT / "blocks/icons.json").read_text(encoding="utf-8"))["icons"]:
            self.assertIn("SVG source for " + icon["label"] + "</summary>", page)

    def test_twelve_opt_in_decorative_asset_recipes(self):
        css = (ROOT / "docs/blocks-assets.css").read_text(encoding="utf-8")
        ids = re.findall(r"/\* asset: ([a-z][a-z0-9-]+) \*/", css)
        self.assertEqual(len(ids), 12)
        self.assertEqual(len(set(ids)), 12)
        for ident in ids:
            self.assertIn(".syn-block-asset--" + ident, css)
        self.assertNotIn("@import", css)
        self.assertNotIn("url(", css)
        self.assertNotIn("@font-face", css)
        self.assertIn("prefers-reduced-motion", css)

    def test_radar_asset_caption_uses_high_contrast_theme_text(self):
        # The decorative radar ring crossed muted caption text at 390px;
        # don't rely on a narrowly passing background sample.
        css = (ROOT / "docs/blocks-assets.css").read_text(encoding="utf-8")
        self.assertRegex(
            css, r"\.syn-root \.syn-block-asset--radar>span\s*\{\s*color:var\(--syn-text\)"
        )

    def test_twenty_four_original_svg_icon_examples(self):
        icons = json.loads((ROOT / "blocks/icons.json").read_text(encoding="utf-8"))["icons"]
        self.assertEqual(len(icons), 24)
        self.assertEqual(len({icon["id"] for icon in icons}), 24)
        for icon in icons:
            with self.subTest(icon=icon["id"]):
                self.assertRegex(icon["id"], r"^[a-z][a-z0-9-]+$")
                self.assertTrue(icon["label"])
                self.assertTrue(icon["body"].startswith("<"))
                self.assertNotIn("<script", icon["body"])
                self.assertNotIn("href=", icon["body"])
                self.assertNotIn("url(", icon["body"])
        page = (ROOT / "docs/blocks.html").read_text(encoding="utf-8")
        parser = InspectHTML()
        parser.feed(page)
        previews = [a for a in parser.attributes if "data-icon-id" in a]
        self.assertEqual(len(previews), 24)
        self.assertIn('id="blocks-icons-heading"', page)
        self.assertIn('aria-hidden="true"', page)

    def test_public_site_ships_only_reviewed_gallery_files(self):
        from scripts.build_cloudflare_site import source_files
        files = source_files()
        for name in ("docs/blocks.html", "docs/blocks.css",
                     "docs/blocks.js", "docs/blocks-assets.css",
                     "docs/blocks-guide.md"):
            self.assertIn(name, files)
        self.assertFalse(any(name.startswith("blocks/") for name in files))


if __name__ == "__main__":
    unittest.main()
