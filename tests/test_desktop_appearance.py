"""Optional desktop appearance adapter contract (no core/runtime coupling)."""
from pathlib import Path
import json
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from package_release import FILES
from build_cloudflare_site import source_files

CSS_PATH = "integrations/desktop/syntyr.desktop.css"
EXAMPLE = "examples/desktop-workspace.html"
DEMO_JS = "examples/desktop-workspace.mjs"


class DesktopAppearanceContract(unittest.TestCase):
    def test_optional_public_adapter_is_packaged_and_exported(self):
        package = json.loads((ROOT / "package.json").read_text())
        self.assertEqual(package["exports"]["./desktop.css"], "./" + CSS_PATH)
        self.assertIn("integrations/desktop/", package["files"])
        for name in (CSS_PATH, EXAMPLE, DEMO_JS, "docs/desktop-apps.md"):
            self.assertTrue((ROOT / name).is_file(), name)
            self.assertIn(name, FILES, f"release ZIP missing {name}")
            self.assertIn(name, source_files(), f"site missing {name}")

    def test_platform_styles_are_scoped_and_independent_of_theme(self):
        css = (ROOT / CSS_PATH).read_text()
        for platform in ("macos", "windows", "gnome"):
            self.assertIn(f'[data-syn-platform="{platform}"]', css)
        self.assertIn(".syn-root", css)
        self.assertIn(".syn-desktop-shell", css)
        self.assertIn(".syn-desktop-toolbar", css)
        self.assertIn(".syn-desktop-sidebar", css)
        self.assertIn(".syn-desktop-inspector", css)
        self.assertIn(".syn-desktop-statusbar", css)
        self.assertNotIn("@import", css)
        self.assertNotRegex(css, r"url\s*\(\s*['\"]?https?://")
        self.assertNotIn("!important", css)
        self.assertNotIn("data-syn-theme", css)
        self.assertNotIn("body {", css)
        self.assertNotIn("html {", css)
        self.assertNotIn("--syn-control-height:", css)  # Density remains independent.
        self.assertIn("border-inline-start: 3px solid", css)  # Selected nav respects RTL.
        self.assertNotIn("inset 3px 0", css)

    def test_demo_is_semantic_and_has_static_no_js_fallback(self):
        html = (ROOT / EXAMPLE).read_text()
        self.assertIn('data-syn-platform="macos"', html)
        self.assertIn(CSS_PATH.replace("integrations/", "../integrations/"), html)
        self.assertIn('aria-current="page"', html)
        self.assertIn("<main", html)
        self.assertIn("<nav", html)
        self.assertIn("<aside", html)
        self.assertIn("<header", html)
        self.assertIn("<footer", html)
        for platform in ("macos", "windows", "gnome"):
            self.assertIn(f'value="{platform}"', html)
        self.assertIn("desktop-workspace.mjs", html)
        self.assertIn("desktop-workspace.html", (ROOT / "docs/index.html").read_text())

    def test_adapter_respects_accessibility_modes(self):
        css = (ROOT / CSS_PATH).read_text()
        self.assertIn(":focus-visible", css)
        self.assertIn("forced-colors: active", css)
        self.assertIn("prefers-reduced-motion: reduce", css)
        self.assertIn("max-width:", css)
        self.assertIn("overflow-wrap:", css)


if __name__ == "__main__":
    unittest.main()
