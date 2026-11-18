"""WordPress block-theme reference patterns remain editable and optional."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = ROOT / "integrations/wordpress/patterns"
NAMES = {"header", "services", "journal", "product-collection"}

class NativeWordPressPatternTests(unittest.TestCase):
    def test_four_portable_gutenberg_patterns(self):
        self.assertEqual({p.stem for p in PATTERNS.glob("*.php")}, NAMES)
        for name in NAMES:
            with self.subTest(pattern=name):
                source = (PATTERNS / (name + ".php")).read_text()
                self.assertIn("Slug: syntyr/" + name, source)
                self.assertIn("Categories:", source)
                self.assertIn("<!-- wp:group ", source)
                self.assertIn("<!-- /wp:group -->", source)
                self.assertIn("syn-root", source)
                self.assertNotIn("wp:html", source)
                self.assertNotIn("<script", source)
                self.assertNotIn("https://", source)
                self.assertNotIn("wp:shortcode", source)
                opening = re.findall(r"<!-- wp:([a-z][a-z-]*)\b", source)
                closing = re.findall(r"<!-- /wp:([a-z][a-z-]*) -->", source)
                self.assertEqual(sorted(opening), sorted(closing))
    def test_documented_non_plugin_installation(self):
        guide = (ROOT / "docs/wordpress.md").read_text()
        self.assertIn("integrations/wordpress/patterns", guide)
        self.assertIn("child theme", guide)
        self.assertIn("WordPress editor", guide)
        self.assertIn("not a plugin", guide.lower())

if __name__ == "__main__":
    unittest.main()
