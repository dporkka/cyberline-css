"""Go stdlib SaaS example integration and distribution contracts."""
from hashlib import sha256
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "go-stdlib-saas"
PINNED_CORE_SHA256 = "8d6458bf1f2ae25098a733e7fb88a84260e54b8b285bf05ff07432cccfbdaa6e"


class GoStdlibSaaSContract(unittest.TestCase):
    def test_examples_are_discoverable_and_not_advertised_as_live_saas(self):
        home = (ROOT / "README.md").read_text(encoding="utf-8")
        kit = (ROOT / "docs/console-kit.html").read_text(encoding="utf-8")
        guide = (EXAMPLE / "README.md").read_text(encoding="utf-8")
        self.assertIn("examples/go-stdlib-saas/README.md", home)
        self.assertIn("tree/main/examples/go-stdlib-saas", kit)
        for boundary in ("read-only", "synthetic", "no authentication"):
            self.assertIn(boundary, (kit + guide).lower())
        self.assertIn("go test ./...", guide)

    def test_example_uses_published_css_with_no_browser_runtime_dependencies(self):
        css = (EXAMPLE / "assets/syntyr.core.css").read_bytes()
        self.assertEqual(sha256(css).hexdigest(), PINNED_CORE_SHA256)
        self.assertIn(b".syn-root", css)
        self.assertNotIn(b"@import url(", css.lower())
        self.assertFalse((EXAMPLE / "package.json").exists())
        self.assertEqual((EXAMPLE / "go.mod").read_text(encoding="utf-8").strip(),
                         "module example.com/syntyr-go-stdlib-saas\n\ngo 1.22")
        for filename in ("base", "overview", "customers", "detail"):
            template = (EXAMPLE / "templates" / f"{filename}.html").read_text(encoding="utf-8")
            self.assertNotIn("<script", template.lower())
            self.assertNotIn("https://", template.lower())
        self.assertIn('action="/customers" method="get"',
                      (EXAMPLE / "templates/customers.html").read_text(encoding="utf-8"))
        self.assertIn('href="/assets/syntyr.core.css"',
                      (EXAMPLE / "templates/base.html").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
