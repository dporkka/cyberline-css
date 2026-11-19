"""Buyer-facing Console Kit discovery and honest prelaunch contact contract."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self.links.append(dict(attrs))


class CommercialFunnelTests(unittest.TestCase):
    def test_homepage_exposes_console_kit_in_nav_hero_and_product_preview(self):
        home = (ROOT / "index.html").read_text(encoding="utf-8")
        header = home.split("<header", 1)[1].split("</header>", 1)[0]
        hero = home.split('<section class="site-hero"', 1)[1].split("</section>", 1)[0]
        self.assertGreaterEqual(header.count('href="docs/console-kit.html"'), 2)
        self.assertIn('href="docs/console-kit.html"', hero)
        self.assertIn('id="console-kit"', home)
        self.assertIn('src="docs/previews/studio-overview.webp"', home)
        self.assertIn("PRIVATE PROTOTYPE", home)
        self.assertIn("NOT FOR SALE", home)

    def test_product_page_offers_private_contact_and_discloses_email_client(self):
        page = (ROOT / "docs/console-kit.html").read_text(encoding="utf-8")
        self.assertIn("REQUEST PRIVATE PREVIEW", page)
        self.assertIn('href="mailto:', page)
        self.assertIn("email app", page.lower())
        self.assertIn("no payment is being accepted", page.lower())
        self.assertIn("not a purchase form", page.lower())
        self.assertIn("current status", page.lower())
        self.assertIn("license", page.lower())
        self.assertIn("not implemented", page.lower())
        self.assertNotIn('action="/api/', page)

    def test_agent_index_discovers_the_non_sale_console_kit_research_page(self):
        index = (ROOT / "llms.txt").read_text(encoding="utf-8")
        self.assertIn("https://syntyr-css.pages.dev/docs/console-kit.html", index)
        self.assertIn("private prototype", index.lower())
        self.assertIn("not for sale", index.lower())
        self.assertIn("preview request", index.lower())
        self.assertIn("integration quote", index.lower())

    def test_service_contact_and_kit_contact_are_separate(self):
        page = (ROOT / "docs/console-kit.html").read_text(encoding="utf-8")
        self.assertIn("REQUEST AN INTEGRATION QUOTE", page)
        self.assertIn("Syntyr%20Console%20Kit", page)
        self.assertIn("integration%20quote", page)
        parser = Links()
        parser.feed(page)
        contact_links = [a.get("href", "") for a in parser.links if a.get("href", "").startswith("mailto:")]
        self.assertGreaterEqual(len(contact_links), 2)
        self.assertTrue(all("subject=" in href for href in contact_links))
        self.assertNotEqual(contact_links[0], contact_links[1])


if __name__ == "__main__":
    unittest.main()
