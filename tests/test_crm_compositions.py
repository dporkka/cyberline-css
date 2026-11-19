"""CRM composition contracts: styles are optional; interaction is host-owned."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CRMMarkup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.labels = set()
        self.fields = set()
        self.search_form = False
        self.pipelines = 0
        self.lanes = 0
        self.links = 0
        self.description_lists = 0

    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        classes = set(a.get("class", "").split())
        if "id" in a:
            self.ids.add(a["id"])
        if tag == "label":
            self.labels.add(a.get("for"))
        if tag in {"input", "select"}:
            self.fields.add((a.get("id"), a.get("name")))
        if tag == "form" and a.get("method") == "get":
            self.search_form = True
        if "syn-pipeline" in classes:
            self.pipelines += 1
            self.assert_tabindex = a.get("tabindex") == "0" and bool(a.get("aria-label"))
        if "syn-pipeline-lane" in classes and tag == "section" and a.get("aria-labelledby"):
            self.lanes += 1
        if tag == "a" and a.get("href"):
            self.links += 1
        if tag == "dl" and "syn-record-fields" in classes:
            self.description_lists += 1


class CRMCompositions(unittest.TestCase):
    def test_density_profiles_can_reset_in_nested_regions(self):
        tokens = (ROOT / "src/tokens.css").read_text()
        for density in ("compact", "comfortable", "spacious"):
            self.assertIn(f'.syn-root[data-syn-density="{density}"]', tokens)
            self.assertIn(f'.syn-root [data-syn-density="{density}"]', tokens)
        self.assertIn("--syn-control-height: 2.25rem", tokens)
        self.assertIn("--syn-control-height: 3.25rem", tokens)
        self.assertIn("--syn-row-padding-block: 1rem", tokens)

    def test_crm_styles_are_opt_in_and_keyboard_visible(self):
        recipes = (ROOT / "src/recipes.css").read_text()
        core = (ROOT / "dist/syntyr.core.css").read_text()
        for cls in (".syn-filter-bar", ".syn-filter-field", ".syn-filter-actions",
                    ".syn-pipeline", ".syn-pipeline-lane", ".syn-pipeline-card",
                    ".syn-record-fields"):
            self.assertIn(cls, recipes)
            self.assertNotIn(cls, core)
        self.assertIn("&.syn-pipeline:focus-visible", recipes)
        self.assertIn("&.syn-pipeline-card:focus-within", recipes)
        self.assertIn("@media (forced-colors: active)", recipes)
        self.assertNotIn("!important", recipes)

    def test_crm_example_is_native_and_accessible(self):
        source = (ROOT / "examples/crm.html").read_text()
        parser = CRMMarkup()
        parser.feed(source)
        self.assertNotIn("<script", source.lower())
        self.assertTrue(parser.search_form)
        self.assertIn(("query", "query"), parser.fields)
        self.assertIn(("status", "status"), parser.fields)
        self.assertIn("query", parser.labels)
        self.assertIn("status", parser.labels)
        self.assertEqual(parser.pipelines, 1)
        self.assertTrue(parser.assert_tabindex)
        self.assertGreaterEqual(parser.lanes, 2)
        self.assertEqual(parser.description_lists, 1)
        self.assertGreaterEqual(parser.links, 3)

    def test_crm_example_is_in_opt_in_browser_and_accessibility_matrix(self):
        for name in ("browser_matrix.py", "axe_audit.py", "reflow_test.py"):
            matrix = (ROOT / "tests" / name).read_text()
            self.assertIn('"examples/crm.html"', matrix)

    def test_html_editor_suggests_all_density_profiles(self):
        import json
        data = json.loads((ROOT / "metadata/syntyr.html-custom-data.json").read_text())
        entry = next(a for a in data["globalAttributes"] if a["name"] == "data-syn-density")
        self.assertEqual({v["name"] for v in entry["values"]},
                         {"compact", "comfortable", "spacious"})

    def test_dist_bundles_and_documentation_include_crm_recipes(self):
        css = (ROOT / "dist/syntyr.recipes.css").read_text()
        all_css = (ROOT / "dist/syntyr.all.css").read_text()
        self.assertIn(".syn-pipeline", css)
        self.assertIn(".syn-pipeline", all_css)
        recipes = (ROOT / "docs/recipes.md").read_text()
        self.assertIn("syn-filter-bar", recipes)
        self.assertIn("syn-pipeline", recipes)
        self.assertIn("data-syn-density=\"spacious\"", recipes)


if __name__ == "__main__":
    unittest.main()
