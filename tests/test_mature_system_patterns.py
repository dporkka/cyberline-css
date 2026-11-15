"""Accessible, CSS-only compositions inspired by mature design systems."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []
        self.ids = set()
        self.links = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        self.elements.append((tag, attrs))
        if "id" in attrs:
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href", "").startswith("#"):
            self.links.append(attrs["href"][1:])


class MatureComponentContracts(unittest.TestCase):
    def test_error_summary_is_root_scoped_and_has_forced_color_fallback(self):
        css = (ROOT / "src/components/form-composition.css").read_text()
        self.assertIn(":where(.syn-root, .syn-root *)", css)
        self.assertIn("&.syn-error-summary {", css)
        self.assertIn("border-inline-start:", css)
        self.assertIn("&.syn-error-summary a", css)
        self.assertIn("@media (forced-colors: active)", css)
        self.assertIn("CanvasText", css)

    def test_description_list_is_semantic_responsive_and_direction_neutral(self):
        css = (ROOT / "src/components/data.css").read_text()
        for fragment in (
            "&.syn-description-list {",
            "&.syn-description-list > div",
            "&.syn-description-list dt",
            "&.syn-description-list dd",
            "@container syn-region",
            "minmax(0, 1fr)",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, css)
        self.assertIn("border-block-end:", css)
        self.assertNotIn("padding-left:", css)
        self.assertNotIn("margin-left:", css)

    def test_data_table_uses_logical_alignment_and_real_sort_state(self):
        css = (ROOT / "src/components/data.css").read_text()
        self.assertIn("&.syn-table {", css)
        self.assertIn("text-align: start;", css)
        self.assertIn(".syn-cell--numeric { text-align: end;", css)
        self.assertIn('th[aria-sort="ascending"]', css)
        self.assertIn('th[aria-sort="descending"]', css)
        self.assertNotIn("text-align: left;", css)
        self.assertNotIn("text-align: right;", css)

    def test_example_has_accessible_server_rendered_form_and_sorted_table(self):
        markup = Markup()
        markup.feed((ROOT / "examples/mature-patterns.html").read_text())
        by_id = {attrs["id"]: (tag, attrs) for tag, attrs in markup.elements if "id" in attrs}
        self.assertIn("name", by_id)
        self.assertEqual(by_id["name"][1].get("aria-invalid"), "true")
        self.assertIn("name-error", by_id["name"][1]["aria-describedby"].split())
        self.assertIn("name-error", by_id)
        self.assertIn("name", markup.links)
        self.assertTrue(any("syn-error-summary" in attrs.get("class", "") for _, attrs in markup.elements))
        self.assertTrue(any(tag == "dl" and "syn-description-list" in attrs.get("class", "") for tag, attrs in markup.elements))
        self.assertTrue(any(tag == "dt" for tag, _ in markup.elements))
        self.assertTrue(any(tag == "dd" for tag, _ in markup.elements))
        self.assertTrue(any(tag == "th" and attrs.get("aria-sort") == "ascending" for tag, attrs in markup.elements))
        self.assertTrue(any(tag == "button" and attrs.get("type") == "button" for tag, attrs in markup.elements))
        self.assertTrue(any(attrs.get("dir") == "rtl" for _, attrs in markup.elements))
        self.assertTrue(all(target in markup.ids for target in markup.links))

    def test_documentation_names_app_owned_behavior_and_real_aria(self):
        text = (ROOT / "docs/mature-system-patterns.md").read_text()
        for phrase in ("server-rendered", "focus", "aria-describedby", "aria-sort", "RTL", "No JavaScript"):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)


if __name__ == "__main__":
    unittest.main()
