"""Real-browser smoke tests for the docs-only geometry mixer and clipped frames.

Run: /tmp/syntyr-browser-env/bin/python tests/geometry_mixer_browser.py chromium
"""
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def verify(browser, width):
    context = browser.new_context(viewport={"width": width, "height": 900})
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto((ROOT / "docs/playground.html").as_uri(), wait_until="load")
    frame = page.locator("#geometry-preview")
    frame.wait_for()
    page.locator("#geometry-shape").select_option("bevel")
    page.locator("#geometry-cut-tl").fill("12")
    page.locator("#geometry-cut-tr").fill("28")
    page.locator("#geometry-stroke").fill("3")
    page.locator("#geometry-border-paint").select_option("gradient")
    page.locator("#geometry-inlay").check()
    styles = frame.evaluate("""e => {
      const before = getComputedStyle(e, '::before');
      const after = getComputedStyle(e, '::after');
      return { outer: before.clipPath, inner: after.clipPath,
               border: before.backgroundImage, inlay: after.backgroundImage,
               afterInset: after.inset, outerDisplay: before.display };
    }""")
    assert styles["outer"].startswith("polygon("), styles
    assert styles["inner"].startswith("polygon("), styles
    assert styles["outer"] != styles["inner"], "inner polygon failed to adjust for bevel stroke"
    assert "12px" in styles["outer"] and "28px" in styles["outer"], styles
    assert "linear-gradient(" in styles["border"], styles
    assert "linear-gradient(" in styles["inlay"], styles
    assert "--syn-frame-cut-tr: 28px" in page.locator("#geometry-code").input_value()
    assert "linear-gradient(" in page.locator("#geometry-code").input_value()

    page.locator("#geometry-shape").select_option("step")
    assert "syn-frame--step" in frame.get_attribute("class")
    assert frame.evaluate("e => getComputedStyle(e, '::before').clipPath").startswith("polygon(")
    page.locator("#geometry-shape").select_option("facet")
    assert "syn-frame--facet" in frame.get_attribute("class")
    assert frame.evaluate("e => getComputedStyle(e, '::before').clipPath").startswith("polygon(")

    page.locator("#playground-theme").select_option("noir")
    assert page.locator("#geometry-preview-theme").get_attribute("data-syn-theme") == "noir"
    page.locator("#geometry-copy").click()
    page.wait_for_function("""() => {
      const message = document.getElementById("geometry-status").textContent;
      return message === "HTML copied." || message === "HTML selected. Copy with your keyboard.";
    }""")
    assert not errors, errors
    assert page.locator("body").evaluate(
        "e => e.scrollWidth <= window.innerWidth + 1"
    ), f"horizontal overflow at width {width}"

    page.emulate_media(forced_colors="active")
    assert frame.evaluate("e => getComputedStyle(e, '::before').display") == "none"
    assert frame.evaluate("e => getComputedStyle(e).borderTopStyle") == "solid"
    context.close()


def main():
    with sync_playwright() as playwright:
        engine = sys.argv[1] if len(sys.argv) > 1 else "chromium"
        browser = getattr(playwright, engine).launch(headless=True)
        try:
            for width in (390, 1280):
                verify(browser, width)
                print(f"PASS {engine} {width}px geometry/gradient/mixer/forced-colors")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
