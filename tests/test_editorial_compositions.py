"""Elementor-inspired publishing, collection and navigation patterns without a builder runtime."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
IDS = ("content-collection", "editorial-article", "site-header-footer", "mega-navigation")


class Nodes(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes = []

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))


class EditorialCompositionTests(unittest.TestCase):
    def setUp(self):
        self.manifest = json.loads((ROOT / "blocks/manifest.json").read_text())["blocks"]
        self.entries = {block["id"]: block for block in self.manifest}

    def snippet(self, ident):
        source = (ROOT / "blocks/snippets" / (ident + ".html")).read_text()
        parser = Nodes()
        parser.feed(source)
        return source, parser.nodes

    def test_four_original_compositions_are_registered_and_core_is_unchanged(self):
        self.assertTrue(set(IDS).issubset(self.entries))
        for ident in IDS:
            entry = self.entries[ident]
            self.assertEqual(entry["modules"], ["core", "recipes"])
            source, nodes = self.snippet(ident)
            self.assertTrue(any("syn-root" in attrs.get("class", "").split() for _, attrs in nodes))
            self.assertFalse(any(tag in ("script", "iframe") for tag, _ in nodes))
            self.assertNotRegex(source, r'(?i)(javascript:|href="#"|onclick=)')
            self.assertFalse(any(k.startswith("on") for _, attrs in nodes for k in attrs))
            self.assertTrue(all(not attrs.get("id", "").startswith("example-") for _, attrs in nodes))

    def test_collection_uses_real_get_filter_and_semantic_listing(self):
        source, nodes = self.snippet("content-collection")
        self.assertTrue(any(tag == "form" and attrs.get("method") == "get" and attrs.get("action", "").startswith("/") for tag, attrs in nodes))
        self.assertTrue(any(tag == "select" and attrs.get("name") == "category" for tag, attrs in nodes))
        self.assertTrue(any(tag == "input" and attrs.get("type") == "search" for tag, attrs in nodes))
        self.assertGreaterEqual(sum(tag == "article" for tag, _ in nodes), 3)
        self.assertTrue(any(tag == "nav" and attrs.get("aria-label") == "Pagination" for tag, attrs in nodes))
        self.assertIn("syn-feature-grid", source)
        self.assertNotIn("data-syn-filtered", source)  # The server handles filtering.

    def test_article_contains_real_toc_author_and_related_content(self):
        source, nodes = self.snippet("editorial-article")
        self.assertTrue(any(tag == "article" for tag, _ in nodes))
        self.assertTrue(any(tag == "time" and attrs.get("datetime") for tag, attrs in nodes))
        self.assertTrue(any(tag == "nav" and attrs.get("aria-label") == "On this page" for tag, attrs in nodes))
        self.assertTrue(any(tag == "aside" and attrs.get("aria-label") == "About the author" for tag, attrs in nodes))
        self.assertTrue(any(tag == "section" and attrs.get("aria-label") == "Related articles" for tag, attrs in nodes))
        self.assertIn("syn-prose", source)
        self.assertIn("syn-sidecar", source)

    def test_navigation_is_native_and_link_based(self):
        header, head_nodes = self.snippet("site-header-footer")
        self.assertTrue(any(tag == "header" for tag, _ in head_nodes))
        self.assertTrue(any(tag == "footer" for tag, _ in head_nodes))
        self.assertTrue(any(tag == "nav" and attrs.get("aria-label") for tag, attrs in head_nodes))
        menu, menu_nodes = self.snippet("mega-navigation")
        self.assertTrue(any(tag == "details" for tag, _ in menu_nodes))
        self.assertTrue(any(tag == "summary" for tag, _ in menu_nodes))
        self.assertTrue(any(tag == "nav" and attrs.get("aria-label") for tag, attrs in menu_nodes))
        self.assertTrue(any(tag == "a" and attrs.get("href", "").startswith("/") for tag, attrs in menu_nodes))
        self.assertNotIn('role="menu"', header + menu)
        self.assertNotIn('aria-haspopup="menu"', header + menu)

    def test_gallery_metadata_and_counts_are_generated_from_manifest(self):
        run = subprocess.run([sys.executable, "scripts/build_blocks.py", "--check"], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        page = (ROOT / "docs/blocks.html").read_text()
        self.assertIn(f"{len(self.manifest)} production-shaped blocks", page)
        self.assertIn(f"{len(self.manifest)} blocks available", page)
        for ident in IDS:
            self.assertIn(f'data-block-id="{ident}"', page)
        for category in ("Publishing", "Navigation"):
            self.assertIn(f'<option value="{category}">{category}</option>', page)


if __name__ == "__main__":
    unittest.main()
