"""Contracts for portable, WordPress-inspired site sections."""
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {
    "site-header", "site-footer", "article-featured", "article-grid",
    "article-detail", "author-profile", "services-grid", "process-steps",
    "portfolio-grid", "case-study-preview", "comparison-table",
    "integrations-grid", "logo-wall", "product-collection",
    "category-showcase", "newsletter-signup", "contact-quote",
    "service-areas", "team-grid", "announcement-banner",
}

class Elements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))

class SiteSectionsTests(unittest.TestCase):
    def test_twenty_additional_portable_site_sections(self):
        blocks = json.loads((ROOT / "blocks/manifest.json").read_text())["blocks"]
        ids = {b["id"] for b in blocks}
        self.assertTrue(REQUIRED.issubset(ids), sorted(REQUIRED - ids))
        self.assertEqual(len(ids), len(blocks))
        self.assertGreaterEqual(len(blocks), 40)
        for block in blocks:
            if block["id"] not in REQUIRED:
                continue
            with self.subTest(block=block["id"]):
                self.assertIn(block["category"], {"Navigation", "Editorial", "Services", "Portfolio", "Commerce", "Marketing"})
                self.assertIn("core", block["modules"])
                self.assertTrue(block["tags"])
                source = (ROOT / "blocks/snippets" / (block["id"] + ".html")).read_text()
                parsed = Elements()
                parsed.feed(source)
                self.assertTrue(any("syn-root" in a.get("class", "").split() for _, a in parsed.elements))
                self.assertFalse(any(tag in {"script", "iframe", "style"} for tag, _ in parsed.elements))
                self.assertFalse(any(a.get("href", "").startswith(("http:", "https:", "#", "javascript:"))
                                     for _, a in parsed.elements if "href" in a))
                ids_in_block = [a["id"] for _, a in parsed.elements if "id" in a]
                self.assertEqual(len(ids_in_block), len(set(ids_in_block)))
                for _, a in parsed.elements:
                    if "aria-labelledby" in a:
                        self.assertTrue(set(a["aria-labelledby"].split()).issubset(ids_in_block))
                    if a.get("type") == "submit":
                        self.assertNotIn("disabled", a)
                self.assertNotRegex(source, r"\bon(?:click|submit|load)=")

    def test_site_header_and_footer_link_targets_use_existing_accessible_rows(self):
        """Prevent WCAG 2.2 target-size regressions in copy-owned nav patterns."""
        for ident in ("site-header", "site-footer"):
            snippet = (ROOT / "blocks/snippets" / f"{ident}.html").read_text()
            parsed = Elements()
            parsed.feed(snippet)
            for tag, attrs in parsed.elements:
                if tag != "a":
                    continue
                with self.subTest(block=ident, destination=attrs.get("href")):
                    classes = set(attrs.get("class", "").split())
                    self.assertTrue(
                        classes.intersection({"syn-list-row", "syn-button", "syn-page-link"}),
                        f"{ident}: link has no existing >=24px target-size primitive",
                    )

    def test_gallery_metadata_counts_are_generated_not_hard_coded(self):
        script = (ROOT / "scripts/build_blocks.py").read_text()
        self.assertNotIn("20 production-shaped blocks", script)
        self.assertNotIn("20 blocks available", script)
        self.assertNotIn("20 original HTML/CSS blocks", script)
        result = subprocess.run([sys.executable, "scripts/build_blocks.py", "--check"],
                                cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr + result.stdout)
        blocks = json.loads((ROOT / "blocks/manifest.json").read_text())["blocks"]
        parsed = Elements()
        parsed.feed((ROOT / "docs/blocks.html").read_text())
        self.assertEqual(sum(1 for _, a in parsed.elements if "data-block-id" in a), len(blocks))
        for name in {"Navigation", "Editorial", "Services", "Portfolio", "Commerce"}:
            self.assertIn('value="' + name + '"', (ROOT / "docs/blocks.html").read_text())

if __name__ == "__main__":
    unittest.main()
