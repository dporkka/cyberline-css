"""Native-first business task page and opt-in cover layout contracts."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.fragment_links = []
        self.labels = []
        self.forms = []
        self.controls = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if a.get("id"):
            self.ids.add(a["id"])
        if tag == "a" and a.get("href", "").startswith("#"):
            self.fragment_links.append(a["href"][1:])
        if tag == "label" and a.get("for"):
            self.labels.append(a["for"])
        if tag == "form":
            self.forms.append(a)
        if tag in ("input", "select", "textarea") and a.get("id"):
            self.controls[a["id"]] = a


class IntrinsicTaskPageContract(unittest.TestCase):
    def test_cover_is_opt_in_scoped_and_has_no_runtime(self):
        css = (ROOT / "src/recipes.css").read_text()
        for token in (".syn-cover", ".syn-cover-main", "--syn-cover-min-size", "margin-block: auto"):
            self.assertIn(token, css)
        self.assertIn("@layer syn.recipes", css)
        self.assertNotIn("@import", css)
        self.assertNotIn("!important", css)
        self.assertIn(".syn-cover", (ROOT / "dist/syntyr.recipes.css").read_text())
        self.assertNotIn(".syn-cover", (ROOT / "dist/syntyr.core.css").read_text())

    def test_app_shell_selector_survives_cover_insertion(self):
        # A literal backslash-n between nested rules changes the following
        # selector into an invalid/nonmatching type selector. It previously
        # escaped our source and generated-bundle checks.
        for path in ("src/recipes.css", "dist/syntyr.recipes.css", "dist/syntyr.all.css"):
            with self.subTest(path=path):
                css = (ROOT / path).read_text()
                self.assertNotIn(r"\n    /* Application shell", css)
                self.assertIn("\n    /* Application shell:", css)
                self.assertIn("&.syn-app-shell {", css)

    def test_task_page_is_covered_by_accessibility_audit(self):
        source = (ROOT / "tests/axe_audit.py").read_text()
        self.assertIn('"examples/intrinsic-task-page.html"', source)

    def test_task_page_uses_semantics_and_server_owned_behavior(self):
        html = (ROOT / "examples/intrinsic-task-page.html").read_text()
        self.assertIn('syntyr.recipes.css', html)
        self.assertIn('syntyr.core.css', html)
        self.assertIn('class="syn-sidebar"', html)
        self.assertIn('class="syn-cover"', html)
        self.assertIn('class="syn-cover-main syn-empty"', html)
        self.assertIn('class="syn-region"', html)
        self.assertIn('class="syn-error-summary"', html)
        self.assertIn('tabindex="-1" role="region" aria-labelledby="error-title"', html)
        self.assertIn('aria-invalid="true"', html)
        self.assertIn('aria-describedby=', html)
        self.assertNotIn("<script", html.lower())
        self.assertNotIn("onclick=", html.lower())
        parser = PageParser()
        parser.feed(html)
        self.assertGreaterEqual(len(parser.forms), 1)
        self.assertTrue(all(f.get("method") in ("get", "post") and f.get("action") for f in parser.forms))
        for item in parser.fragment_links + parser.labels:
            self.assertIn(item, parser.ids)
        for cid, attrs in parser.controls.items():
            if attrs.get("aria-describedby"):
                for desc in attrs["aria-describedby"].split():
                    self.assertIn(desc, parser.ids, cid)
            if attrs.get("aria-invalid") == "true":
                self.assertIn(cid, parser.labels)

    def test_example_is_published_and_documented(self):
        from scripts.build_cloudflare_site import source_files
        from scripts.build_cloudflare_site import NOINDEX_HTML
        self.assertTrue("examples/intrinsic-task-page.html" in source_files(), "public site must include new HTML demo")
        self.assertIn("examples/intrinsic-task-page.html", NOINDEX_HTML)
        self.assertIn('href="../examples/intrinsic-task-page.html"', (ROOT / "docs/index.html").read_text())
        recipes = (ROOT / "docs/recipes.md").read_text()
        self.assertIn("syn-cover", recipes)
        self.assertIn("../examples/intrinsic-task-page.html", recipes)
        self.assertIn("form error", recipes.lower())


if __name__ == "__main__":
    unittest.main()
