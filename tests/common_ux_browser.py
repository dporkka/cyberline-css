"""Real-browser smoke for opt-in Syntyr common UI (requires Playwright)."""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
from urllib.parse import parse_qs, urlsplit

from playwright.sync_api import sync_playwright, expect

ROOT = Path(__file__).resolve().parents[1]


def main():
    handler = partial(SimpleHTTPRequestHandler, directory=str(ROOT))
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    url = f"http://127.0.0.1:{server.server_port}/examples/common-ux.html"
    try:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            context = browser.new_context(viewport={"width": 375, "height": 700})
            context.grant_permissions(["clipboard-read", "clipboard-write"], origin=f"http://127.0.0.1:{server.server_port}")
            page = context.new_page()
            errors = []
            page.on("pageerror", lambda error: errors.append(str(error)))
            page.goto(url, wait_until="networkidle")
            expect(page.locator("[data-syn-copy-target]")).to_be_enabled()

            page.get_by_role("button", name="Open actions").click()
            assert page.locator("#common-action-list").evaluate("(el) => el.matches(':popover-open')"), "popover didn't open"
            page.keyboard.press("Escape")
            assert not page.locator("#common-action-list").evaluate("(el) => el.matches(':popover-open')"), "popover didn't close"

            page.get_by_role("button", name="Open details").click()
            expect(page.locator("#common-drawer")).to_be_visible()
            assert page.locator("#common-drawer").evaluate("(el) => el.open")
            page.keyboard.press("Escape")
            assert not page.locator("#common-drawer").evaluate("(el) => el.open"), "drawer didn't close"

            for source, target in (
                ("gallery-studio", "Studio dashboard"),
                ("gallery-grid", "Grid resources"),
                ("gallery-noir", "Noir billing"),
            ):
                page.locator(f'button[commandfor="{source}"]').click()
                expect(page.locator(f"dialog#{source}")).to_be_visible()
                assert page.locator(f"dialog#{source} img").evaluate("(el) => el.complete && el.naturalWidth > 0")
                page.locator(f"dialog#{source} form button").click()
                assert not page.locator(f"dialog#{source}").evaluate("(el) => el.open")

            page.locator("#date-from").fill("2026-11-01")
            page.locator("#date-to").fill("2026-11-30")
            page.get_by_role("button", name="Apply dates").click()
            page.wait_for_url("**/common-ux.html?*")
            values = parse_qs(urlsplit(page.url).query)
            assert values["date_from"] == ["2026-11-01"]
            assert values["date_to"] == ["2026-11-30"]

            page.get_by_role("button", name="Copy snippet").click()
            expect(page.locator("[data-syn-feedback-status]")).to_contain_text("Copied to clipboard.")
            copied = page.evaluate("navigator.clipboard.readText()")
            assert copied == "Syntyr CSS: semantic HTML, native APIs, optional enhancements."
            assert not errors, f"JavaScript page errors: {errors}"

            page.set_viewport_size({"width": 320, "height": 680})
            assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1"), "horizontal overflow"

            # A rejected Clipboard API must not show a false success.
            failed = context.new_page()
            failed.add_init_script("""Object.defineProperty(navigator, 'clipboard', {
              configurable: true, value: {writeText: () => Promise.reject(new Error('denied'))}
            });""")
            failed.goto(url, wait_until="networkidle")
            failed.get_by_role("button", name="Copy snippet").click()
            expect(failed.locator("[data-syn-feedback-status]")).to_contain_text("Copy unavailable.")
            context.close()
            browser.close()
        print("PASS chromium: popover, drawer, three lightboxes, date GET, copy success/failure, 320px reflow")
    finally:
        server.shutdown()
        server.server_close()


if __name__ == "__main__":
    main()
