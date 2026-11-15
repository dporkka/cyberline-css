"""Homepage design contracts: clear use cases, honest claims and native interaction."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class HomeParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a":
            self.links.append(attrs.get("href", ""))


class HomeShowcaseContract(unittest.TestCase):
    def setUp(self):
        self.html = (ROOT / "index.html").read_text(encoding="utf-8")
        self.page = HomeParser()
        self.page.feed(self.html)

    def test_studio_first_and_real_world_demo_routes(self):
        body = next(attrs for tag, attrs in self.page.tags if tag == "body")
        self.assertEqual(body["data-syn-theme"], "studio")
        self.assertTrue({"main", "showcase", "themes", "components"} <= self.page.ids)
        for link in ("examples/saas-workflows.html", "examples/business.html",
                     "examples/console.html", "examples/landing.html", "docs/"):
            with self.subTest(link=link):
                self.assertIn(link, self.page.links)
        self.assertIn("SaaS", self.html)
        self.assertIn("Business", self.html)
        self.assertIn("Grid", self.html)

    def test_no_js_accessible_navigation_and_real_interaction(self):
        self.assertFalse(any(tag == "script" for tag, _ in self.page.tags))
        self.assertTrue(any(tag == "a" and attrs.get("href") == "#main"
                            and "site-skip" in attrs.get("class", "")
                            for tag, attrs in self.page.tags))
        self.assertTrue(any(tag == "nav" and attrs.get("aria-label")
                            for tag, attrs in self.page.tags))
        self.assertTrue(any(tag == "main" and attrs.get("id") == "main"
                            for tag, attrs in self.page.tags))
        self.assertTrue(any(tag == "button" and attrs.get("commandfor") == "grid-dialog"
                            and attrs.get("command") == "show-modal"
                            for tag, attrs in self.page.tags))
        self.assertTrue(any(tag == "button" and attrs.get("popovertarget") == "grid-popover"
                            for tag, attrs in self.page.tags))
        self.assertTrue(any(tag == "details" for tag, _ in self.page.tags))

    def test_accurate_unreleased_palette_messaging(self):
        self.assertIn("alpha.5", self.html)
        self.assertIn("unreleased", self.html.lower())
        self.assertIn("alpha.4", self.html)
        self.assertIn("seven", self.html.lower())
        self.assertIn("no live data", self.html.lower())
        self.assertIn("MIT", self.html)
        self.assertNotIn("no dependencies, ever", self.html.lower())

    def test_hero_has_css_only_theme_picker_with_real_preview_content(self):
        hero = self.html.split('<section class="site-hero"', 1)[1].split('<details class="site-preview-source"', 1)[0]
        self.assertIn('class="site-hero-gallery"', hero)
        self.assertIn('class="site-theme-picker"', hero)
        for theme in ("studio", "grid", "noir"):
            with self.subTest(theme=theme):
                self.assertIn(f'name="site-preview-theme" value="{theme}"', hero)
                self.assertIn(f'data-site-preview="{theme}"', hero)
        self.assertIn('value="grid" checked', hero)
        self.assertIn('NO LIVE DATA', hero)
        self.assertIn('data-syn-theme="studio" id="top"', self.html)
        self.assertNotIn('<script', hero.lower())

    def test_visual_previews_are_not_fake_operable_controls(self):
        self.assertEqual(self.html.count('class="site-showcase-card'), 3)
        self.assertEqual(sum("site-preview" in attrs.get("class", "").split()
                             for _, attrs in self.page.tags), 3)
        self.assertIn('aria-hidden="true"', self.html)
        self.assertIn("repeat(auto-fit", self.html)
        self.assertIn("prefers-reduced-motion", self.html)
        self.assertIn("forced-colors", self.html)


if __name__ == "__main__":
    unittest.main()
