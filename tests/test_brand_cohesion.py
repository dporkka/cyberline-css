"""Contracts for product-led branding and three zero-runtime flagship pages."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
FLAGSHIPS = ("studio", "noir", "grid")


class PageElements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.fragments = []
        self.links = []
        self.scripts = []
        self.mains = 0
        self.h1s = 0

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if attr.get("id"):
            self.ids.add(attr["id"])
        if tag == "a":
            href = attr.get("href", "")
            self.links.append(href)
            if href.startswith("#"):
                self.fragments.append(href[1:])
        if tag == "script":
            self.scripts.append(tag)
        if tag == "main":
            self.mains += 1
        if tag == "h1":
            self.h1s += 1


class BrandCohesionContract(unittest.TestCase):
    def test_homepage_has_native_copyable_product_proof(self):
        home = (ROOT / "index.html").read_text()
        self.assertIn('class="site-preview-source"', home)
        self.assertIn("<summary>View the HTML", home)
        self.assertIn('class="syn-kpi-grid site-preview-metrics"', home)
        self.assertIn('class="syn-app-card site-mini-metric"', home)
        self.assertIn('aria-label="Illustrative', home)
        hero = home.split('<section class="site-hero"', 1)[1].split("</section>", 1)[0]
        self.assertEqual(hero.count('href="docs/#install"'), 1)
        self.assertEqual(hero.count('href="docs/catalog.html"'), 1)

    def test_flagship_pages_have_real_markup_and_accessible_navigation(self):
        for variant in FLAGSHIPS:
            path = ROOT / f"examples/flagship-{variant}.html"
            with self.subTest(variant=variant):
                page = path.read_text()
                parser = PageElements()
                parser.feed(page)
                self.assertEqual((parser.mains, parser.h1s), (1, 1))
                self.assertFalse(parser.scripts)
                self.assertTrue(set(parser.fragments) <= parser.ids)
                self.assertIn('data-syn-theme="' + variant + '"', page)
                self.assertIn('href="flagship.css"', page)
                self.assertIn('class="syn-button flagship-skip"', page)
                self.assertIn("../dist/syntyr.core.css", page)
                self.assertIn("syn-app-card", page)
                self.assertIn("DEMONSTRATION", page)
                self.assertNotIn('src="https://', page)
                self.assertNotIn('<script', page.lower())

    def test_flagship_styles_are_opt_in_responsive_and_accessible(self):
        stylesheet = (ROOT / "examples/flagship.css").read_text()
        for expected in ("--syn-bg", "--syn-surface", "--syn-border-subtle",
                         "@media (max-width:", "@media (forced-colors: active)",
                         "@media (prefers-reduced-motion: reduce)", ".flagship"):
            self.assertIn(expected, stylesheet)
        self.assertNotIn("@import", stylesheet)
        self.assertNotIn("!important", stylesheet)

    def test_navigation_and_activity_use_quiet_separators(self):
        recipes = (ROOT / "src/recipes.css").read_text()
        self.assertIn("border-block-end: 1px solid var(--syn-border-subtle);", recipes)
        self.assertIn("border-inline-end: 1px solid var(--syn-border-subtle);", recipes)
        self.assertIn(
            "li { display: flex; justify-content: space-between; flex-wrap: wrap; "
            "gap: .5rem 1rem; padding: .75rem 0; "
            "border-block-end: 1px solid var(--syn-border-subtle); }",
            recipes
        )
        # Stronger essential input/control boundaries are not weakened.
        self.assertIn("var(--syn-frame)", (ROOT / "src/components/forms.css").read_text())

    def test_flagship_terminal_has_keyboard_accessible_scroll_region(self):
        html = (ROOT / "examples/flagship-grid.html").read_text()
        self.assertIn(
            '<pre class="flagship-terminal" tabindex="0" role="region" '
            'aria-label="Simulated command output">',
            html,
        )
        css = (ROOT / "examples/flagship.css").read_text()
        self.assertIn(".flagship .flagship-terminal:focus-visible", css)

    def test_forced_color_pillars_preserve_canvas_foreground_contrast(self):
        css = (ROOT / "examples/flagship.css").read_text()
        self.assertIn(
            ".flagship .flagship-pillar { border-color: CanvasText; background: Canvas; }",
            css,
        )
        self.assertNotIn(
            ".flagship .flagship-eyebrow::before, .flagship .flagship-pillar",
            css,
        )

    def test_new_public_visual_guidance_is_agent_discoverable(self):
        llms = (ROOT / "llms.txt").read_text()
        self.assertIn("https://syntyr-css.pages.dev/docs/visual-composition.md", llms)
        source = (ROOT / "scripts/build_agent_docs.py").read_text()
        self.assertIn('"docs/visual-composition.md"', source)
        compiled = (ROOT / "llms-full.txt").read_text()
        self.assertIn("## Source: docs/visual-composition.md", compiled)

    def test_public_site_contains_showcases_and_visual_guidelines(self):
        from scripts.build_cloudflare_site import source_files
        published = source_files()
        for filename in ("examples/flagship.css", "docs/visual-composition.md", "docs/visual-composition.html",
                         *(f"examples/flagship-{variant}.html" for variant in FLAGSHIPS)):
            self.assertTrue(filename in published, filename)
        home = (ROOT / "index.html").read_text()
        docs = (ROOT / "docs/index.html").read_text()
        for variant in FLAGSHIPS:
            self.assertIn(f'examples/flagship-{variant}.html', home)
            self.assertIn(f'../examples/flagship-{variant}.html', docs)
        self.assertIn('visual-composition.html', docs)
        self.assertIn("Resend", (ROOT / "docs/visual-composition.md").read_text())


if __name__ == "__main__":
    unittest.main()
