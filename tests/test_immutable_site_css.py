"""Live-site CSS gets content-addressed caching while public /dist stays stable."""
import importlib.util
import hashlib
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_site():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("site_hash", ROOT / "scripts/build_cloudflare_site.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ImmutableSiteCssTests(unittest.TestCase):
    def test_published_site_pages_reference_immutable_copied_css(self):
        b = load_site()
        files = b.source_files()
        path_core = None
        for page in ("index.html", "examples/business.html", "examples/saas.html",
                     "docs/index.html", "docs/guides.html"):
            with self.subTest(page=page):
                html = files[page].decode("utf-8")
                links = re.findall(r'href="(/_assets/css/[0-9a-f]{64}\.css)"', html)
                self.assertGreater(len(links), 0, (page, html[:150]))
                for uri in links:
                    name = uri.lstrip("/")
                    self.assertIn(name, files)
                    digest = name.rsplit("/", 1)[1].split(".")[0]
                    self.assertEqual(hashlib.sha256(files[name]).hexdigest(), digest)
                if page == "index.html":
                    path_core = links[0]
                if page == "examples/business.html":
                    self.assertEqual(links[0], path_core, "core stylesheet must share cache")
        # Preserve consumer URLs and frozen release files.
        self.assertIn("dist/syntyr.core.css", files)
        self.assertIn("v/0.3.0-alpha.4/syntyr.core.css", files)
        self.assertIn("/_assets/css/*", files["_headers"].decode())
        self.assertIn("max-age=31536000, immutable", files["_headers"].decode())

    def test_hosting_guidance_is_indexed_for_agents(self):
        index = (ROOT / "llms.txt").read_text()
        self.assertIn("https://syntyr-css.pages.dev/docs/cloudflare-hosting.md", index)

    def test_source_html_and_external_links_remain_unchanged(self):
        b = load_site()
        files = b.source_files()
        self.assertIn('href="dist/syntyr.core.css"',
                      (ROOT / "index.html").read_text())
        self.assertIn("https://", files["index.html"].decode())
        self.assertNotIn("/_assets/css/", (ROOT / "index.html").read_text())


if __name__ == "__main__":
    unittest.main()
