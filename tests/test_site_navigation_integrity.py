"""Regression contracts for real navigation versus illustrative gallery markup."""
from html.parser import HTMLParser
from pathlib import Path
from posixpath import dirname, join, normpath
from urllib.parse import unquote, urlsplit
import re
import unittest

from scripts.build_cloudflare_site import source_files

ROOT = Path(__file__).resolve().parents[1]



class PageLinks(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "a" and attrs.get("href"):
            self.hrefs.append(attrs["href"])


class SiteNavigationIntegrityTests(unittest.TestCase):
    def test_block_previews_cannot_navigate_to_fictional_app_routes(self):
        html = (ROOT / "docs/blocks.html").read_text(encoding="utf-8")
        cards = re.findall(
            r'<div class="blocks-preview">\s*(.*?)\s*</div>\s*<details class="blocks-details">',
            html, flags=re.S,
        )
        self.assertEqual(len(cards), 20)
        demo_links = 0
        for card in cards:
            with self.subTest(card=card[:70]):
                self.assertNotRegex(card, r'<a\b[^>]*href="/')
                self.assertNotRegex(card, r'<form\b')
                demo_links += card.count('data-syn-preview-only="true"')
        self.assertGreater(demo_links, 5)
        # Preserve the real app-route placeholders in the copyable HTML source.
        self.assertIn('href=&quot;/checkout/team&quot;', html)
        self.assertIn('action=&quot;/settings&quot;', html)
        self.assertIn('Preview only', html)

    def test_human_facing_catalog_and_blocks_guides_use_html(self):
        for name in ("docs/catalog.html", "docs/blocks.html"):
            html = (ROOT / name).read_text(encoding="utf-8")
            self.assertNotRegex(html, r'<a\b[^>]*href="[^"]+\.md(?:[#?][^"]*)?"', name)
        self.assertIn('href="components.html"', (ROOT / "docs/catalog.html").read_text())
        self.assertIn('href="blocks-guide.html"', (ROOT / "docs/blocks.html").read_text())

    def test_both_homepage_navs_expose_docs_and_playground_without_losing_starter(self):
        html = (ROOT / "index.html").read_text(encoding="utf-8")
        for label in ("Main navigation", "Mobile navigation"):
            nav = re.search(
                r'<nav[^>]*aria-label="' + label + r'"[^>]*>(.*?)</nav>',
                html, flags=re.S,
            )
            self.assertIsNotNone(nav, label)
            for href in ("docs/reference.html", "docs/playground.html",
                         "examples/semantic-starter.html"):
                self.assertIn('href="' + href + '"', nav.group(1), label)

    def test_catalog_and_blocks_identify_unreleased_source_previews(self):
        for name in ("docs/catalog.html", "docs/blocks.html"):
            html = (ROOT / name).read_text(encoding="utf-8")
            self.assertIn("alpha.4", html, name)
            self.assertIn("alpha.5", html, name)
            self.assertIn("unreleased", html.lower(), name)

    def test_shipped_entrypoint_links_resolve_without_network_requests(self):
        """Check the actual published HTML, not just pre-build source paths."""
        files = source_files()
        paths = ("index.html", "docs/index.html", "docs/catalog.html",
                 "docs/blocks.html", "docs/guides.html", "docs/reference.html")
        parsed_pages = {}
        for name in paths:
            parser = PageLinks()
            parser.feed(files[name].decode("utf-8"))
            parsed_pages[name] = parser

        for name, page in parsed_pages.items():
            for href in page.hrefs:
                with self.subTest(page=name, href=href):
                    url = urlsplit(href)
                    if url.scheme or url.netloc or href.startswith("//"):
                        continue
                    path = unquote(url.path)
                    if not path:
                        target = name
                    elif path.startswith("/"):
                        target = normpath(path.lstrip("/"))
                    else:
                        target = normpath(join(dirname(name), path))
                    if target in ("", "."):
                        target = "index.html"
                    elif target.endswith("/") or target == "docs":
                        target = target.rstrip("/") + "/index.html"
                    self.assertIn(target, files, f"{name} links to missing {href}")
                    if url.fragment and target.endswith(".html"):
                        dest = parsed_pages.get(target)
                        if dest is None:
                            dest = PageLinks()
                            dest.feed(files[target].decode("utf-8"))
                        self.assertIn(unquote(url.fragment), dest.ids,
                                      f"{name} links to missing anchor {href}")

    def test_sitemap_does_not_invite_indexing_404(self):
        sitemap = source_files()["sitemap.xml"].decode()
        self.assertNotIn("/404.html", sitemap)
        self.assertIn("/docs/reference.html", sitemap)


if __name__ == "__main__":
    unittest.main()
