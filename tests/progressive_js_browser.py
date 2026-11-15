"""Browser regression tests for opt-in Syntyr progressive enhancement.

Run with: uv run --with playwright python tests/progressive_js_browser.py
Requires local Playwright browsers. No production Node dependency.
"""
from contextlib import contextmanager
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import os
import shutil
import threading
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]


@contextmanager
def site():
    class QuietHandler(SimpleHTTPRequestHandler):
        def log_message(self, *_args):
            pass
    server = ThreadingHTTPServer(("127.0.0.1", 0),
                                 partial(QuietHandler, directory=str(ROOT)))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{server.server_port}/examples/progressive-js.html"
    finally:
        server.shutdown()
        server.server_close()
        thread.join()


def test_browser(browser, url, name):
    disabled = browser.new_context(java_script_enabled=False)
    page = disabled.new_page()
    page.goto(url)
    assert page.locator("table tbody tr").count() == 4
    assert page.locator("[data-syn-point]").count() == 4
    assert page.get_by_text("Always readable without scripts").is_visible()
    assert page.locator("[data-syn-motion-js]").first.is_visible()
    disabled.close()

    context = browser.new_context(reduced_motion="no-preference")
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(url)
    page.wait_for_function("document.documentElement.dataset.synDemoReady === 'true'")
    assert not errors, errors
    point = page.locator("[data-syn-point]").first
    assert point.get_attribute("tabindex") == "0"
    point.focus()
    assert page.locator(".syn-chart-tooltip:not([hidden])").count() == 1
    assert "Jan" in page.locator(".syn-chart-tooltip:not([hidden])").inner_text()
    page.keyboard.press("ArrowRight")
    assert page.locator("[data-syn-point]").nth(1).evaluate("(el)=>document.activeElement===el")
    crosshair = page.locator("[data-syn-crosshair]")
    assert crosshair.get_attribute("hidden") is None
    assert crosshair.get_attribute("x1") == "100"
    page.keyboard.press("End")
    assert page.locator("[data-syn-point]").nth(3).evaluate("(el)=>document.activeElement===el")
    page.keyboard.press("Home")
    assert point.evaluate("(el)=>document.activeElement===el")
    page.keyboard.press("Escape")
    assert page.locator(".syn-chart-tooltip:not([hidden])").count() == 0
    point.hover()
    assert page.locator(".syn-chart-tooltip:not([hidden])").count() == 1

    resized = page.evaluate("""async () => {
      const chart = document.querySelector('[data-syn-viz="points"]');
      return await new Promise((resolve) => {
        const timeout = setTimeout(() => resolve(null), 1500);
        chart.addEventListener('syntyr:viz:resize', (event) => {
          clearTimeout(timeout);
          resolve(event.detail);
        }, {once: true});
        chart.style.width = '300px';
      });
    }""")
    assert resized and resized["width"] > 0, (name, "resize event", resized)
    page.locator('[data-syn-viz="points"]').evaluate("(chart) => chart.style.removeProperty('width')")
    playing = page.evaluate("""async () => {
      const {enhanceMotion} = await import('/dist/syntyr.motion.js');
      const motion = enhanceMotion(document.querySelector('.syn-root'));
      const node = document.querySelector('[data-syn-motion-js]');
      const first = motion.play(node, 'enter');
      const second = motion.play(node, 'fade');
      return {first: first?.playState, second: second?.playState};
    }""")
    assert playing == {"first": "idle", "second": "running"}, playing
    page.emulate_media(reduced_motion="reduce")
    page.wait_for_function("document.querySelector('[data-syn-motion-js]').getAnimations().length === 0")
    page.emulate_media(reduced_motion="no-preference")
    page.set_viewport_size({"width": 320, "height": 740})
    assert page.evaluate("document.documentElement.scrollWidth - document.documentElement.clientWidth") <= 1, "mobile horizontal overflow"
    point.hover()
    bounds = page.locator(".syn-chart-tooltip:not([hidden])").bounding_box()
    assert bounds["x"] >= 0 and bounds["x"] + bounds["width"] <= 321, bounds

    state = page.evaluate("""async () => {
      const {enhanceViz} = await import('/dist/syntyr.viz.js');
      const {enhanceMotion} = await import('/dist/syntyr.motion.js');
      const root = document.querySelector('.syn-root');
      const viz = enhanceViz(root);
      const motion = enhanceMotion(root);
      const same = viz === enhanceViz(root) && motion === enhanceMotion(root);
      // HTMX-like insertion: refresh explicit, without global observers.
      const fragment = document.createElement('div');
      fragment.innerHTML = '<p data-syn-motion-js="fade">Updated fragment</p>';
      root.append(fragment);
      motion.refresh();
      const animated = fragment.firstElementChild.getAnimations().length > 0;
      const selected = document.querySelectorAll('[data-syn-point]')[1];
      selected.focus();
      viz.refresh();
      const preservesFocus = selected.getAttribute('tabindex') === '0';
      const crosshair = document.querySelector('[data-syn-crosshair]');
      viz.destroy();
      const restoresCrosshair = crosshair.getAttribute('x1') === '0' && crosshair.hasAttribute('hidden');
      motion.destroy();
      return {same, animated, preservesFocus, restoresCrosshair, points: [...document.querySelectorAll('[data-syn-point]')].map(el=>el.getAttribute('tabindex')),
              tips: document.querySelectorAll('.syn-chart-tooltip').length,
              active: fragment.firstElementChild.getAnimations().length};
    }""")
    assert state["same"], state
    assert state["animated"], state
    assert state["preservesFocus"], state
    assert state["restoresCrosshair"], state
    assert state["points"] == [None] * 4, state
    assert state["tips"] == 0, state
    assert state["active"] == 0, state
    assert not errors, errors
    context.close()

    reduced = browser.new_context(reduced_motion="reduce")
    page = reduced.new_page()
    page.goto(url)
    page.wait_for_function("document.documentElement.dataset.synDemoReady === 'true'")
    assert page.locator("[data-syn-motion-js]").first.evaluate(
        "(el) => el.getAnimations().length") == 0
    assert page.locator("[data-syn-motion-js]").first.is_visible()
    reduced.close()
    print(f"PASS {name}: no JS fallback, keyboard/pointer chart, cleanup, HTMX refresh, reduced motion")


def main():
    with site() as url, sync_playwright() as p:
        failures = 0
        for name in ("chromium", "firefox"):
            try:
                kwargs = {"headless": True}
                if name == "chromium":
                    binary = os.getenv("PLAYWRIGHT_CHROMIUM_EXECUTABLE") or shutil.which("chromium")
                    if binary:
                        kwargs.update(executable_path=binary, args=["--no-sandbox"])
                browser = getattr(p, name).launch(**kwargs)
                try:
                    test_browser(browser, url, name)
                finally:
                    browser.close()
            except Exception as exc:
                import traceback
                traceback.print_exc()
                failures += 1
                print(f"FAIL {name}: {exc}")
        return failures != 0


if __name__ == "__main__":
    raise SystemExit(main())
