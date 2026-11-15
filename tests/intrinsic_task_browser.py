"""Optional three-engine smoke test for Syntyr's CSS-only task page.

Run (developer-only Playwright + browser dependencies required):
    python3 tests/intrinsic_task_browser.py --browsers chromium firefox webkit
No Playwright dependency is added to Syntyr's published CSS or packages.
"""
import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = (ROOT / "examples/intrinsic-task-page.html").as_uri()


def check(browser, name, width, font_scale=1, forced_colors="none"):
    context = browser.new_context(
        viewport={"width": width, "height": 900},
        forced_colors=forced_colors,
        reduced_motion="reduce",
    )
    page = context.new_page()
    try:
        page.goto(EXAMPLE, wait_until="load")
        page.evaluate("(scale) => document.documentElement.style.fontSize = String(16 * scale) + 'px'", font_scale)
        assert page.locator("script").count() == 0, (name, "site shipped scripts")
        summary = page.get_by_role("region", name="There is a problem")
        assert summary.count() == 1 and summary.get_attribute("tabindex") == "-1", (name, "focusable error summary")
        assert page.get_by_role("link", name="Enter a valid email address").get_attribute("href") == "#contact-email"
        field = page.get_by_label("Contact email")
        assert field.count() == 1 and field.get_attribute("aria-invalid") == "true"
        assert field.get_attribute("aria-describedby") == "contact-email-error"
        assert page.locator("#contact-email-error").count() == 1
        assert page.get_by_role("navigation", name="Account sections").count() == 1
        cover = page.locator(".syn-cover")
        assert cover.evaluate("e => getComputedStyle(e).display") == "flex"
        assert cover.evaluate("e => getComputedStyle(e).minBlockSize") != "0px"
        assert cover.locator(".syn-cover-main").count() == 1

        page.evaluate("""() => {
          const shell = document.createElement("section");
          shell.className = "syn-app-shell";
          shell.id = "shell-regression";
          document.body.appendChild(shell);
        }""")
        assert page.locator("#shell-regression").evaluate(
            "e => getComputedStyle(e).display") == "grid", (name, "app-shell selector regression")
        page.locator("#shell-regression").evaluate("e => e.remove()")
        # The root must not leak styles to host elements after opt-out.
        page.evaluate("document.body.classList.remove('syn-root')")
        assert cover.evaluate("e => getComputedStyle(e).display") != "flex", (name, "root leakage")
        page.evaluate("document.body.classList.add('syn-root')")

        sidebar = page.locator(".syn-sidebar")
        positions = sidebar.evaluate("""e => {
          const left = e.children[0].getBoundingClientRect();
          const right = e.children[1].getBoundingClientRect();
          return {sameRow: Math.abs(left.top - right.top) < 2,
            stacked: right.top >= left.bottom - 2};
        }""")
        if font_scale == 1:
            if width <= 390:
                assert positions["stacked"], (name, width, positions)
            if width >= 1280:
                assert positions["sameRow"], (name, width, positions)
        if width == 390 and font_scale == 1 and forced_colors == "none":
            sidebar.evaluate("e => e.style.inlineSize = '320px'")
            layout = sidebar.evaluate("""e => {
              const a = e.children[0].getBoundingClientRect();
              const b = e.children[1].getBoundingClientRect();
              return {inlineSize: e.getBoundingClientRect().width,
                overflow: e.scrollWidth - e.clientWidth,
                stacked: b.top >= a.bottom - 2};
            }""")
            assert abs(layout["inlineSize"] - 320) < 1 and layout["overflow"] <= 1 and layout["stacked"], layout

        overflow = page.evaluate("""() => document.documentElement.scrollWidth
            - document.documentElement.clientWidth""")
        if overflow > 2:
            offenders = page.evaluate("""() => Array.from(document.querySelectorAll('*'))
                .map(e => ({node: e.tagName.toLowerCase(), className: e.className,
                    id: e.id, right: e.getBoundingClientRect().right,
                    left: e.getBoundingClientRect().left}))
                .filter(e => e.right > document.documentElement.clientWidth + 2 || e.left < -2)
                .map(e => [e.node, e.id, e.className, Math.round(e.left), Math.round(e.right)])
                .slice(0, 20)""")
            raise AssertionError((name, width, font_scale, forced_colors,
                                  "page overflow", overflow, offenders))
        # Relevant forced-color elements have visible borders even when theme color is overridden.
        if forced_colors == "active":
            assert page.locator(".syn-panel").first.evaluate(
                "e => getComputedStyle(e).borderTopStyle") != "none"
        print("PASS", name, f"{width}px", f"{font_scale}x-root-text",
              forced_colors, flush=True)
    finally:
        context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browsers", nargs="+", choices=("chromium", "firefox", "webkit"),
                        default=("chromium", "firefox", "webkit"))
    args = parser.parse_args()
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print("BLOCKED: developer-only Playwright is unavailable", file=sys.stderr)
        return 2
    with sync_playwright() as playwright:
        for name in args.browsers:
            try:
                browser = getattr(playwright, name).launch()
            except Exception as exc:
                print(f"BLOCKED: {name} unavailable: {exc}", file=sys.stderr)
                return 2
            try:
                for width in (320, 390, 768, 1280):
                    check(browser, name, width)
                for factor in (2, 4):
                    check(browser, name, 390, factor)
                check(browser, name, 390, forced_colors="active")
            finally:
                browser.close()
    print("PASS all requested engines and task-page states")
    return 0


if __name__ == "__main__":
    sys.exit(main())
