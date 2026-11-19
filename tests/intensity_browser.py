"""Optional browser verification for scoped effect intensity and geometry precedence.

Run: uv run --no-project --with playwright==1.64.1 python tests/intensity_browser.py
No runtime JavaScript is required by the SYNTYR distributions.
"""
from pathlib import Path
import os
import shutil

ROOT = Path(__file__).resolve().parents[1]


def verify(browser_type, name):
    options = {"headless": True}
    if name == "chromium":
        path = (os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
                or shutil.which("chromium") or shutil.which("chromium-browser"))
        if path:
            options.update(executable_path=path, args=["--no-sandbox"])
    browser = browser_type.launch(**options)
    try:
        for width in (390, 1280):
            page = browser.new_page(viewport={"width": width, "height": 860})
            core = (ROOT / "dist/syntyr.core.css").read_text()
            effects = (ROOT / "dist/syntyr.effects.css").read_text()
            geometry = (ROOT / "dist/syntyr.geometry.css").read_text()
            page.set_content(f"""<style>{core}</style><style>{effects}</style><style>{geometry}</style>
              <section class="syn-root" data-syn-theme="grid" data-syn-intensity="quiet">
                <article id="quiet" class="syn-panel syn-glow syn-grid-effect">Quiet</article>
                <section data-syn-intensity="cinematic" data-syn-theme="noir">
                  <article id="cinematic" class="syn-panel syn-glow syn-grid-effect">Cinematic</article>
                  <article id="notch" class="syn-panel syn-panel--cut syn-frame syn-frame--notch syn-frame--accent">Accent notch</article>
                  <article id="bracket" class="syn-panel syn-panel--cut syn-frame syn-frame--bracket">Bracket</article>
                  <section data-syn-intensity="standard">
                    <article id="reset" class="syn-panel syn-glow">Standard reset</article>
                  </section>
                </section>
              </section>""")
            quiet = page.locator("#quiet")
            cinematic = page.locator("#cinematic")
            read = lambda selector, token: page.locator(selector).evaluate(
                "(node, key) => getComputedStyle(node).getPropertyValue(key).trim()", token
            )
            assert read("#quiet", "--syn-glow-alpha") == "0%"
            assert read("#cinematic", "--syn-glow-alpha") == "25%"
            assert read("#reset", "--syn-glow-alpha") == "12%"
            assert read("#cinematic", "--syn-accent") == "#f1b574"
            assert read("#quiet", "--syn-accent") == "#76e7f7"
            assert quiet.evaluate("(e) => getComputedStyle(e).boxShadow") != cinematic.evaluate(
                "(e) => getComputedStyle(e).boxShadow")
            assert quiet.evaluate("(e) => getComputedStyle(e).backgroundImage") != cinematic.evaluate(
                "(e) => getComputedStyle(e).backgroundImage")
            for selector, shape in (("#notch", "polygon("), ("#bracket", "none")):
                styles = page.locator(selector).evaluate("""e => {
                  const host = e.getBoundingClientRect();
                  const pseudo = getComputedStyle(e, '::after');
                  return { width: parseFloat(pseudo.width), height: parseFloat(pseudo.height),
                           hostWidth: host.width, clip: pseudo.clipPath };
                }""")
                assert styles["width"] >= styles["hostWidth"] - 8, (name, width, selector, styles)
                assert styles["height"] >= 30, (name, width, selector, styles)
                assert (shape in styles["clip"]), (name, selector, styles)
            assert read("#notch", "--syn-frame-stroke") == "2px"
            page.emulate_media(forced_colors="active")
            assert page.locator("#notch").evaluate("e => getComputedStyle(e, '::after').display") == "none"
            assert page.locator("#notch").evaluate("e => getComputedStyle(e).borderTopWidth") == "1px"
            assert page.evaluate("document.documentElement.scrollWidth <= document.documentElement.clientWidth + 1")
            page.close()
    finally:
        browser.close()


def verify_page_layout(browser_type, name):
    options = {"headless": True}
    if name == "chromium":
        executable = (os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE")
                      or shutil.which("chromium") or shutil.which("chromium-browser"))
        if executable:
            options.update(executable_path=executable, args=["--no-sandbox"])
    browser = browser_type.launch(**options)
    try:
        for path in ("examples/intensity-geometry.html", "examples/operations-console.html",
                     "examples/landing.html"):
            for width in (390, 1280):
                page = browser.new_page(viewport={"width": width, "height": 860})
                errors = []
                page.on("pageerror", lambda error: errors.append(str(error)))
                url = (ROOT / path).as_uri()
                response = page.goto(url, wait_until="load")
                # Firefox returns no navigation response for local file:// pages.
                assert page.url == url and (response is None or response.ok), (name, path, page.url)
                assert page.locator("main").count() == 1, (name, path)
                assert page.locator("script").count() == 0, (name, path)
                overflow = page.evaluate(
                    "document.documentElement.scrollWidth - document.documentElement.clientWidth"
                )
                assert overflow <= 1, (name, path, width, overflow)
                assert not errors, (name, path, errors)
                page.close()
    finally:
        browser.close()


if __name__ == "__main__":
    import argparse
    from playwright.sync_api import sync_playwright
    parser = argparse.ArgumentParser()
    parser.add_argument("--browsers", default="chromium,firefox,webkit",
                        help="Comma-separated engines to verify (default: all three)")
    names = [name.strip() for name in parser.parse_args().browsers.split(",")]
    if not names or any(name not in ("chromium", "firefox", "webkit") for name in names):
        parser.error("Use chromium,firefox,webkit")
    with sync_playwright() as p:
        for engine in names:
            try:
                verify(getattr(p, engine), engine)
                verify_page_layout(getattr(p, engine), engine)
            except Exception as error:
                print(f"BLOCKED/FAILED {engine}: {error}")
                raise SystemExit(2) from error
            print(f"PASS {engine}: scoped intensity, inherited reset, frame precedence, forced colors (390/1280px)")
