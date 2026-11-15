"""Regression contract for the small Pico/Blades-inspired Syntyr additions."""
from html.parser import HTMLParser
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class _LinksAndLabels(HTMLParser):
    def __init__(self):
        super().__init__()
        self.styles = []
        self.labels = []
        self.ids = set()
        self.scripts = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.styles.append(attrs["href"])
        if tag == "label":
            self.labels.append(attrs.get("for"))
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "script":
            self.scripts += 1


class PicoBladesErgonomics(unittest.TestCase):
    def test_text_columns_only_in_optional_utility_bundle(self):
        css = (ROOT / "src/utilities.css").read_text()
        self.assertIn(".syn-u-columns", css)
        self.assertIn("--syn-columns-min-width", css)
        self.assertIn("--syn-columns-gap", css)
        self.assertIn("break-inside: avoid", css)
        self.assertIn(".syn-root", css)
        self.assertNotIn("column-count:", css, "Use natural responsive column width rather than hardcoded breakpoints")
        self.assertIn(".syn-u-columns", (ROOT / "dist/syntyr.utilities.css").read_text())
        self.assertIn(".syn-u-columns", (ROOT / "dist/syntyr.all.css").read_text())
        self.assertNotIn(".syn-u-columns", (ROOT / "dist/syntyr.core.css").read_text())

    def test_compact_density_keeps_touch_controls_at_44_px_or_larger(self):
        css = (ROOT / "src/tokens.css").read_text()
        self.assertIn("@media (pointer: coarse)", css)
        coarse = css.split("@media (pointer: coarse)", 1)[1].split("}", 2)[0]
        self.assertIn('data-syn-density="compact"', coarse)
        self.assertIn("--syn-control-height: max(2.75rem, 44px);", coarse)

    def test_real_consumer_fixture_uses_only_per_component_styles(self):
        html = (ROOT / "examples/component-imports.html").read_text()
        parser = _LinksAndLabels()
        parser.feed(html)
        expected = [
            "tokens.css", "base.css", "layout.css", "typography.css",
            "buttons.css", "forms.css",
        ]
        self.assertEqual(
            parser.styles,
            ["../dist/components/" + name for name in expected] + ["../dist/syntyr.utilities.css"],
        )
        package = json.loads((ROOT / "package.json").read_text())
        for name in expected:
            self.assertIn("./components/" + name, package["exports"])
        self.assertIn("./utilities.css", package["exports"])
        self.assertIn('class="syn-u-columns"', html)
        self.assertIn('data-syn-density="compact"', html)
        self.assertIn('class="syn-root', html)
        self.assertEqual(parser.scripts, 0)
        self.assertTrue(parser.labels)
        self.assertTrue(all(label in parser.ids for label in parser.labels if label is not None))
        self.assertNotIn("syntyr.core.css", html)
        self.assertNotIn("syntyr.all.css", html)

    def test_example_is_public_and_portable_with_editor_metadata(self):
        from scripts.package_release import FILES
        from scripts.build_cloudflare_site import source_files, NOINDEX_HTML
        self.assertIn("examples/component-imports.html", FILES)
        self.assertIn("examples/component-imports.html", source_files())
        self.assertIn("examples/component-imports.html", NOINDEX_HTML)
        contract = json.loads((ROOT / "metadata/syntyr-contract.json").read_text())
        self.assertIn("syn-u-columns", {entry["name"] for entry in contract["classes"]})
        for name in ("--syn-columns-min-width", "--syn-columns-gap"):
            self.assertIn(name, {entry["name"] for entry in contract["tokens"]})

    def test_per_component_css_is_not_duplicated_in_core(self):
        core = (ROOT / "dist/syntyr.core.css").read_text()
        for name in ("tokens", "base", "layout", "typography", "buttons", "forms"):
            fragment = (ROOT / ("dist/components/" + name + ".css")).read_text().strip()
            self.assertEqual(core.count(fragment), 1, f"{name} should appear exactly once in core")


if __name__ == "__main__":
    unittest.main()
