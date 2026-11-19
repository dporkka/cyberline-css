"""Opt-in progressive-loading example and comparison-tool contracts."""
from html.parser import HTMLParser
from pathlib import Path
import importlib.util
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def load_tool():
    sys.path.insert(0, str(ROOT / "scripts"))
    spec = importlib.util.spec_from_file_location(
        "syntyr_loading_compare", ROOT / "scripts/perf_loading_compare.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    return tool


class ProgressiveLoadingContract(unittest.TestCase):
    def test_example_ships_stable_zero_script_resource_priorities(self):
        html = (ROOT / "examples/performance-first.html").read_text()
        parser = Tags()
        parser.feed(html)
        sheets = [attrs["href"] for tag, attrs in parser.tags
                  if tag == "link" and attrs.get("rel") == "stylesheet"]
        self.assertEqual(sheets, ["../dist/syntyr.core.css",
                                  "../dist/syntyr.recipes.css"])
        self.assertNotIn("<script", html.lower())
        self.assertNotIn("onload=", html.lower())
        self.assertNotIn('rel="preload"', html)
        images = [attrs for tag, attrs in parser.tags if tag == "img"]
        self.assertGreaterEqual(len(images), 2)
        hero = next(img for img in images if img.get("id") == "hero-image")
        self.assertEqual(hero["loading"], "eager")
        self.assertEqual(hero["fetchpriority"], "high")
        self.assertEqual(hero["decoding"], "async")
        self.assertEqual(hero["width"], "1200")
        self.assertEqual(hero["height"], "630")
        for img in images:
            self.assertTrue(img.get("alt"))
            self.assertTrue(img.get("width"))
            self.assertTrue(img.get("height"))
            self.assertTrue((ROOT / "examples" / img["src"]).resolve().is_file())
            if img is not hero:
                self.assertEqual(img.get("loading"), "lazy")
                self.assertNotEqual(img.get("fetchpriority"), "high")
        self.assertIn('class="syn-root', html)

    def test_progressive_loading_guide_is_publicly_discoverable(self):
        guide = (ROOT / "docs/progressive-loading.md").read_text()
        for required in ("critical CSS", "CSP", "LCP", "CLS", "warm", "cold",
                         "scripts/perf_loading_compare.py", "build_selective.py"):
            self.assertIn(required, guide)
        self.assertIn('href="progressive-loading.html"',
                      (ROOT / "docs/guides.html").read_text())
        self.assertIn("performance-first.html",
                      (ROOT / "docs/guides.html").read_text())
        site = (ROOT / "scripts/build_cloudflare_site.py").read_text()
        self.assertIn('"progressive-loading.md"', site)
        self.assertIn('"performance-first.html"', site)
        self.assertIn("docs/progressive-loading.md",
                      (ROOT / "README.md").read_text())

    def test_performance_baseline_does_not_claim_stale_size_gate(self):
        guide = (ROOT / "docs/performance-validation.md").read_text()
        self.assertNotIn("Both remain within the checked", guide)
        self.assertIn("no arbitrary", guide.lower())
        self.assertIn("not", guide.lower())

    def test_comparison_summary_preserves_missing_metrics_and_cache_split(self):
        tool = load_tool()
        samples = {
            "baseline": {
                "cold": [{"fcp_ms": 40, "lcp_ms": None, "cls": None, "css_requests": 2},
                         {"fcp_ms": 60, "lcp_ms": 55, "cls": None, "css_requests": 2}],
                "warm": [{"fcp_ms": 20, "lcp_ms": 30, "cls": 0, "css_requests": 1}],
            },
            "candidate": {
                "cold": [{"fcp_ms": 35, "lcp_ms": 45, "cls": 0, "css_requests": 1}],
                "warm": [{"fcp_ms": None, "lcp_ms": None, "cls": None, "css_requests": 1}],
            }
        }
        result = tool.summarize(samples, browser="chromium",
                                viewport="mobile", runs=2)
        self.assertEqual(result["results"]["baseline"]["cold"]["fcp_ms"]["median"], 50)
        self.assertEqual(result["results"]["baseline"]["cold"]["lcp_ms"]["median"], 55)
        self.assertIsNone(result["results"]["baseline"]["cold"]["cls"]["median"])
        self.assertIsNone(result["results"]["candidate"]["warm"]["fcp_ms"]["median"])
        self.assertEqual(result["results"]["baseline"]["warm"]["css_requests"]["median"], 1)
        self.assertIn("not field", " ".join(result["limitations"]))

    def test_urls_must_be_distinct_web_urls_without_credentials(self):
        tool = load_tool()
        tool.validate_urls("http://localhost:8000/a", "http://localhost:8000/b")
        for baseline, candidate in (
            ("file:///etc/passwd", "http://localhost/x"),
            ("https://user:pass@example.com/a", "https://example.com/b"),
            ("https://example.com/x", "https://example.com/x"),
        ):
            with self.subTest(url=baseline), self.assertRaises(ValueError):
                tool.validate_urls(baseline, candidate)


if __name__ == "__main__":
    unittest.main()
