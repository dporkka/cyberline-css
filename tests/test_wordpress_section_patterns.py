"""Native, copy-owned website section and Gutenberg pattern contracts."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
NEW_IDS = {
    "site-header", "site-footer", "article-grid", "article-detail",
    "service-overview", "process-steps", "portfolio-grid", "case-study",
    "comparison-matrix", "integration-directory", "commerce-collection",
    "newsletter-signup",
}

class SemanticHTML(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.ids = []
        self.labels = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        a = dict(attrs)
        if "id" in a:
            self.ids.append(a["id"])
        if tag == "label":
            self.labels.append(a)

class WebsiteSectionTests(unittest.TestCase):
    def test_first_twelve_new_website_sections_use_existing_primitives(self):
        manifest = json.loads((ROOT / "blocks/manifest.json").read_text())["blocks"]
        blocks = {b["id"]: b for b in manifest}
        self.assertTrue(NEW_IDS <= blocks.keys())
        for ident in sorted(NEW_IDS):
            with self.subTest(ident=ident):
                self.assertIn(blocks[ident]["category"], {"Websites", "Commerce"})
                self.assertIn("core", blocks[ident]["modules"])
                self.assertFalse(set(blocks[ident]["modules"]) - {"core", "recipes"})
                source = (ROOT / "blocks/snippets" / f"{ident}.html").read_text()
                parsed = SemanticHTML()
                parsed.feed(source)
                self.assertEqual(len(parsed.ids), len(set(parsed.ids)))
                self.assertIn("syn-root", source)
                self.assertNotIn("<script", source.lower())
                self.assertNotIn('href="#"', source)
                self.assertNotIn("style=", source)
                self.assertNotIn("http://", source)
                self.assertNotIn("https://", source)
                self.assertNotIn("onclick=", source)
        checks = {
            "site-header": ("header", "nav"),
            "site-footer": ("footer", "nav"),
            "article-grid": ("article", "time"),
            "article-detail": ("article", "time"),
            "service-overview": ("section", "article"),
            "process-steps": ("ol", "li"),
            "portfolio-grid": ("article", "h3"),
            "case-study": ("blockquote", "figure"),
            "comparison-matrix": ("table", "caption"),
            "integration-directory": ("ul", "li"),
            "commerce-collection": ("article", "h3"),
            "newsletter-signup": ("form", "label"),
        }
        for ident, required in checks.items():
            parsed = SemanticHTML()
            parsed.feed((ROOT / "blocks/snippets" / f"{ident}.html").read_text())
            self.assertTrue(set(required) <= set(parsed.tags), ident)

    def test_gallery_and_registry_derive_from_manifest(self):
        blocks = json.loads((ROOT / "blocks/manifest.json").read_text())["blocks"]
        page = (ROOT / "docs/blocks.html").read_text()
        for ident in NEW_IDS:
            self.assertIn(f'data-block-id="{ident}"', page)
            self.assertTrue((ROOT / "registry/r" / f"{ident}.json").is_file())
        for category in sorted({b["category"] for b in blocks}):
            self.assertIn(f'<option value="{category}">', page)
        self.assertIn(f'{len(blocks)} blocks available.', page)
        self.assertIn(f'{len(blocks)} production-shaped blocks.', page)

    def test_wordpress_editor_patterns_use_native_gutenberg_blocks(self):
        plugin = (ROOT / "integrations/wordpress/syntyr-patterns.php").read_text()
        self.assertIn("register_block_pattern_category", plugin)
        self.assertIn("register_block_pattern(", plugin)
        self.assertIn("add_action('init'", plugin)
        for name in ("service-overview", "article-teasers", "call-to-action"):
            source = (ROOT / "integrations/wordpress/patterns" / f"{name}.html").read_text()
            self.assertIn("<!-- wp:group ", source)
            self.assertIn("<!-- /wp:group -->", source)
            self.assertIn("syn-root", source)
            self.assertNotIn("wp:html", source)
            self.assertNotIn("<script", source)
            self.assertIn(f"'{name}'", plugin)
        enqueue = (ROOT / "integrations/wordpress/syntyr-enqueue.php").read_text()
        self.assertIn("enqueue_block_editor_assets", enqueue)
        self.assertIn("wp_enqueue_scripts", enqueue)

if __name__ == "__main__":
    unittest.main()
