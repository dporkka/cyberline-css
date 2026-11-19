"""Catalog discoverability and inclusion in real-browser / accessibility gates."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CatalogCoverage(unittest.TestCase):
    def test_main_homepage_directly_links_to_searchable_catalog(self):
        home = (ROOT / 'index.html').read_text(encoding='utf-8')
        self.assertIn('href="docs/catalog.html"', home)
        self.assertIn('href="docs/"', home, 'Preserve the ordinary documentation route')

    def test_catalog_is_exercised_in_all_existing_browser_gates(self):
        for file in ('tests/browser_matrix.py', 'tests/reflow_test.py', 'tests/axe_audit.py'):
            with self.subTest(file=file):
                source = (ROOT / file).read_text(encoding='utf-8')
                self.assertIn('"docs/catalog.html"', source)

    def test_browser_matrix_requires_only_a_local_docs_script(self):
        matrix = (ROOT / 'tests/browser_matrix.py').read_text(encoding='utf-8')
        self.assertIn('script[src="catalog.js"]', matrix)
        self.assertIn('name == "docs/catalog.html"', matrix)


if __name__ == '__main__':
    unittest.main()
