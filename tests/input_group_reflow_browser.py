"""Developer-only input-group reflow regression for Syntyr CSS.

Run with Python Playwright and installed browsers:
    python3 tests/input_group_reflow_browser.py --browsers chromium firefox webkit
"""
import argparse
from pathlib import Path
import sys

PAGE = (Path(__file__).resolve().parents[1] / "examples/form-composition.html").as_uri()


def check(browser, name, scale):
    context = browser.new_context(viewport={"width": 390, "height": 900})
    page = context.new_page()
    try:
        page.goto(PAGE, wait_until="load")
        page.evaluate("""scale => {
            document.documentElement.style.fontSize = String(16 * scale) + 'px';
            const group = document.querySelector('.syn-field-body .syn-input-group');
            group.style.inlineSize = '240px';
            group.querySelector('.syn-input-addon').textContent =
                'unbrokenverylongdomainname'.repeat(7) + '.example';
        }""", scale)
        metrics = page.evaluate("""() => {
            const group = document.querySelector('.syn-field-body .syn-input-group');
            const addon = group.querySelector('.syn-input-addon');
            const input = group.querySelector('input');
            return {
                overflow: group.scrollWidth - group.clientWidth,
                addonWidth: addon.getBoundingClientRect().width,
                inputWidth: input.getBoundingClientRect().width,
                groupWidth: group.getBoundingClientRect().width,
                addonRight: addon.getBoundingClientRect().right,
                groupRight: group.getBoundingClientRect().right,
            };
        }""")
        assert metrics["overflow"] <= 2, (name, scale, metrics)
        assert metrics["addonRight"] <= metrics["groupRight"] + 2, (name, scale, metrics)
        assert metrics["inputWidth"] >= 0, (name, scale, metrics)
        print("PASS", name, f"{scale}x-root-text", metrics, flush=True)
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browsers", nargs="+",
                        choices=("chromium", "firefox", "webkit"),
                        default=("chromium", "firefox", "webkit"))
    args = parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("BLOCKED: install developer-only Playwright", file=sys.stderr)
        return 2
    with sync_playwright() as pw:
        for name in args.browsers:
            try:
                browser = getattr(pw, name).launch()
            except Exception as error:
                print("BLOCKED", name, str(error), file=sys.stderr)
                return 2
            try:
                for scale in (1, 2, 4):
                    check(browser, name, scale)
            finally:
                browser.close()
    print("PASS all input-group reflow scenarios")
    return 0


if __name__ == "__main__":
    sys.exit(main())
