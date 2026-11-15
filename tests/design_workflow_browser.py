"""Browser-level verification of docs-only designer workflows.

uv run --no-project --with playwright==1.64.1 python tests/design_workflow_browser.py
"""
from pathlib import Path
import argparse
from playwright.sync_api import expect, sync_playwright

ROOT = Path(__file__).resolve().parents[1]


def check_playground(browser):
    page = browser.new_page(viewport={"width": 1280, "height": 850})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.add_init_script("""Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {writeText: async text => { window.__copied = text; }}
    });""")
    page.goto((ROOT / "docs/playground.html").as_uri())
    frame = page.frame_locator("#playground-preview")
    frame.locator(".syn-stat").first.wait_for()
    page.locator("#playground-size").select_option("375")
    assert page.locator("#playground-preview").evaluate(
        "e => Math.round(e.getBoundingClientRect().width)"
    ) == 375
    page.locator("#playground-density").select_option("compact")
    expect(frame.locator("body")).to_have_attribute("data-syn-density", "compact")
    page.locator("#playground-theme").select_option("noir")
    expect(frame.locator("body")).to_have_attribute("data-syn-theme", "noir")
    page.locator("#playground-example").select_option("form")
    page.locator("#playground-state").select_option("invalid")
    expect(frame.locator("#workspace-name")).to_have_attribute("aria-invalid", "true")
    assert "aria-invalid" not in page.locator("#playground-markup").input_value()
    page.locator("#playground-example").select_option("actions")
    page.locator("#playground-state").select_option("disabled")
    expect(frame.locator("button").first).to_be_disabled(timeout=5000)
    assert "disabled" not in page.locator("#playground-markup").input_value()
    page.locator("#playground-copy-setup").click()
    copied = page.evaluate("window.__copied")
    assert '<link rel="stylesheet" href="syntyr.all.css">' in copied
    assert 'data-syn-theme="noir"' in copied
    assert 'data-syn-density="compact"' in copied
    assert " disabled " not in copied
    page.locator("#playground-markup").fill(
        '<p id="safe">Static only</p><script>parent.__syntyrInjected = true</script>'
    )
    assert frame.locator("#safe").inner_text() == "Static only"
    assert page.evaluate("window.__syntyrInjected === undefined")
    expect(page.locator("#playground-status")).to_contain_text("no suitable native control")
    assert not errors, errors
    page.close()


def check_theme_editor(browser):
    page = browser.new_page(viewport={"width": 390, "height": 850})
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.add_init_script("""Object.defineProperty(navigator, 'clipboard', {
      configurable: true,
      value: {writeText: async text => { window.__copied = text; }}
    });""")
    page.goto((ROOT / "docs/theme-editor.html").as_uri())
    page.locator("#theme").select_option("studio")
    page.locator("#background").fill("#123456")
    page.locator("#surface").fill("#234567")
    page.locator("#text-color").fill("#ffffff")
    page.locator("#radius").fill("13")
    page.locator("#body-size").fill("18")
    assert page.locator("#preview p.syn-lede").evaluate("e => getComputedStyle(e).fontSize") == "18px"
    page.locator("#density").select_option("compact")
    css = page.locator("#generated-css").inner_text()
    assert "--syn-bg: #123456;" in css
    assert "--syn-surface: #234567;" in css
    assert "--syn-radius: 13px;" in css
    assert "--syn-type-body: 18px;" in css
    assert 'data-syn-density="compact"' in css
    assert "font-size: var(--syn-type-body);" in css
    # Verify the exported unlayered CSS also works when applied to a nested
    # region, not merely when the editor writes inline overrides.
    stylesheet = page.add_style_tag(content=css)
    page.locator("#preview").evaluate("""e => {
      e.style.removeProperty('font-size');
      e.style.removeProperty('--syn-type-body');
    }""")
    assert page.locator("#preview p.syn-lede").evaluate(
        "e => getComputedStyle(e).fontSize"
    ) == "18px"
    stylesheet.evaluate("e => e.remove()")
    page.locator("#preview").evaluate("""e => {
      e.style.setProperty('--syn-type-body', '18px');
      e.style.fontSize = '18px';
    }""")
    data = page.locator("#generated-tokens").inner_text()
    import json
    parsed = json.loads(data)
    assert parsed["tokens"]["--syn-radius"] == "13px"
    assert parsed["tokens"]["--syn-bg"] == "#123456"
    assert parsed["density"] == "compact"
    page.locator("#copy-tokens").click()
    assert json.loads(page.evaluate("window.__copied")) == parsed
    page.locator("#copy-css").click()
    assert "--syn-radius: 13px" in page.evaluate("window.__copied")
    assert page.locator("#preview").evaluate(
        "e => getComputedStyle(e).getPropertyValue('--syn-bg').trim()"
    ) == "#123456"
    page.locator("#accent").fill("#ffffff")
    page.locator("#on-accent").fill("#ffffff")
    assert page.locator("#contrast-result").get_attribute("data-result") == "fail"
    page.locator("#reset-theme").click()
    assert page.locator("#background").input_value() == "#f5f7fb"
    assert page.locator("#radius").input_value() == "4"
    assert page.locator("#body-size").input_value() == "16"
    assert page.locator("#contrast-result").get_attribute("data-result") == "pass"
    overflow = page.evaluate(
        "document.documentElement.scrollWidth - document.documentElement.clientWidth"
    )
    assert overflow <= 1, overflow
    assert not errors, errors
    page.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--browsers", nargs="+", choices=("chromium", "firefox", "webkit"),
                        default=("chromium", "firefox", "webkit"))
    args = parser.parse_args()
    with sync_playwright() as playwright:
        for engine in args.browsers:
            browser = getattr(playwright, engine).launch(headless=True)
            check_playground(browser)
            check_theme_editor(browser)
            browser.close()
            print(f"PASS docs design workflow: {engine}")
    print(f"PASS docs design workflow: {', '.join(args.browsers)}, responsive preview, states, themes and exports")
