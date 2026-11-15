"""Real browser stress test for text resize and 320px reflow.

Run in a developer-only Playwright environment:
    PLAYWRIGHT_CHROMIUM_EXECUTABLE=/usr/bin/chromium-browser python3 tests/reflow_test.py

This changes the document's root font size and is a *text-size stress test*,
not proof of real browser 200%/400% zoom or WCAG certification.
Horizontal scrolling *inside* the tabular-data widget remains allowed.
"""
import argparse
import os
from pathlib import Path
import shutil
import sys

from playwright.sync_api import sync_playwright
from browser_launch import launch_options

ROOT = Path(__file__).resolve().parents[1]
PAGES = (
    "index.html", "docs/index.html", "examples/console.html",
    "examples/resources.html", "examples/pricing.html",
    "docs/console-kit.html", "examples/saas.html",
    "examples/business.html", "examples/terminal.html",
         "examples/geometry-terminal.html",
         "examples/operations-console.html", "examples/themes.html",
    "examples/vertigo-admin.html", "examples/saas-workflows.html", "examples/minimalist-patterns.html", "examples/design-states.html", "examples/symbols.html", "examples/motion.html",
)


def check_page(browser, path: str, width: int, scale: float) -> None:
    context = browser.new_context(viewport={"width": width, "height": 850})
    page = context.new_page()
    try:
        page.goto((ROOT / path).as_uri())
        page.evaluate("(scale) => { document.documentElement.style.fontSize = (16 * scale) + 'px'; }", scale)
        data = page.evaluate("""() => {
            const root=document.documentElement;
            const clipped = Array.from(document.querySelectorAll('a, button, input, select, textarea, summary'))
              .filter(e => {
                const r=e.getBoundingClientRect(), s=getComputedStyle(e);
                if(s.display==='none'||s.visibility==='hidden'||r.width===0||r.height===0) return false;
                // Controls inside intentionally scrollable tables are exempt.
                if(e.closest('.syn-table-wrap')) return false;
                return r.left < -1 || r.right > innerWidth + 1;
              }).slice(0,5).map(e=>[e.tagName, e.textContent.trim().slice(0,35),
                 Math.round(e.getBoundingClientRect().left),Math.round(e.getBoundingClientRect().right)]);
            return {scrollWidth:root.scrollWidth, clientWidth:root.clientWidth, clipped};
        }""")
        assert data["scrollWidth"] <= data["clientWidth"] + 1 and not data["clipped"], (
            f"{path}: viewport={width}px, font scale={scale}x: {data}"
        )
    finally:
        context.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browsers", nargs="+", default=["chromium"],
                        choices=["chromium", "firefox", "webkit"])
    args = parser.parse_args()
    failed = 0
    with sync_playwright() as p:
        for engine in args.browsers:
            opts = launch_options(engine)
            try:
                browser = getattr(p, engine).launch(**opts)
            except Exception as e:
                failed += 1
                print(f"BLOCKED {engine}: {e}")
                continue
            for path in PAGES:
                for width, scale in ((320, 1), (320, 1.5), (320, 2), (390, 2)):
                    try:
                        check_page(browser, path, width, scale)
                    except Exception as e:
                        print(f"FAIL {engine}: {e}", flush=True)
                        failed += 1
            browser.close()
            print(f"FINISHED {engine}: {len(PAGES)*4} reflow cases", flush=True)
    return int(bool(failed))


if __name__ == "__main__":
    sys.exit(main())
