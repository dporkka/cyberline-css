"""Production-shaped, JavaScript-free multi-page business-site starter contract."""

from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "examples" / "business-starter"
PAGES = ("index.html", "services.html", "case-study.html", "contact.html")


class SiteMarkup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.nav_current = []
        self.forms = []
        self.buttons = []
        self.scripts = []
        self.headings = []
        self.main_count = 0

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get("id"):
            self.ids.append(attrs["id"])
        if tag in ("a", "link", "img", "script"):
            if tag != "script":
                self.links.append(attrs.get("href") or attrs.get("src") or "")
            else:
                self.scripts.append(attrs)
        if tag == "a" and attrs.get("aria-current") == "page":
            self.nav_current.append(attrs.get("href"))
        if tag == "form":
            self.forms.append(attrs)
        if tag == "button":
            self.buttons.append(attrs)
        if tag == "h1":
            self.headings.append(attrs)
        if tag == "main":
            self.main_count += 1


class BusinessSiteStarterTests(unittest.TestCase):
    def test_four_page_starter_and_copy_owned_css_exist(self):
        for name in (*PAGES, "site.css", "README.md"):
            with self.subTest(file=name):
                self.assertTrue((SITE / name).is_file())

    def test_pages_are_semantic_and_cross_link_correctly_without_javascript(self):
        for name in PAGES:
            with self.subTest(page=name):
                page = SITE / name
                html = page.read_text(encoding="utf-8")
                parser = SiteMarkup()
                parser.feed(html)
                self.assertEqual(parser.main_count, 1)
                self.assertEqual(len(parser.headings), 1)
                self.assertEqual(len(parser.ids), len(set(parser.ids)))
                self.assertIn("main-content", parser.ids)
                self.assertIn('href="#main-content"', html)
                self.assertEqual(parser.nav_current, [name])
                self.assertIn("syn-root", html)
                self.assertIn("data-syn-theme=\"studio\"", html)
                self.assertIn("../../dist/syntyr.core.css", parser.links)
                self.assertIn("../../dist/syntyr.recipes.css", parser.links)
                self.assertIn("./site.css", parser.links)
                self.assertFalse(parser.scripts, "No browser JavaScript in the starter")
                self.assertNotRegex(html, r'https?://[^"\s>]+(?:\.js|\.woff2?|\.css)')
                for url in parser.links:
                    parsed = urlsplit(url)
                    if parsed.scheme or parsed.netloc or parsed.path.startswith("/"):
                        continue
                    if parsed.path:
                        target = (page.parent / unquote(parsed.path)).resolve()
                        self.assertTrue(target.is_relative_to(ROOT))
                        self.assertTrue(target.is_file(), (name, url))
                    if parsed.fragment and not parsed.path:
                        self.assertIn(parsed.fragment, parser.ids, (name, url))

    def test_nonfunctional_contact_form_is_safely_marked_for_integration(self):
        html = (SITE / "contact.html").read_text(encoding="utf-8")
        parser = SiteMarkup()
        parser.feed(html)
        self.assertEqual(len(parser.forms), 1)
        self.assertFalse(parser.forms[0].get("action"), "Do not POST to an inactive endpoint")
        self.assertIn('method="post"', html)
        self.assertIn("<fieldset disabled", html)
        self.assertTrue(any("disabled" in button for button in parser.buttons))
        self.assertIn("server-side", html.lower())
        self.assertIn("csrf", (SITE / "README.md").read_text().lower())

    def test_fictional_story_does_not_imply_real_customer_evidence(self):
        html = (SITE / "case-study.html").read_text(encoding="utf-8")
        self.assertRegex(html.lower(), r"fictional|illustrative")
        self.assertNotIn('type="application/ld+json"', html)

    def test_release_archive_contains_editable_complete_starter(self):
        from scripts.package_release import package
        version = (ROOT / "VERSION").read_text().strip()
        with tempfile.TemporaryDirectory() as temp:
            archive_path = Path(temp) / "site.zip"
            package(archive_path)
            with ZipFile(archive_path) as archive:
                names = set(archive.namelist())
                for name in (*PAGES, "site.css", "README.md"):
                    expected = f"syntyr-css-{version}/examples/business-starter/{name}"
                    self.assertTrue(expected in names, expected)
                self.assertIn(f"syntyr-css-{version}/dist/syntyr.core.css", names)
                self.assertIn(f"syntyr-css-{version}/dist/syntyr.recipes.css", names)

    def test_public_site_outputs_starter_but_excludes_fictional_pages_from_sitemap(self):
        from scripts.build_cloudflare_site import source_files, SITE_URL
        files = source_files()
        for name in PAGES:
            path = f"examples/business-starter/{name}"
            self.assertTrue(path in files, path)
            self.assertIn('name="robots" content="noindex,follow"', files[path].decode())
            self.assertNotIn(SITE_URL + "/" + path.removesuffix(".html"), files["sitemap.xml"].decode())
        self.assertIn("examples/business-starter/site.css", files)


if __name__ == "__main__":
    unittest.main()
