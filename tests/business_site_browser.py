"""Optional real-browser checks for the four-page Syntyr business starter.

python3 tests/business_site_browser.py --browsers chromium,firefox,webkit
Playwright and browser engines are developer-only; consumers need no JS.
"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import shutil

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "examples" / "business-starter"
PAGES = ("index.html", "services.html", "case-study.html", "contact.html")


def verify_browser(browser, name: str) -> int:
    passed = 0
    for filename in PAGES:
        for width, enlarged in ((320, False), (390, False), (768, False), (1280, False), (320, True)):
            context = browser.new_context(viewport={"width": width, "height": 840}, device_scale_factor=1)
            page = context.new_page()
            errors: list[str] = []
            page.on("pageerror", lambda e: errors.append(str(e)))
            try:
                page.goto((SITE / filename).as_uri(), wait_until="load")
                if enlarged:
                    page.add_style_tag(content="html { font-size: 32px !important; }")
                # The Syntyr stylesheet must load; unstyled HTML can otherwise pass reflow.
                accent = page.locator("body").evaluate(
                    "(e) => getComputedStyle(e).getPropertyValue('--syn-accent').trim()"
                )
                assert accent, (name, filename, "Syntyr styles did not load")
                metrics = page.evaluate("""() => ({
                    scroll: document.documentElement.scrollWidth,
                    client: document.documentElement.clientWidth,
                    heading: document.querySelector('h1')?.getBoundingClientRect().width
                })""")
                assert metrics["scroll"] <= metrics["client"] + 1, (
                    name, filename, width, enlarged, metrics
                )
                assert metrics["heading"] > 0, (name, filename, width)
                assert page.locator('nav[aria-label="Primary navigation"] a[aria-current="page"]').count() == 1
                assert not errors, (name, filename, errors)
                if filename == "contact.html":
                    assert not page.locator('button[type="submit"]').is_enabled()
                passed += 1
            finally:
                context.close()

    context = browser.new_context(viewport={"width": 390, "height": 844})
    page = context.new_page()
    try:
        page.goto((SITE / "index.html").as_uri(), wait_until="load")
        page.locator('nav[aria-label="Primary navigation"] a[href="contact.html"]').click()
        assert page.url.endswith("/contact.html"), (name, "navigation", page.url)
        assert page.locator("h1").inner_text().startswith("Tell us"), (name, "navigation")
        passed += 1
    finally:
        context.close()
    return passed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--browsers", default="chromium")
    args = parser.parse_args()
    names = [n.strip() for n in args.browsers.split(",") if n.strip()]
    with sync_playwright() as p:
        for name in names:
            if name not in {"chromium", "firefox", "webkit"}:
                parser.error(f"Unsupported browser: {name}")
            options = {"headless": True}
            if name == "chromium":
                chrome = os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE") or shutil.which("chromium")
                if chrome:
                    options.update(executable_path=chrome, args=["--no-sandbox"])
            browser = getattr(p, name).launch(**options)
            try:
                passed = verify_browser(browser, name)
                print(f"PASS {name}: {passed} real-browser cases")
            finally:
                browser.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
