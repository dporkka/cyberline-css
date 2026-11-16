"""Optional developer-only browser checks for Syntyr Blocks gallery.

Run: python tests/blocks_browser.py --browsers chromium firefox --axe-file /tmp/axe.min.js
"""
from __future__ import annotations
import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import sys
from threading import Thread
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
GALLERY = (ROOT / "docs/blocks.html").as_uri()


def require(value, message):
    if not value:
        raise AssertionError(message)


def layout_check(browser, engine, width, scale):
    context = browser.new_context(viewport={"width": width, "height": 900})
    page = context.new_page()
    try:
        page.goto(GALLERY)
        page.evaluate("(scale) => {document.documentElement.style.fontSize = (16 * scale) + 'px';}", scale)
        metrics = page.evaluate("""() => {
            const d = document.documentElement;
            const controls = [...document.querySelectorAll('a,button,input,select,textarea,summary')]
              .filter(el => {
                if (el.closest('details:not([open])') && el.tagName !== 'SUMMARY') return false;
                const r = el.getBoundingClientRect(), s = getComputedStyle(el);
                if (s.display === 'none' || s.visibility === 'hidden' || !r.width || !r.height) return false;
                if (el.closest('.blocks-source, .blocks-icon-card pre, .syn-table-wrap')) return false;
                return r.left < -1 || r.right > innerWidth + 1;
              }).slice(0, 6).map(el => [
                el.tagName, (el.textContent || el.getAttribute('aria-label') || '').slice(0, 32),
                Math.round(el.getBoundingClientRect().left), Math.round(el.getBoundingClientRect().right)
              ]);
            const cards = [...document.querySelectorAll('[data-block-id]')];
            return {viewport: d.clientWidth, scroll: d.scrollWidth,
                    clipped: controls, cards: cards.length,
                    visible: cards.filter(card => !card.hidden).length};
        }""")
        require(metrics["cards"] == 20 and metrics["visible"] == 20,
                f"{engine} {width}px {scale}x: missing blocks {metrics}")
        require(metrics["scroll"] <= metrics["viewport"] + 1,
                f"{engine} {width}px {scale}x: overflow {metrics}")
        require(not metrics["clipped"],
                f"{engine} {width}px {scale}x: controls clipped {metrics}")
        if width == 390 and scale == 1:
            # Small text must not inherit the muted token against decorative radar rings.
            radar = page.locator(".syn-block-asset--radar")
            require(radar.count() == 1, f"{engine}: radar preview missing")
            for theme in ("studio", "grid", "noir", "industrial", "terminal", "corporate", "minimal"):
                page.locator("body.syn-root").evaluate("(e, value) => e.setAttribute('data-syn-theme', value)", theme)
                fg = radar.locator("span").evaluate("e => getComputedStyle(e).color")
                label = radar.locator("strong").evaluate("e => getComputedStyle(e).color")
                require(fg == label, f"{engine} {theme}: small radar caption is less legible than its label: {fg} / {label}")

    finally:
        context.close()


def progressive_checks(browser, engine, screenshots):
    context = browser.new_context(java_script_enabled=False, viewport={"width": 390, "height": 844})
    page = context.new_page()
    page.goto(GALLERY)
    require(page.locator("[data-block-id]").count() == 20, "No-JS: blocks missing")
    require(page.locator("[data-icon-id]").count() == 36, "No-JS: SVG icons missing")
    require(page.locator(".syn-block-asset").count() == 12, "No-JS: CSS assets missing")
    require(page.locator("#blocks-controls").is_hidden(), "No-JS: controls should be hidden")
    details = page.locator(".blocks-details").first
    details.locator("summary").focus()
    page.keyboard.press("Enter")
    require(details.get_attribute("open") is not None, "No-JS: keyboard disclosure failed")
    block_ax = page.locator('[data-block-id="hero-product"]').aria_snapshot()
    icon_ax = page.locator('[data-icon-id="search"]').aria_snapshot()
    require("View HTML source for Product launch hero" in block_ax,
            f"Screen-reader source disclosure lacks block context: {block_ax[-350:]}")
    require("SVG source for Search" in icon_ax,
            f"Screen-reader SVG source disclosure lacks icon context: {icon_ax}")
    context.close()

    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
    console_errors = []
    page.on("pageerror", lambda error: console_errors.append(str(error)))
    page.goto(GALLERY)
    require(page.locator("#blocks-controls").is_visible(), "JS: controls not revealed")
    require(page.get_by_role("searchbox", name="Search blocks").count() == 1,
            "Accessibility: search input lacks expected accessible name")
    require(page.get_by_role("button", name="Copy HTML for Product launch hero").count() == 1,
            "Accessibility: copy button lacks block context")
    require("20 of 20" in page.locator("#blocks-results").inner_text(), "JS: count wrong")
    page.locator("#blocks-search").fill("pricing")
    require(page.locator("[data-block-id]:visible").count() == 1, "JS: search wrong")
    page.locator("#blocks-search").fill("no-results-can-match-XYZ")
    require(page.locator("#blocks-empty").is_visible(), "JS: empty state missing")
    page.locator("#blocks-search").fill("")
    page.locator("#blocks-category").select_option("Technical")
    require(page.locator("[data-block-id]:visible").count() == 4, "JS: category filter wrong")
    page.locator("#blocks-category").select_option("all")
    page.locator("#blocks-theme").select_option("noir")
    require(page.locator('.blocks-preview > .syn-root[data-syn-theme="noir"]').count() == 20,
            "JS: theme did not apply to all previews")
    if screenshots:
        screenshots.mkdir(parents=True, exist_ok=True)
        page.screenshot(path=str(screenshots / f"blocks-{engine}-desktop.png"))
        page.set_viewport_size({"width": 390, "height": 844})
        page.screenshot(path=str(screenshots / f"blocks-{engine}-mobile.png"))
        page.set_viewport_size({"width": 1280, "height": 900})
    require(page.get_by_role("searchbox", name="Search icons").count() == 1, "Icon search missing")
    page.locator("#icons-search").fill("delete")
    require(page.locator("[data-icon-id]:visible").count() == 1, "Icon filter wrong")
    page.locator("#icons-search").fill("")
    page.locator("#icons-size").select_option("2rem")
    require(page.locator("#blocks-icons-grid").evaluate(
        'el => el.style.getPropertyValue("--syn-gallery-icon-size")') == "2rem", "Icon size not applied")
    page.locator("#icons-theme").select_option("noir")
    require(page.locator(".blocks-icons-section").get_attribute("data-syn-theme") == "noir",
            "Icon theme not applied")
    require(page.get_by_role("button", name="Copy SVG for Search").count() == 1,
            "Accessible SVG copy button missing")
    page.locator("[data-block-copy]").first.click()
    page.wait_for_function(
        "() => /copied|selected/i.test(document.querySelector('#blocks-results').textContent)",
        timeout=3000
    )
    status = page.locator("#blocks-results").inner_text().lower()
    require("copied" in status or "selected" in status, "JS: copy/fallback failed")
    require(not console_errors, f"{engine}: script errors {console_errors}")
    context.close()


