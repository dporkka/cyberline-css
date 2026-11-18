"""Opt-in real Chromium regression checks for Syntyr's desktop adapter.

Run: SYNTYR_CHROME=/path/to/chrome python3 tests/desktop_browser.py
No browser or Python package is added to the CSS consumer dependency graph.
"""
from html import unescape
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import os
import re
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHROME = os.environ.get("SYNTYR_CHROME") or next(
    (path for binary in ("chromium", "chromium-browser", "google-chrome")
     if (path := shutil.which(binary))), None
)


def render_fixture(chrome, width):
    """Use actual distributed core CSS and optional adapter in the browser."""
    core = (ROOT / "dist/syntyr.core.css").read_text()
    desktop = (ROOT / "integrations/desktop/syntyr.desktop.css").read_text()
    script = """
    const root = document.querySelector("#app");
    const shell = document.querySelector("#nested-shell");
    const content = document.querySelector("#nested-content");
    const bar = document.querySelector("#nested-toolbar");
    const selected = document.querySelector("#selected");
    const reference = document.querySelector("#reference-noir");
    const expected = getComputedStyle(reference);
    const entries = [];
    for (const platform of ["macos", "windows", "gnome"]) {
      root.dataset.synPlatform = platform;
      const shellStyle = getComputedStyle(shell);
      const contentStyle = getComputedStyle(content);
      const barStyle = getComputedStyle(bar);
      const selectedStyle = getComputedStyle(selected);
      entries.push({
        platform, shellBg: shellStyle.backgroundColor,
        contentBg: contentStyle.backgroundColor,
        text: shellStyle.color, toolbarBg: barStyle.backgroundColor,
        selectedBorder: selectedStyle.borderInlineStartWidth,
        referenceBg: expected.backgroundColor,
        referenceText: expected.color,
        overflow: document.documentElement.scrollWidth - document.documentElement.clientWidth,
        columns: shellStyle.gridTemplateColumns
      });
    }
    document.querySelector("#test-results").textContent = JSON.stringify(entries);
    """
    markup = f"""<!doctype html><html><head><meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>{core}\n{desktop}</style></head>
    <body>
      <section class="syn-root" data-syn-theme="noir"><div id="reference-noir" class="syn-panel">Noir reference</div></section>
      <section id="app" class="syn-root" data-syn-platform="macos" data-syn-theme="studio">
        <div id="nested-shell" class="syn-desktop-shell" data-syn-theme="noir">
          <header id="nested-toolbar" class="syn-desktop-toolbar">Toolbar</header>
          <aside class="syn-desktop-sidebar"><nav class="syn-desktop-nav"><a id="selected" aria-current="page" href="#nested-content">Records</a></nav></aside>
          <main id="nested-content" class="syn-desktop-content">Nested theme content</main>
          <aside class="syn-desktop-inspector">Inspector</aside>
          <footer class="syn-desktop-statusbar">Status</footer>
        </div>
      </section><output id="test-results">not-run</output>
      <script>{script}</script>
    </body></html>"""
    with TemporaryDirectory(dir=Path.home(), prefix="syntyr-desktop-browser-") as tmp:
        directory = Path(tmp)
        file = directory / "fixture.html"
        file.write_text(markup)
        command = [
            chrome, "--headless=new", "--no-sandbox", "--no-first-run",
            "--disable-gpu", "--disable-extensions", "--disable-dev-shm-usage",
            f"--user-data-dir={directory / 'profile'}",
            f"--window-size={width},800", "--virtual-time-budget=2000",
            "--dump-dom", file.as_uri()
        ]
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode != 0:
            raise AssertionError(f"Chromium failed ({result.returncode}): {result.stderr[-1200:]}")
        found = re.search(r'<output id="test-results">([^<]+)</output>', result.stdout)
        if not found:
            raise AssertionError(f"Missing browser result: {result.stdout[-900:]}")
        return json.loads(unescape(found.group(1)))


@unittest.skipUnless(CHROME and Path(CHROME).is_file(), "Set SYNTYR_CHROME to a Chromium executable")
class DesktopBrowserTests(unittest.TestCase):
    def test_nested_noir_theme_recomputes_platform_colors_and_reflows(self):
        for width in (480, 1280):
            samples = render_fixture(CHROME, width)
            self.assertEqual([e["platform"] for e in samples], ["macos", "windows", "gnome"])
            for sample in samples:
                with self.subTest(width=width, platform=sample["platform"]):
                    self.assertEqual(sample["shellBg"], sample["referenceBg"])
                    self.assertEqual(sample["contentBg"], sample["referenceBg"])
                    self.assertEqual(sample["text"], sample["referenceText"])
                    self.assertNotEqual(sample["toolbarBg"], "rgb(255, 255, 255)")
                    self.assertLessEqual(sample["overflow"], 1)
                    if sample["platform"] == "windows":
                        self.assertEqual(sample["selectedBorder"], "3px")
                    else:
                        self.assertEqual(sample["selectedBorder"], "0px")
                    if width == 480:
                        self.assertEqual(len(sample["columns"].split()), 1)
                    else:
                        self.assertEqual(len(sample["columns"].split()), 3)


if __name__ == "__main__":
    unittest.main()
