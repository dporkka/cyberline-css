"""Opt-in real-browser smoke for the server HTML CSS bridge.

Run explicitly with Playwright installed:
    python3 tests/server_framework_browser.py --browsers chromium,firefox,webkit

No web server, framework client, or JavaScript runtime is loaded in Syntyr.
This tests computed CSS and preservation of native DOM/focus.
"""
from __future__ import annotations

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

HTML = """
<!doctype html>
<html lang="en"><body>
<section class="syn-root" data-syn-theme="studio">
  <button id="normal" class="syn-button" type="button">Idle</button>
  <button id="disabled" class="syn-button" type="button" disabled>Disabled</button>
  <button id="livewire" class="syn-button" type="submit" disabled data-loading>Saving</button>
  <button id="htmx" class="syn-button htmx-request" type="button">Fetching</button>
  <button id="phx-click" class="syn-button phx-click-loading" type="button">Saving</button>
  <button id="generic" class="syn-button" data-syn-state="loading" type="button">Working</button>
  <form class="phx-submit-loading">
    <button id="phx-submit" class="syn-button" type="submit" disabled>Sending</button>
  </form>
  <form aria-busy="true" data-turbo-frame="results">
    <button id="turbo-form" class="syn-button" type="submit" disabled>Searching</button>
  </form>
  <turbo-frame id="results" busy>
    <button id="turbo-frame" class="syn-button" type="button">Refreshing</button>
  </turbo-frame>
  <label for="search">Search</label>
  <input id="search" class="syn-input" value="Campaign"/>
</section>
<button id="host" class="syn-button" data-loading type="button">Host button</button>
</body></html>
"""


def check(browser_type):
    browser = browser_type.launch(headless=True)
    try:
        page = browser.new_page()
        page.set_content(HTML)
        page.add_style_tag(content=(ROOT / "dist/syntyr.core.css").read_text(encoding="utf-8"))
        page.add_style_tag(content=(ROOT / "dist/syntyr.server.css").read_text(encoding="utf-8"))
        cursor = lambda identifier: page.locator(f"#{identifier}").evaluate(
            "(node) => getComputedStyle(node).cursor"
        )
        assert cursor("normal") == "pointer"
        assert cursor("disabled") == "not-allowed"
        assert cursor("host") != "progress", "Bridge must not style host app siblings"
        for identifier in (
            "livewire", "htmx", "phx-click", "generic", "phx-submit", "turbo-form", "turbo-frame",
        ):
            assert cursor(identifier) == "progress", f"{identifier}: got {cursor(identifier)}"
        page.locator("#search").focus()
        page.locator("#generic").evaluate(
            "(node) => {node.removeAttribute('data-syn-state'); node.setAttribute('aria-busy', 'true')}"
        )
        assert page.locator("#search").evaluate("(node) => document.activeElement === node")
        assert cursor("generic") == "progress", "Core aria-busy cursor must remain supported"
        print(f"{browser_type.name}: PASS (7 request states, disabled, scope, focus)")
    finally:
        browser.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--browsers", default="chromium", help="comma-separated Playwright browser names")
    args = parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as error:
        raise SystemExit("Optional Playwright not installed; install as a dev-only test dependency") from error
    with sync_playwright() as playwright:
        for name in args.browsers.split(","):
            if name not in ("chromium", "firefox", "webkit"):
                parser.error(f"Unsupported browser: {name}")
            check(getattr(playwright, name))


if __name__ == "__main__":
    main()
