"""Homepage and documentation onboarding contracts for the static website."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class NavigationParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside_header_nav = 0
        self.header_links = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "nav" and attrs.get("aria-label") in {"Main navigation", "Documentation navigation"}:
            self.inside_header_nav += 1
        if tag == "a" and self.inside_header_nav:
            self.header_links.append(attrs.get("href", ""))

    def handle_endtag(self, tag):
        if tag == "nav" and self.inside_header_nav:
            self.inside_header_nav -= 1


class SiteOnboardingTests(unittest.TestCase):
    def test_home_has_direct_first_screen_installation_and_catalog_paths(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        hero = home.split('<section class="site-hero"', 1)[1].split("</section>", 1)[0]
        self.assertIn('href="docs/#install"', hero)
        self.assertIn('href="docs/catalog.html"', hero)
        self.assertIn('href="#theme-comparison"', home)
        self.assertIn('class="site-theme-comparison"', home)
        for theme in ("studio", "grid", "noir"):
            self.assertIn(f'class="site-compare-card" data-syn-theme="{theme}"', home)

    def test_docs_put_getting_started_before_component_gallery(self):
        docs = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        self.assertLess(docs.index('id="install"'), docs.index('id="themes"'))
        self.assertLess(docs.index('id="themes"'), docs.index('id="components"'))
        hero = docs.split('<section class="docs-hero', 1)[1].split("</section>", 1)[0]
        self.assertIn('href="#install"', hero)
        self.assertIn('href="catalog.html"', hero)
        self.assertIn('href="guides.html"', docs)
        self.assertNotIn("V0.3.0-ALPHA.2 / DISTRIBUTION", docs)

    def test_install_page_defaults_to_published_version_and_labels_source_preview(self):
        docs = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        install = docs.split('id="install"', 1)[1].split('id="themes"', 1)[0]
        published = 'https://syntyr-css.pages.dev/v/0.3.0-alpha.4/syntyr.core.css'
        self.assertIn(f'class="syn-button syn-button--primary" href="{published}"', install)
        self.assertIn(f'href="{published}"&gt;', install, "copyable CDN sample must match the published release")
        self.assertIn('href="../dist/syntyr.core.css"', install, "experimental source must remain available")
        self.assertIn("UNRELEASED ALPHA.5 PREVIEW", install)
        self.assertNotIn('class="syn-button syn-button--primary" href="../dist/syntyr.core.css"', install)

    def test_responsive_navigation_uses_native_details_without_javascript(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        docs = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        css = (ROOT / "docs/docs.css").read_text(encoding="utf-8")
        for page in (home, docs):
            self.assertIn('class="site-mobile-menu"', page)
            self.assertIn('<summary', page)
            self.assertIn('aria-label="Mobile navigation"', page)
            self.assertNotIn("<script", page.lower())
        self.assertIn('.site-mobile-menu', home)
        self.assertIn('.site-mobile-menu', css)
        nav = NavigationParser()
        nav.feed(docs)
        self.assertTrue(all(not href.endswith(".md") for href in nav.header_links))

    def test_site_brand_assets_and_styled_guides_are_published(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        docs = (ROOT / "docs/index.html").read_text(encoding="utf-8")
        self.assertIn('rel="icon" href="assets/syntyr-mark.svg"', home)
        self.assertIn('rel="icon" href="../assets/syntyr-mark.svg"', docs)
        self.assertIn('property="og:image"', home)
        self.assertTrue((ROOT / "assets/syntyr-mark.svg").is_file())
        self.assertTrue((ROOT / "assets/og-syntyr.png").is_file())
        self.assertTrue((ROOT / "docs/guides.html").is_file())
        build = (ROOT / "scripts/build_cloudflare_site.py").read_text(encoding="utf-8")
        for asset in ('"guides.html"', '"assets/syntyr-mark.svg"', '"assets/og-syntyr.png"'):
            self.assertIn(asset, build)


if __name__ == "__main__":
    unittest.main()
