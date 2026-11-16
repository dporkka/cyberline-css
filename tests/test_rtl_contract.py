"""RTL and mixed-direction consumers use the same CSS artifacts as LTR consumers."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class RtlContractTests(unittest.TestCase):
    def test_native_and_classed_tables_use_logical_alignment(self):
        classed = (ROOT / "src/components/data.css").read_text()
        semantic = (ROOT / "src/semantic.css").read_text()
        self.assertIn("border-collapse: collapse; text-align: start;", classed)
        self.assertIn("syn-cell--numeric { text-align: end;", classed)
        self.assertIn("border-collapse: collapse; text-align: start;", semantic)
        self.assertNotIn("text-align: left", classed + semantic)
        self.assertNotIn("text-align: right", classed + semantic)

    def test_directional_overlays_and_decorations_use_logical_edges(self):
        layout = (ROOT / "src/components/layout.css").read_text()
        overlays = (ROOT / "src/components/overlays.css").read_text()
        recipes = (ROOT / "src/recipes.css").read_text()
        self.assertIn("inset-inline-end: -1px;", layout)
        self.assertIn(":dir(rtl)", layout)
        self.assertIn("inset-inline: auto 1rem;", overlays)
        self.assertIn("inset-inline-start: .25rem;", recipes)
        self.assertIn("inset-inline-start: .56rem;", recipes)

    def test_rtl_fixture_is_part_of_all_browser_and_accessibility_inventories(self):
        for script in ("browser_matrix.py", "reflow_test.py", "axe_audit.py"):
            with self.subTest(script=script):
                source = (ROOT / "tests" / script).read_text()
                self.assertIn('"examples/rtl-dashboard.html"', source)
        site = (ROOT / "scripts/build_cloudflare_site.py").read_text()
        self.assertIn('"rtl-dashboard.html"', site)

    def test_fixture_uses_one_self_contained_preset_and_native_direction(self):
        source = (ROOT / "examples/rtl-dashboard.html").read_text()
        parser = Tags()
        parser.feed(source)
        self.assertEqual([attrs.get("href") for tag, attrs in parser.tags
                          if tag == "link" and attrs.get("rel") == "stylesheet"],
                         ["../dist/presets/saas.css"])
        self.assertFalse(any(tag == "script" for tag, _ in parser.tags))
        self.assertTrue(any(tag == "html" and attrs.get("lang") == "ar"
                            and attrs.get("dir") == "rtl" for tag, attrs in parser.tags))
        self.assertTrue(any(attrs.get("dir") == "ltr" for _, attrs in parser.tags))
        self.assertTrue(any(tag == "table" and "syn-table" in attrs.get("class", "")
                            for tag, attrs in parser.tags))
        self.assertTrue(any(tag == "table" and not attrs.get("class")
                            for tag, attrs in parser.tags))
        self.assertIn("syn-cell--numeric", source)
        self.assertIn("syn-panel--cut", source)


if __name__ == "__main__":
    unittest.main()
