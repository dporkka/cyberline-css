"""Reproducible, opt-in Syntyr stylesheet delivery experiment."""
from pathlib import Path
import importlib.util
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))


def load_experiment():
    spec = importlib.util.spec_from_file_location(
        "loading_experiment", ROOT / "scripts/perf_loading_fixture.py")
    obj = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


class LoadingExperimentTests(unittest.TestCase):
    def test_three_variants_have_identical_page_body_and_assets(self):
        exp = load_experiment()
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            report = exp.generate(out)
            baseline = (out / "baseline.html").read_text()
            selective = (out / "selective.html").read_text()
            inline = (out / "inline.html").read_text()
            self.assertIn('href="dist/syntyr.core.css"', baseline)
            self.assertIn('href="dist/syntyr.recipes.css"', baseline)
            self.assertIn('href="dist/syntyr.route.css"', selective)
            self.assertNotIn("syntyr.core.css", selective)
            self.assertNotIn('rel="stylesheet"', inline)
            self.assertIn('data-syn-experiment="inline"', inline)
            self.assertNotIn("<script", inline.lower())
            self.assertNotIn("onload=", inline.lower())
            for body in (selective, inline):
                self.assertEqual(body[body.index("<body"):], baseline[baseline.index("<body"):])
            self.assertEqual((out / "dist/syntyr.route.css").read_text(),
                             inline.split('data-syn-experiment="inline">', 1)[1].split("</style>", 1)[0])
            self.assertTrue((out / "assets/og-syntyr.png").is_file())
            self.assertTrue((out / "previews/studio-overview.webp").is_file())
            self.assertTrue((out / "dist/syntyr.core.css").is_file())
            self.assertEqual(report["experiment"], "route-selective-vs-inline")
            self.assertGreater(report["bytes"]["baseline_css_raw"], report["bytes"]["selective_css_raw"])

    def test_fixture_server_uses_gzip_and_separate_cache_policies(self):
        import threading
        from http.server import ThreadingHTTPServer
        from urllib.request import Request, urlopen

        exp = load_experiment()
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory) / "site"
            exp.generate(folder)
            handler = exp.make_handler(folder, css_delay_ms=0)
            server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
            thread = threading.Thread(target=server.serve_forever, daemon=True)
            thread.start()
            try:
                address = f"http://127.0.0.1:{server.server_port}"
                for path, cache in (("/baseline.html", "no-store"),
                                    ("/dist/syntyr.core.css", "max-age=86400")):
                    with urlopen(Request(address + path, headers={"Accept-Encoding": "gzip"})) as response:
                        self.assertEqual(response.headers["Content-Encoding"], "gzip")
                        self.assertIn(cache, response.headers["Cache-Control"])
                        import gzip
                        self.assertGreater(len(gzip.decompress(response.read())), 100)
            finally:
                server.shutdown()
                server.server_close()
                thread.join(timeout=3)

    def test_experiment_output_rejects_symlink_and_repo_source_paths(self):
        exp = load_experiment()
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            destination = parent / "real"
            destination.mkdir()
            link = parent / "redirect"
            link.symlink_to(destination, target_is_directory=True)
            with self.assertRaises(ValueError):
                exp.generate(link)
            with self.assertRaises(ValueError):
                exp.generate(ROOT / "dist")

    def test_benchmark_guide_records_real_results_and_caveats(self):
        guide = (ROOT / "docs/progressive-loading.md").read_text()
        for phrase in ("perf_loading_fixture.py", "150 ms", "pixel-identical",
                       "Cold", "warm", "not automatic critical CSS extraction",
                       "WebKit", "synthetic"):
            self.assertIn(phrase.lower(), " ".join(guide.lower().split()))

    def test_comparison_includes_html_and_resource_transfer_metrics(self):
        from perf_loading_compare import METRICS, snapshot
        self.assertIn("total_transfer_bytes", METRICS)
        self.assertIn("html_transfer_bytes", METRICS)
        self.assertIn("css_transfer_bytes", METRICS)

        class Page:
            def evaluate(self, _):
                return {"fcp_ms": 20, "lcp_ms": 40, "cls": 0,
                        "html_transfer_bytes": 1000,
                        "css_transfer_bytes": 3000,
                        "total_transfer_bytes": 5000}

        result = snapshot(Page(), [object(), object()])
        self.assertEqual(result["total_transfer_bytes"], 5000)
        self.assertEqual(result["html_transfer_bytes"], 1000)
        self.assertEqual(result["css_transfer_bytes"], 3000)
        self.assertEqual(result["css_requests"], 2)


if __name__ == "__main__":
    unittest.main()
