"""Native HTML styling must be semantic, opt-in, accessible and dependency-free."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class NativeSemanticPrimitives(unittest.TestCase):
    def test_all_additional_html_elements_supported_only_in_semantic_mode(self):
        source = (ROOT / "src/semantic.css").read_text()
        for element in ("search", "output", "meter", "kbd", "mark", "figure", "figcaption", "pre"):
            with self.subTest(element=element):
                self.assertIn(f"{element}:not([class])", source)
                self.assertIn(f"{element}[data-syn-semantic]", source)
        self.assertIn(":is(.syn-root.syn-semantic, .syn-root .syn-semantic)", source)
        for element in ("mark:not([class])", "meter:not([class])", "figure:not([class])"):
            self.assertNotIn(element, (ROOT / "dist/syntyr.core.css").read_text())

    def test_mark_colors_use_accessible_theme_pair_and_high_contrast_fallback(self):
        css = (ROOT / "src/semantic.css").read_text()
        self.assertIn("background: var(--syn-accent)", css)
        self.assertIn("color: var(--syn-on-accent)", css)
        forced = css.split("@media (forced-colors: active)")[-1]
        self.assertIn("HighlightText", forced)
        self.assertIn("Highlight", forced)

    def test_noninteractive_semantics_remain_native_and_responsive(self):
        css = (ROOT / "src/semantic.css").read_text()
        self.assertIn("overflow-x: auto", css)
        self.assertIn("max-inline-size: 100%", css)
        self.assertIn("min-inline-size: 0", css)
        self.assertIn("accent-color: var(--syn-accent)", css)
        self.assertNotIn("@import", css)
        self.assertNotIn("url(", css)

    def test_native_file_input_can_shrink_in_narrow_grid_containers(self):
        css = (ROOT / "src/semantic.css").read_text()
        block = css.split('input[type="file"]:not([class])', 1)[1]
        block = block.split('::file-selector-button', 1)[0]
        self.assertIn("min-inline-size: 0;", block)
        self.assertIn("max-inline-size: 100%;", block)

    def test_semantic_preview_contains_accessible_html_without_runtime_js(self):
        html = (ROOT / "examples/native-elements.html").read_text()
        for fragment in ('syn-root syn-page syn-semantic', 'syntyr.semantic.css',
                         '<search', 'aria-label="Search examples"', '<figure',
                         '<figcaption', '<mark', '<kbd', '<meter', '<output', '<pre',
                         'type="submit"', 'method="get"', 'for="native-q"'):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, html)
        self.assertNotIn("<script", html.lower())
        self.assertIn("static example", html.lower())

    def test_demo_is_discoverable_and_published_explicitly(self):
        self.assertIn('href="../examples/native-elements.html"', (ROOT / "docs/index.html").read_text())
        self.assertIn('"native-elements.html"', (ROOT / "scripts/build_cloudflare_site.py").read_text())
        self.assertIn("native-elements.html", (ROOT / "docs/components.md").read_text())
        self.assertIn("native-elements.html", (ROOT / "docs/progressive-enhancement.md").read_text())
        self.assertIn("native_semantic_browser.py", (ROOT / "docs/accessibility.md").read_text())

    def test_source_css_rebuilt_in_semantic_distribution(self):
        css = (ROOT / "src/semantic.css").read_text().strip()
        self.assertEqual(css, (ROOT / "dist/syntyr.semantic.css").read_text().strip())
        self.assertIn(css, (ROOT / "dist/syntyr.all.css").read_text())


    def test_keyboard_scrollable_code_example_is_focusable(self):
        import re
        html = (ROOT / "examples/native-elements.html").read_text()
        open_tag = re.search(r"<pre\b[^>]*>", html)
        self.assertIsNotNone(open_tag)
        self.assertIn('tabindex="0"', open_tag.group())
        self.assertIn('aria-label="SQL query example"', open_tag.group())

    def test_long_kbd_chords_wrap_at_large_text_sizes(self):
        css = (ROOT / "src/semantic.css").read_text()
        block = css[css.index("kbd:not([class])") : css.index("mark:not([class])")]
        self.assertIn("max-inline-size: 100%", block)
        self.assertIn("white-space: normal", block)
        self.assertIn("overflow-wrap: anywhere", block)
        self.assertNotIn("white-space: nowrap", block)

    def test_nested_code_preserves_mark_text_contrast(self):
        css = (ROOT / "src/semantic.css").read_text()
        mark = css[css.index("mark:not([class])"):]
        self.assertIn("code:not([class])", mark)
        self.assertIn("color: inherit", mark)
        self.assertIn("<mark><code>status</code></mark>", (ROOT / "examples/native-elements.html").read_text())

    def test_browser_regression_requires_scrollable_focus_and_nested_contrast(self):
        browser = (ROOT / "tests/native_semantic_browser.py").read_text()
        self.assertIn("scrollWidth > e.clientWidth", browser)
        self.assertIn("getComputedStyle(e).overflowX", browser)
        self.assertIn("scrollLeft", browser)
        self.assertIn("mark code", browser)


    def test_native_example_is_covered_by_shared_browser_audits(self):
        for script in ("tests/axe_audit.py", "tests/browser_matrix.py", "tests/reflow_test.py"):
            with self.subTest(script=script):
                self.assertIn('"examples/native-elements.html"', (ROOT / script).read_text())


if __name__ == "__main__":
    unittest.main()
