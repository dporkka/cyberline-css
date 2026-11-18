"""Static site-starter pages compose existing MIT blocks without new CSS or JS."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
NAMES = ("business", "journal", "article", "services")

class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.attrs = []
    def handle_starttag(self, tag, attrs):
        self.tags.append(tag)
        self.attrs.append(dict(attrs))

class SiteStarterTests(unittest.TestCase):
    def test_generated_pages_are_reproducible_and_semantic(self):
        run = subprocess.run([sys.executable, "scripts/build_site_starters.py", "--check"],
                             cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        for name in NAMES:
            with self.subTest(name=name):
                page = (ROOT / "examples" / ("site-starter-" + name + ".html")).read_text()
                tags = Tags()
                tags.feed(page)
                self.assertEqual(tags.tags.count("main"), 1)
                self.assertEqual(tags.tags.count("h1"), 1)
                self.assertGreaterEqual(tags.tags.count("section"), 2)
                self.assertEqual(tags.tags.count("script"), 0)
                self.assertIn('href="../dist/syntyr.all.css"', page)
                self.assertIn('class="syn-root', page)
                self.assertIn('id="content"', page)
                self.assertTrue(any(a.get("href") == "#content" for a in tags.attrs))
                self.assertIn("Illustrative site starter", page)

    def test_agent_index_discovers_free_starters(self):
        index = (ROOT / 'llms.txt').read_text()
        self.assertIn('docs/blocks-guide.md', index)
        self.assertIn('site starter', index.lower())

    def test_only_public_free_pages_are_allowlisted(self):
        from scripts.build_cloudflare_site import source_files
        public = source_files()
        for name in NAMES:
            self.assertIn("examples/site-starter-" + name + ".html", public)
        self.assertFalse(any(path.startswith("products/") for path in public))

if __name__ == "__main__":
    unittest.main()
