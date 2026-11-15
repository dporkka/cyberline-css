"""Optional browser-level forced-colors visual regression tests.

Requires developer-only Playwright and Chromium. The component library still
ships zero runtime JavaScript and has no Python package dependencies.
"""
import base64
import os
from pathlib import Path
import shutil
import unittest

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def ink_count(page, screenshot: bytes) -> int:
    """Count rendered dark glyph pixels inside a primary link's text band.

    Chromium's forced-colors text backplate can cover entire text runs even when
    computed foreground and background report excellent contrast. Sampling a
    *real screenshot* catches that rendering defect without image dependencies.
    """
    data_uri = "data:image/png;base64," + base64.b64encode(screenshot).decode("ascii")
    return page.evaluate("""async (url) => {
        const image = new Image();
        image.src = url;
        await image.decode();
        const canvas = document.createElement('canvas');
        canvas.width = image.width; canvas.height = image.height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(image, 0, 0);
        const {data} = ctx.getImageData(0, 0, image.width, image.height);
        let ink = 0;
        for (let y = Math.floor(image.height * .39); y < Math.ceil(image.height * .63); y++) {
            for (let x = Math.floor(image.width * .15); x < Math.floor(image.width * .85); x++) {
                const index = (y * image.width + x) * 4;
                if (data[index] < 170 || data[index + 1] < 170 || data[index + 2] < 170) ink++;
            }
        }
        return ink;
    }""", data_uri)


class ForcedColorsTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        exe = (os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
               or shutil.which("chromium") or shutil.which("chromium-browser"))
        kwargs = {"headless": True}
        if exe:
            kwargs.update(executable_path=exe, args=["--no-sandbox"])
        cls.browser = cls.playwright.chromium.launch(**kwargs)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.playwright.stop()

    def test_primary_action_text_is_rendered_in_forced_colors(self):
        context = self.browser.new_context(viewport={"width": 1280, "height": 900},
                                           forced_colors="active", color_scheme="light")
        try:
            page = context.new_page()
            page.goto((ROOT / "examples/themes.html").as_uri())
            self.assertTrue(page.evaluate("matchMedia('(forced-colors: active)').matches"))
            links = page.locator(".theme-tile .syn-button--primary")
            self.assertEqual(links.count(), 7)
            for i in range(links.count()):
                with self.subTest(theme=i):
                    button = links.nth(i)
                    self.assertEqual(button.inner_text(), "Explore components")
                    screenshot = button.screenshot()
                    self.assertGreater(
                        ink_count(page, screenshot), 12,
                        "Rendered action label was replaced by a solid forced-color text backplate"
                    )

        finally:
            context.close()

    def test_primary_actions_retain_focus_outline(self):
        context = self.browser.new_context(viewport={"width": 1280, "height": 900},
                                           forced_colors="active")
        try:
            page = context.new_page()
            page.goto((ROOT / "examples/themes.html").as_uri())
            for i in range(7):
                with self.subTest(theme=i):
                    link = page.locator(".theme-tile .syn-button--primary").nth(i)
                    link.focus()
                    style = link.evaluate("""e => {
                        const s = getComputedStyle(e);
                        return {outlineStyle:s.outlineStyle, outlineWidth:parseFloat(s.outlineWidth)};
                    }""")
                    self.assertNotEqual(style["outlineStyle"], "none")
                    self.assertGreaterEqual(style["outlineWidth"], 2)
        finally:
            context.close()

    def test_rtl_navigation_and_error_summary_survive_forced_colors(self):
        context = self.browser.new_context(viewport={"width": 390, "height": 820},
                                           forced_colors="active", color_scheme="light")
        try:
            page = context.new_page()
            page.goto((ROOT / "examples/mature-patterns.html").as_uri())
            self.assertTrue(page.evaluate("matchMedia('(forced-colors: active)').matches"))
            summary = page.locator(".syn-error-summary")
            border = summary.evaluate("""e => {
                const c = getComputedStyle(e);
                return {width: parseFloat(c.borderInlineStartWidth),
                        color: c.borderInlineStartColor, background: c.backgroundColor};
            }""")
            self.assertGreaterEqual(border["width"], 3)
            self.assertNotEqual(border["color"], border["background"])
            active = page.locator('[dir="rtl"] .syn-app-nav [aria-current="page"]')
            marker = active.evaluate("""e => {
                const c = getComputedStyle(e, '::before');
                return {width: parseFloat(c.width), background: c.backgroundColor};
            }""")
            self.assertGreaterEqual(marker["width"], 3)
            self.assertNotEqual(marker["background"], "rgba(0, 0, 0, 0)")
        finally:
            context.close()


if __name__ == "__main__":
    unittest.main()
