"""Optional real-browser exercise for the docs-only component playground.

Run: /path/to/playwright/python tests/playground_browser.py
"""
from pathlib import Path
import sys
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def verify(browser, viewport):
    context = browser.new_context(viewport={"width": viewport, "height": 850})
    page = context.new_page()
    page_errors = []
    page.on("pageerror", lambda err: page_errors.append(str(err)))
    page.goto((ROOT / "docs/playground.html").as_uri(), wait_until="load")
    frame = page.frame_locator("#playground-preview")
    frame.locator(".syn-stat").first.wait_for()
    assert frame.locator(".syn-stat").count() == 3
    accent = frame.locator("body").evaluate("e => getComputedStyle(e).getPropertyValue('--syn-accent').trim()")
    assert accent == "#2458c6", ("initial studio stylesheet did not load", accent)
    page.locator("#playground-theme").select_option("grid")
    frame.locator("body[data-syn-theme='grid']").wait_for()
    accent = frame.locator("body").evaluate("e => getComputedStyle(e).getPropertyValue('--syn-accent').trim()")
    assert accent == "#76e7f7", ("grid theme CSS did not load", accent)
    # Both sandboxed frames use identical markup but independently resolve
    # theme tokens. The selected viewport must remain an exact CSS width,
    # even inside a narrow scrolling comparison column.
    page.locator("#playground-compare").check()
    secondary = page.frame_locator("#playground-preview-compare")
    secondary.locator("body[data-syn-theme='grid']").wait_for()
    assert page.locator("#playground-secondary").is_visible()
    assert secondary.locator(".syn-stat").count() == 3
    assert frame.locator("body[data-syn-theme='grid']").count() == 1
    page.locator("#playground-compare-theme").select_option("noir")
    secondary.locator("body[data-syn-theme='noir']").wait_for()
    assert secondary.locator("body").evaluate("e => getComputedStyle(e).getPropertyValue('--syn-accent').trim()") == "#f1b574"
    page.locator("#playground-viewport").select_option("375")
    page.locator("#playground-density").select_option("compact")
    page.locator("#playground-radius").fill("18")
    frame.locator("body[data-syn-density='compact']").wait_for()
    assert page.locator("#playground-preview").evaluate("e => e.clientWidth") == 375
    assert page.locator("#playground-preview-compare").evaluate("e => e.clientWidth") == 375
    assert frame.locator("body").evaluate("e => getComputedStyle(e).getPropertyValue('--syn-radius').trim()") == "18px"
    configured = page.locator("#playground-configured-html").input_value()
    assert 'data-syn-theme="grid"' in configured
    assert 'data-syn-density="compact"' in configured
    assert '--syn-radius: 18px' in configured
    page.locator("#playground-copy-configured").click()
    page.wait_for_function("document.getElementById('playground-status').textContent.includes('Configured HTML')")
    page.locator("#playground-compare").uncheck()
    page.locator("#playground-secondary").wait_for(state="hidden")
    assert page.locator("#playground-compare-theme").is_disabled()
    page.locator("#playground-example").select_option("actions")
    frame.locator(".syn-panel").wait_for()
    panel_radius = frame.locator(".syn-panel").evaluate("e => getComputedStyle(e).borderTopLeftRadius")
    assert panel_radius == "12px", ("panel radius token not applied", panel_radius)
    page.locator("#playground-markup").fill('<div id="safe">Edited HTML</div><script>parent.document.body.dataset.injected="yes"</script>')
    frame.locator("#safe").wait_for()
    assert page.locator("body").get_attribute("data-injected") is None, "sandbox permitted parent script injection"
    assert page.locator("body").evaluate("e => e.scrollWidth <= window.innerWidth + 1"), "playground overflows"
    assert not page_errors, page_errors
    context.close()


def main():
    with sync_playwright() as playwright:
        browser_name = sys.argv[1] if len(sys.argv) > 1 else "firefox"
        browser = getattr(playwright, browser_name).launch(headless=True)
        try:
            for viewport in (390, 1280):
                verify(browser, viewport)
                print(f"PASS {browser_name} {viewport}px preview/theme/edit/sandbox")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
