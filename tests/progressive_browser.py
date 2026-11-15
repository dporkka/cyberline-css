"""Browser-engine smoke tests for opt-in progressive Syntyr CSS.

Run with Python Playwright (dev-only):
  python3 tests/progressive_browser.py --browsers chromium firefox webkit
No web access, JavaScript runtime dependency, or external assets are needed.
"""
import argparse
import os
from pathlib import Path
import shutil
import sys
from playwright.sync_api import sync_playwright
from browser_launch import launch_options

ROOT = Path(__file__).resolve().parents[1]


def check(browser, name):
    css = "\n".join((ROOT / f"dist/syntyr.{module}.css").read_text()
                    for module in ("core", "semantic", "print"))
    context = browser.new_context(viewport={"width": 1280, "height": 850},
                                  reduced_motion="reduce")
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda exc: errors.append(str(exc)))
    page.set_content(f"""<style>{css}</style>
        <section class="syn-semantic" id="external" style="--syn-control-height:2.75rem">
          <button id="external-control" data-syn-semantic>Outside</button>
        </section>
        <main class="syn-root" data-syn-theme="auto" id="root">
          <section id="noir" data-syn-theme="noir">
            <div id="nested" data-syn-theme="auto">Nested automatic theme</div>
          </section>
          <section class="syn-semantic">
            <label for="lookup">Lookup</label>
            <input id="lookup" data-syn-semantic type="search">
            <button id="styled" data-syn-semantic>Search</button>
          </section>
          <div id="host" style="width:310px;max-width:100%">
            <div class="syn-layout">
              <article id="left">Left</article><article id="right">Right</article>
            </div>
          </div>
          <nav class="syn-app-nav" id="navigation"><a href="/next">Next</a></nav>
          <div class="syn-table-wrap" id="table">
            <table><tbody><tr><td id="row">Invoice data</td></tr></tbody></table>
          </div>
          <button id="print-action" class="syn-button syn-button--primary">Print</button>
        </main>""", wait_until="load")
    accent = lambda target: page.locator(target).evaluate("""e => {
        const probe = document.createElement('span');
        probe.style.color = 'var(--syn-accent)';
        e.append(probe);
        const resolved = getComputedStyle(probe).color;
        probe.remove();
        return resolved;
    }""")
    cssprop = lambda selector, prop: page.locator(selector).evaluate(
        "(e, p) => getComputedStyle(e).getPropertyValue(p).trim()", prop)
    bounds = lambda selector: page.locator(selector).bounding_box()

    assert cssprop("#styled", "min-height") == "44px", (name, "semantic opt-in")
    assert cssprop("#external-control", "min-height") != "44px", (name, "scope escape")
    for mode, expected in (("light", "rgb(36, 88, 198)"), ("dark", "rgb(118, 231, 247)")):
        page.emulate_media(color_scheme=mode)
        assert accent("#root") == expected, (name, mode, "root")
        assert accent("#nested") == expected, (name, mode, "nested")
        assert accent("#noir") == "rgb(241, 181, 116)", (name, mode, "explicit theme")

    assert bounds("#right")["y"] > bounds("#left")["y"], (name, "narrow layout")
    page.locator("#host").evaluate("e => e.style.width = '900px'")
    assert abs(bounds("#right")["y"] - bounds("#left")["y"]) <= 1, (name, "wide row")
    assert bounds("#right")["x"] > bounds("#left")["x"], (name, "wide columns")

    page.emulate_media(media="print")
    assert cssprop("#root", "background-color") == "rgb(255, 255, 255)", (name, "print background")
    assert cssprop("#root", "color") == "rgb(17, 17, 17)", (name, "print text")
    assert cssprop("#navigation", "display") == "none", (name, "print navigation")
    assert cssprop("#table", "overflow-x") == "visible", (name, "print tables")
    assert cssprop("#row", "visibility") == "visible", (name, "print data visibility")
    assert cssprop("#print-action", "color") == "rgb(17, 17, 17)", (name, "print action")
    assert cssprop("#print-action", "transition-duration") == "0s", (name, "print motion")
    assert not errors, errors
    context.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--browsers", nargs="+", choices=("chromium", "firefox", "webkit"),
                        default=("chromium", "firefox", "webkit"))
    args = parser.parse_args()
    failures = 0
    with sync_playwright() as playwright:
        for name in args.browsers:
            launch = launch_options(name)
            try:
                browser = getattr(playwright, name).launch(**launch)
            except Exception as exc:
                failures += 1
                print(f"BLOCKED {name}: {str(exc).splitlines()[0]}", flush=True)
                continue
            try:
                check(browser, name)
                print(f"PASS {name}: auto theme, scoping, layout, print and motion", flush=True)
            except Exception as exc:
                failures += 1
                print(f"FAIL {name}: {type(exc).__name__}: {exc}", flush=True)
            finally:
                browser.close()
    return bool(failures)


if __name__ == "__main__":
    sys.exit(main())
