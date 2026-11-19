"""Optional Chromium visual regression for independently built consumer fixtures.

Requires developer-only packages: pip install playwright pillow
Build the example apps before running. No browser dependency ships with Syntyr.
Use --update-baselines only when reviewing intentional visual changes.
"""
from __future__ import annotations

import argparse
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import io
import os
from pathlib import Path
import threading
import unittest

from PIL import Image, ImageChops
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
BASELINES = ROOT / "tests" / "visual-baselines"
FIXTURES = ("tailwind-v4", "astro", "shadcn-bridge", "syntyr-shadcn-react")
UPDATE = False


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


@contextmanager
def serve(directory: Path):
    handler = partial(QuietHandler, directory=str(directory))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}"
    finally:
        server.shutdown()
        thread.join(timeout=3)
        server.server_close()


class SyntyrAdoptionVisual(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.pw = sync_playwright().start()
        browser_binary = os.environ.get("SYNTYR_CHROMIUM_EXECUTABLE")
        kwargs = {"headless": True}
        if browser_binary:
            kwargs["executable_path"] = browser_binary
            kwargs["args"] = ["--no-sandbox"]
        cls.browser = cls.pw.chromium.launch(**kwargs)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.pw.stop()

    def inspect_fixture(self, name):
        root = ROOT / "examples" / name
        root = root / "dist" if name in ("astro", "syntyr-shadcn-react") else root
        self.assertTrue((root / "index.html").is_file(), f"Build {name} before browser tests")
        page = self.browser.new_page(viewport={"width": 1100, "height": 760}, device_scale_factor=1, reduced_motion="reduce")
        errors = []
        page.on("pageerror", lambda err: errors.append(str(err)))
        page.on("response", lambda resp: errors.append(f"HTTP {resp.status}: {resp.url}") if resp.status >= 400 else None)
        with serve(root) as url:
            page.goto(f"{url}/index.html", wait_until="networkidle")
            self.assertTrue(page.locator(".syn-root").count())
            self.assertEqual(errors, [])
            overflow = page.evaluate("document.documentElement.scrollWidth > window.innerWidth")
            self.assertFalse(overflow, f"{name} viewport has horizontal overflow")
            if name == "tailwind-v4":
                self.assertEqual(page.locator("[data-syn-theme=noir]").evaluate(
                    "e => getComputedStyle(e).getPropertyValue('--syn-accent').trim()"), "#f1b574")
                self.assertEqual(page.locator(".text-syntyr-accent").first.evaluate(
                    "e => getComputedStyle(e).color"), "rgb(118, 231, 247)")
                button = page.locator("button.syn-button").first
                button.focus()
                self.assertEqual(button.evaluate("e => getComputedStyle(e).outlineWidth"), "3px")
                button.evaluate("e => e.blur()")
            if name == "shadcn-bridge":
                self.assertEqual(page.locator("#host").evaluate(
                    "e => getComputedStyle(e).getPropertyValue('--primary').trim()"), "")
                self.assertEqual(page.locator(".syn-shadcn").evaluate(
                    "e => getComputedStyle(e).getPropertyValue('--primary').trim()"), "#2458c6")
                self.assertEqual(page.locator("[data-syn-theme=noir]").evaluate(
                    "e => getComputedStyle(e).getPropertyValue('--primary').trim()"), "#f1b574")
                self.assertEqual(page.locator(".bg-primary").first.evaluate(
                    "e => getComputedStyle(e).backgroundColor"), "rgb(36, 88, 198)")
                self.assertEqual(page.locator("[data-syn-theme=noir] .bg-primary").evaluate(
                    "e => getComputedStyle(e).backgroundColor"), "rgb(241, 181, 116)")
            if name == "astro":
                self.assertEqual(page.locator("article.syn-panel").count(), 2)
                self.assertEqual(page.locator(".syn-button--primary").count(), 1)
            if name == "syntyr-shadcn-react":
                self.assertEqual(page.locator(".syn-shadcn").evaluate(
                    "e => getComputedStyle(e).getPropertyValue('--primary').trim()"), "#2458c6")
                self.assertEqual(page.locator("[data-syn-theme=noir]").evaluate(
                    "e => getComputedStyle(e).getPropertyValue('--primary').trim()"), "#f1b574")
                self.assertEqual(page.locator("#react-action").evaluate(
                    "e => getComputedStyle(e).backgroundColor"), "rgb(36, 88, 198)")
                self.assertEqual(page.locator("#noir-action").evaluate(
                    "e => getComputedStyle(e).backgroundColor"), "rgb(241, 181, 116)")
                self.assertEqual(page.locator("#aschild-link").get_attribute("data-slot"), "button")
                self.assertEqual(page.locator("#aschild-link").evaluate("e => e.tagName"), "A")
                self.assertTrue(page.locator("#disabled-action").is_disabled())
                page.locator("#react-action").click()
                self.assertEqual(page.locator("#react-action").inner_text(), "Increment 1")
                page.locator("#aschild-link").click()
                self.assertTrue(page.url.endswith("#details"))
                page.reload(wait_until="networkidle")
            image_bytes = page.locator("main").screenshot(animations="disabled")
        page.close()
        expected = BASELINES / f"syntyr-{name}.png"
        if UPDATE:
            BASELINES.mkdir(parents=True, exist_ok=True)
            expected.write_bytes(image_bytes)
            return
        self.assertTrue(expected.is_file(), f"Missing {expected}; run --update-baselines, review and commit")
        with Image.open(expected) as baseline, Image.open(io.BytesIO(image_bytes)) as rendered:
            original = baseline.convert("RGB")
            actual = rendered.convert("RGB")
            self.assertEqual(actual.size, original.size, f"{name} screenshot size changed")
            diff = ImageChops.difference(original, actual)
            changed = sum(max(pixel) > 24 for pixel in diff.get_flattened_data())
            fraction = changed / (actual.width * actual.height)
            self.assertLessEqual(fraction, 0.02, f"{name} visual drift: {fraction:.2%} pixels changed")

    def test_tailwind_v4(self):
        self.inspect_fixture("tailwind-v4")

    def test_astro(self):
        self.inspect_fixture("astro")

    def test_shadcn_bridge(self):
        self.inspect_fixture("shadcn-bridge")

    def test_generated_shadcn_react(self):
        self.inspect_fixture("syntyr-shadcn-react")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--update-baselines", action="store_true")
    args = parser.parse_args()
    UPDATE = args.update_baselines
    unittest.main(argv=[__file__], verbosity=2)
