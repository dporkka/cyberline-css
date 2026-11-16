"""Browser verification of actual RTL/LTR layout, not just CSS source strings.

Run in the optional developer Playwright environment:
    python3 tests/rtl_browser.py --browsers chromium firefox webkit
"""
import argparse
import os
from pathlib import Path
import sys

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = (ROOT / "examples/rtl-dashboard.html").as_uri()


def check(browser, width):
    context = browser.new_context(viewport={"width": width, "height": 900})
    page = context.new_page()
    try:
        page.goto(URL)
        result = page.evaluate("""() => {
          const css = (selector, pseudo) => getComputedStyle(document.querySelector(selector), pseudo);
          const panel = css("#rtl-panel", "::after");
          const timeline = css("#rtl-timeline > li", "::before");
          const classed = css("#rtl-table");
          const native = css("#rtl-native-table");
          const numeric = css("#rtl-table .syn-cell--numeric");
          return {
            documentDirection: css("html").direction,
            rtlTableDirection: classed.direction,
            rtlTableAlign: classed.textAlign,
            nativeTableAlign: native.textAlign,
            numericAlign: numeric.textAlign,
            englishDirection: css("#ltr-panel").direction,
            panelCutLeft: panel.left,
            panelCutShape: panel.clipPath,
            panelCutRight: panel.right,
            timelineDotRight: timeline.right,
            scrollWidth: document.documentElement.scrollWidth,
            viewportWidth: innerWidth,
          };
        }""")
        expected = {
            "documentDirection": "rtl",
            "rtlTableDirection": "rtl",
            "rtlTableAlign": "start",
            "nativeTableAlign": "start",
            "numericAlign": "end",
            "englishDirection": "ltr",
            "panelCutLeft": "-1px",
        }
        for key, value in expected.items():
            assert result[key] == value, f"{width}px {key} expected {value}: {result}"
        assert result["panelCutRight"] != "-1px", result
        assert result["timelineDotRight"] not in ("auto", ""), result
        assert result["scrollWidth"] <= result["viewportWidth"] + 1, result

        # The same stylesheet must reflow correctly when a component is
        # embedded into an LTR host. No special RTL stylesheet is allowed.
        page.locator("#rtl-panel").evaluate("e => e.dir = 'ltr'")
        assert page.locator("#rtl-panel").evaluate(
            "e => getComputedStyle(e, '::after').right"
        ) == "-1px"
        assert page.locator("#rtl-panel").evaluate(
            "e => getComputedStyle(e, '::after').clipPath"
        ) != result["panelCutShape"]

        page.get_by_role("button", name="خيارات العرض").click()
        assert page.locator("#rtl-menu").evaluate("e => e.matches(':popover-open')")
        assert page.locator("#rtl-menu").evaluate(
            "e => getComputedStyle(e).insetInlineEnd"
        ) == "16px"
        page.get_by_role("button", name="إغلاق").click()
        assert not page.locator("#rtl-menu").evaluate("e => e.matches(':popover-open')")
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browsers", nargs="+", default=["chromium"],
                        choices=["chromium", "firefox", "webkit"])
    args = parser.parse_args()
    failures = 0
    with sync_playwright() as playwright:
        for engine in args.browsers:
            try:
                launch_args = {"headless": True}
                if engine == "chromium" and os.environ.get("PLAYWRIGHT_CHROMIUM_EXECUTABLE"):
                    launch_args["executable_path"] = os.environ["PLAYWRIGHT_CHROMIUM_EXECUTABLE"]
                    launch_args["args"] = ["--no-sandbox"]
                browser = getattr(playwright, engine).launch(**launch_args)
            except Exception as exc:
                print(f"BLOCKED {engine}: {exc}")
                failures += 1
                continue
            try:
                for width in (320, 390, 1280):
                    try:
                        check(browser, width)
                        print(f"PASS {engine} {width}px")
                    except Exception as exc:
                        failures += 1
                        print(f"FAIL {engine} {width}px: {exc}")
            finally:
                browser.close()
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
