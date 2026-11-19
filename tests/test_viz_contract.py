"""Optional CSS-only data visualization contract."""
from html.parser import HTMLParser
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build import distributions  # noqa: E402
from scripts.build_cloudflare_site import source_files  # noqa: E402


class VizGalleryParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class VizContract(unittest.TestCase):
    def test_optional_distribution_is_independent_and_packaged(self):
        manifest = distributions()
        self.assertEqual(manifest["syntyr.viz.css"], ("viz.css",))
        self.assertIn("viz.css", manifest["syntyr.all.css"])
        for base in ("syntyr.core.css", "syntyr.css", "syntyr.recipes.css"):
            self.assertNotIn("viz.css", manifest[base])
        source = (ROOT / "src/viz.css").read_text()
        artifact = (ROOT / "dist/syntyr.viz.css").read_text()
        self.assertEqual(source.strip() + "\n", artifact)
        self.assertIn("dist/syntyr.viz.css", source_files())

    def test_viz_has_scoped_tokens_and_no_runtime_dependencies(self):
        css = (ROOT / "src/viz.css").read_text()
        self.assertIn("@layer syn.viz", css)
        self.assertIn(".syn-root [data-syn-theme]", css)
        for name in (
            "--syn-chart-1", "--syn-chart-2", "--syn-chart-3",
            "--syn-chart-4", "--syn-chart-grid", "--syn-chart-axis",
            "--syn-chart-tooltip-bg",
        ):
            with self.subTest(token=name):
                self.assertIn(name + ":", css)
        for forbidden in ("@import", "url(", "!important", "@keyframes", "animation:"):
            self.assertNotIn(forbidden, css)

    def test_four_microvisualizations_and_generic_chart_primitives(self):
        css = (ROOT / "src/viz.css").read_text()
        for selector in (
            ".syn-viz-sparkline", ".syn-viz-bars", ".syn-viz-bar-track",
            ".syn-viz-tracker", ".syn-viz-heatmap", ".syn-viz-cell",
            ".syn-chart", ".syn-chart-legend", ".syn-chart-grid",
            ".syn-chart-axis", ".syn-chart-tooltip",
        ):
            with self.subTest(selector=selector):
                self.assertIn(selector, css)
        self.assertIn("clamp(0%, calc(var(--syn-viz-value, 0) * 1%), 100%)", css)
        for level in range(5):
            self.assertIn(f'[data-syn-level="{level}"]', css)
        for state in ("healthy", "degraded", "down", "unknown"):
            self.assertIn(f'[data-syn-state="{state}"]', css)
        self.assertIn("forced-colors: active", css)

    def test_static_gallery_shows_all_seven_themes_and_data_alternatives(self):
        html = (ROOT / "examples/viz.html").read_text()
        parsed = VizGalleryParser()
        parsed.feed(html)
        for theme in ("grid", "noir", "studio", "industrial",
                      "terminal", "corporate", "minimal"):
            self.assertTrue(
                any(attrs.get("data-syn-theme") == theme for _, attrs in parsed.tags),
                f"Missing {theme} theme",
            )
        for cls in ("syn-viz-sparkline", "syn-viz-bars", "syn-viz-tracker", "syn-viz-heatmap"):
            self.assertIn(cls, html)
        self.assertIn("syntyr.viz.css", html)
        self.assertNotIn("<script", html.lower())
        self.assertTrue(any(tag == "table" for tag, _ in parsed.tags),
                        "Charts need inspectable underlying values")
        self.assertTrue(any(tag == "svg" and attrs.get("role") == "img"
                            for tag, attrs in parsed.tags))
        self.assertTrue(any(tag == "figcaption" for tag, _ in parsed.tags))
        self.assertTrue(any(tag == "a" and attrs.get("href", "").startswith("#")
                            for tag, attrs in parsed.tags))

    def test_documentation_and_discovery(self):
        readme = (ROOT / "README.md").read_text()
        guide = (ROOT / "docs/viz.md").read_text()
        gallery = (ROOT / "docs/index.html").read_text()
        self.assertIn("syntyr.viz.css", readme)
        self.assertIn("docs/viz.md", readme)
        self.assertIn("../examples/viz.html", gallery)
        self.assertIn("no JavaScript", guide)
        self.assertIn("screen reader", guide.lower())
        self.assertIn("Recharts", guide)
        self.assertIn("ECharts", guide)
        self.assertNotIn("<script", guide.lower())


if __name__ == "__main__":
    unittest.main()
