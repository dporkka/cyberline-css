"""Contracts for optional deployed-site mobile audit, no Playwright required."""
import importlib.util
import sys
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def tool():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location("live_perf", ROOT / "scripts/audit_live_performance.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LivePerfTests(unittest.TestCase):
    def test_scope_rejects_credentials_and_non_http_urls(self):
        x = tool()
        self.assertEqual(x.validate_origin("https://syntyr-css.pages.dev/"),
                         "https://syntyr-css.pages.dev")
        for url in ("file:///etc/passwd", "http://user:pw@example.com/",
                    "https://example.com/path", "https://example.com/#frag",
                    "ftp://example.com"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                x.validate_origin(url)

    def test_metrics_ignore_unsupported_entries(self):
        x = tool()
        records = [{"lcp_ms": None, "cls": None, "css_transfer_bytes": 0},
                   {"lcp_ms": 150, "cls": 0, "css_transfer_bytes": 1024},
                   {"lcp_ms": 250, "cls": None, "css_transfer_bytes": 2048}]
        s = x.summarize(records)
        self.assertEqual(s["lcp_ms"]["median"], 200)
        self.assertEqual(s["lcp_ms"]["samples"], 2)
        self.assertEqual(s["cls"]["median"], 0)
        self.assertEqual(s["css_transfer_bytes"]["median"], 1024)

    def test_response_headers_distinguish_csp_cache_and_revalidation(self):
        x = tool()
        attrs = x.audit_headers({"cache-control": "public, max-age=0, must-revalidate",
                                 "x-content-type-options": "nosniff"})
        self.assertFalse(attrs["enforced_csp"])
        self.assertTrue(attrs["cache_requires_revalidation"])
        pinned = x.audit_headers({"cache-control": "public, max-age=31536000, immutable",
                                  "content-security-policy": "default-src 'self'"})
        self.assertFalse(pinned["cache_requires_revalidation"])
        self.assertTrue(pinned["enforced_csp"])

    def test_live_audit_is_documented_and_published(self):
        guide = (ROOT / "docs/live-performance-audit.md").read_text()
        for expected in ("scripts/audit_live_performance.py", "150 ms",
                         "Chromium", "0 automated", "CSP", "revalidat",
                         "not field Core Web Vitals"):
            self.assertIn(expected.lower(), guide.lower())
        self.assertIn('"live-performance-audit.md"',
                      (ROOT / "scripts/build_cloudflare_site.py").read_text())
        self.assertIn('href="live-performance-audit.html"',
                      (ROOT / "docs/guides.html").read_text())
        self.assertIn("https://syntyr-css.pages.dev/docs/live-performance-audit.md",
                      (ROOT / "llms.txt").read_text())

    def test_two_deployed_business_and_saas_targets_are_constant(self):
        x = tool()
        self.assertEqual([path for path in x.ROUTES],
                         ["/examples/business", "/examples/saas"])
        self.assertEqual(x.NETWORK["latency"], 150)
        self.assertEqual(x.NETWORK["downloadThroughput"], 200000)
        self.assertTrue((ROOT / "docs/performance-validation.md").is_file())


if __name__ == "__main__":
    unittest.main()