class QuietStaticHandler(SimpleHTTPRequestHandler):
    """Test-server only; avoid polluting browser verification output."""
    def log_message(self, fmt, *args):
        pass


def live_clipboard_check(browser):
    """Verify actual clipboard output on a trustworthy localhost HTTP origin."""
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), partial(QuietStaticHandler, directory=str(ROOT))
    )
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        context = browser.new_context(permissions=["clipboard-read", "clipboard-write"])
        page = context.new_page()
        page.goto(f"http://127.0.0.1:{server.server_port}/docs/blocks.html")
        require(page.locator("#blocks-controls").is_visible(),
                "HTTP: controls not available")
        page.get_by_role("button", name="Copy HTML for Product launch hero").click()
        page.wait_for_function(
            "() => document.querySelector('#blocks-results').textContent.includes('HTML copied')",
            timeout=3000
        )
        clipboard = page.evaluate("navigator.clipboard.readText()")
        source = page.locator(".blocks-source code").first.text_content().strip()
        require(clipboard == source, "HTTP: clipboard differs from visible source")
        context.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def axe_check(browser, engine, axe_file):
    context = browser.new_context(viewport={"width": 1280, "height": 900})
    page = context.new_page()
    page.goto(GALLERY)
    page.add_script_tag(path=str(axe_file))
    result = page.evaluate("""async () => axe.run(document, {
        runOnly: {type: 'tag', values: ['wcag2a','wcag2aa','wcag21a','wcag21aa','wcag22aa']}
    })""")
    violations = []
    for entry in result["violations"]:
        violations.append({"rule": entry["id"], "impact": entry["impact"],
                           "targets": [n["target"] for n in entry["nodes"][:8]],
                           "summary": [n.get("failureSummary") for n in entry["nodes"][:3]]})
    print(f"AXE {engine}: {len(violations)} violations, {len(result['incomplete'])} incomplete")
    for entry in violations:
        print(f"  {entry['impact']} {entry['rule']}: {entry['targets']}")
    context.close()
    return violations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browsers", nargs="+", default=["chromium", "firefox"],
                        choices=["chromium", "firefox", "webkit"])
    parser.add_argument("--axe-file", type=Path)
    parser.add_argument("--screenshots", type=Path)
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    failures = []
    evidence = {"gallery": "docs/blocks.html", "engines": {}, "failures": failures}
    with sync_playwright() as pw:
        for engine in args.browsers:
            try:
                browser = getattr(pw, engine).launch(headless=True)
            except Exception as exc:
                failures.append(f"BLOCKED {engine}: {str(exc)[:240]}")
                continue
            item = {"layout_cases": [], "axe": None}
            evidence["engines"][engine] = item
            for width, scale in ((320, 1), (320, 1.5), (320, 2),
                                 (390, 1), (390, 2), (768, 1.5), (1280, 1)):
                try:
                    layout_check(browser, engine, width, scale)
                    item["layout_cases"].append([width, scale, "pass"])
                except Exception as exc:
                    failures.append(str(exc))
                    item["layout_cases"].append([width, scale, "fail"])
            try:
                progressive_checks(browser, engine, args.screenshots)
                item["progressive"] = "pass"
            except Exception as exc:
                failures.append(f"{engine} progressive: {exc}")
                item["progressive"] = "fail"
            if engine == "chromium":
                try:
                    live_clipboard_check(browser)
                    item["http_clipboard"] = "pass"
                except Exception as exc:
                    failures.append(f"{engine} HTTP clipboard: {exc}")
                    item["http_clipboard"] = "fail"
            if args.axe_file:
                try:
                    violations = axe_check(browser, engine, args.axe_file)
                    item["axe"] = violations
                    if violations:
                        failures.append(f"{engine}: axe violations {len(violations)}")
                except Exception as exc:
                    failures.append(f"{engine} axe blocked: {exc}")
            browser.close()
            print(f"COMPLETE {engine}: {len(item['layout_cases'])} layout cases")
    if args.report:
        args.report.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")
    for failure in failures:
        print("FAIL:", failure)
    if not failures:
        print("PASS: all requested browser checks")
    return int(bool(failures))


if __name__ == "__main__":
    sys.exit(main())
