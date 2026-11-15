"""Optional cross-engine runtime smoke: per-component CSS, columns and mobile density.

Use a development environment with Playwright installed:
  python3 tests/component_imports_browser.py
"""
from pathlib import Path
import os
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
URL = (ROOT / "examples/component-imports.html").as_uri()


def check(page, engine, width):
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.goto(URL)
    assert page.locator("link[rel='stylesheet']").count() == 7, (engine, "missing component styles")
    assert page.locator("#email").count() == 1
    actual = page.locator("body").evaluate("(el) => getComputedStyle(el).backgroundColor")
    assert actual != "rgba(0, 0, 0, 0)", (engine, "Syntyr tokens missing", actual)
    assert page.evaluate("() => document.documentElement.scrollWidth <= innerWidth + 1"), (engine, width, "page overflow")
    assert page.locator("ol.syn-u-columns > li").count() == 8
    xs = page.locator("ol.syn-u-columns > li").evaluate_all(
        "(els) => els.map(el => Math.round(el.getBoundingClientRect().x))"
    )
    if width == 320:
        assert len(set(xs)) == 1, (engine, "columns must collapse", xs)
    else:
        assert len(set(xs)) >= 2, (engine, "responsive columns not present", xs)
    for selector in ("#email", "button.syn-button", "a.syn-button--small"):
        height = page.locator(selector).evaluate("(el) => el.getBoundingClientRect().height")
        assert height >= 44, (engine, width, selector, height)
    text_size = page.locator("#email").evaluate("(el) => parseFloat(getComputedStyle(el).fontSize)")
    assert text_size >= 16, (engine, width, "focus zoom text size", text_size)
    if width == 320:
        page.evaluate("document.documentElement.style.fontSize = '200%'")
        assert page.evaluate("() => document.documentElement.scrollWidth <= innerWidth + 1"), (engine, width, "200% overflow")
        page.locator("#email").focus()
        page.keyboard.press("Tab")
        assert page.locator("button.syn-button").evaluate("(el) => document.activeElement === el"), (engine, "keyboard flow")
    assert errors == [], (engine, errors)


def main():
    with sync_playwright() as p:
        for name in ("chromium", "firefox", "webkit"):
            engine = getattr(p, name)
            executable = os.getenv(f"SYNTYR_TEST_{name.upper()}_EXECUTABLE")
            browser = engine.launch(**({"executable_path": executable} if executable else {}))
            try:
                for width in (320, 960):
                    page = browser.new_page(viewport={"width": width, "height": 900},
                                            has_touch=True, is_mobile=True)
                    try:
                        check(page, name, width)
                    finally:
                        page.close()
            finally:
                browser.close()
            print(f"PASS {name}: selective imports, columns, touch density, reflow, keyboard")


if __name__ == "__main__":
    main()
