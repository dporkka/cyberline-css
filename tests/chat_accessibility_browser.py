"""Optional browser regression for conversation and contrast CSS.

Run: uv run --offline --with playwright python tests/chat_accessibility_browser.py
No Playwright or browser JavaScript is required by Syntyr consumers.
"""
from pathlib import Path
from playwright.sync_api import sync_playwright

URL = (Path(__file__).resolve().parents[1] / "examples/chat-interface.html").as_uri()

FIXTURE = """
<div class="syn-root" data-syn-theme="studio" data-syn-contrast="more">
  <div id="more" class="syn-panel" data-syn-theme="grid">High contrast</div>
  <div data-syn-contrast="normal">
    <div id="normal" class="syn-panel" data-syn-theme="noir">Normal contrast</div>
    <div id="overlay" class="syn-surface--floating">Normal overlay</div>
    <div data-syn-contrast="more">
      <div id="reenabled" class="syn-panel" data-syn-theme="grid">High again</div>
    </div>
  </div>
  <div class="syn-composer">
    <label for="invalid">Message</label>
    <textarea class="syn-textarea" id="invalid" aria-invalid="true">Invalid</textarea>
  </div>
</div>
"""


def matches(actual, expected, tolerance=2):
    return all(abs(a - b) <= tolerance for a, b in zip(actual, expected))


def inspect(page):
    return page.evaluate("""() => {
      const pixel = color => {
        const canvas = document.createElement('canvas');
        canvas.width = canvas.height = 1;
        const ctx = canvas.getContext('2d');
        ctx.fillStyle = color;
        ctx.fillRect(0, 0, 1, 1);
        return [...ctx.getImageData(0, 0, 1, 1).data];
      };
      const inspect = id => {
        const element = document.getElementById(id);
        const style = getComputedStyle(element);
        const tokenColor = name => pixel(style.getPropertyValue(name).trim());
        return {
          border: pixel(style.borderTopColor),
          frame: tokenColor('--syn-frame'),
          strong: tokenColor('--syn-frame-strong'),
          danger: tokenColor('--syn-danger'),
          shadow: style.boxShadow
        };
      };
      return Object.fromEntries(['more', 'normal', 'reenabled', 'overlay', 'invalid']
        .map(id => [id, inspect(id)]));
    }""")


def main():
    passed = 0
    blocked = []
    with sync_playwright() as playwright:
        for name in ("chromium", "firefox", "webkit"):
            try:
                browser = getattr(playwright, name).launch(headless=True)
            except Exception as error:
                blocked.append((name, str(error).splitlines()[0]))
                continue
            try:
                page = browser.new_page(viewport={"width": 390, "height": 800})
                page.goto(URL, wait_until="load")
                page.evaluate("(html) => { document.body.innerHTML = html; }", FIXTURE)
                data = inspect(page)
                assert matches(data["more"]["border"], data["more"]["strong"]), (name, "nested more", data)
                assert matches(data["normal"]["border"][:3], data["normal"]["frame"][:3]), (name, "nested normal", data)
                assert 140 <= data["normal"]["border"][3] <= 170, (name, "normal alpha", data)
                assert matches(data["reenabled"]["border"], data["reenabled"]["strong"]), (name, "re-enabled more", data)
                assert data["overlay"]["shadow"] != "none", (name, "normal overlay lacks shadow", data)
                page.locator("#invalid").focus()
                data = inspect(page)
                assert matches(data["invalid"]["border"], data["invalid"]["danger"]), (name, "focused invalid", data)

                # OS preference must defeat explicit normal opt-out, including shadows.
                page.emulate_media(contrast="more")
                # Firefox applies emulated OS contrast reliably after navigation;
                # mirror the existing cross-engine smoke's reload discipline.
                page.reload(wait_until="load")
                page.evaluate("(html) => { document.body.innerHTML = html; }", FIXTURE)
                supports_os_emulation = page.evaluate(
                    "() => matchMedia('(prefers-contrast: more)').matches")
                if supports_os_emulation:
                    data = inspect(page)
                    assert data["overlay"]["shadow"] == "none", (name, "OS overlay", data)
                    assert matches(data["normal"]["border"], data["normal"]["strong"]), (name, "OS normal override", data)
                page.close()
                passed += 1
                print(f"PASS {name}: nested contrast, re-enable, invalid composer")
                if supports_os_emulation:
                    print(f"PASS {name}: OS contrast takes precedence, including overlay shadows")
                else:
                    print(f"UNVERIFIED {name}: OS contrast emulation unavailable")
            finally:
                browser.close()
    for name, reason in blocked:
        print(f"BLOCKED {name}: {reason}")
    if not passed:
        raise SystemExit("No browser engines verified")
    print(f"RESULT {passed} passed; {len(blocked)} engines unavailable")


if __name__ == "__main__":
    main()
