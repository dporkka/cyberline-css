"""Icon contract and explorer regression tests."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.build_blocks import validate_icons


class IconImprovements(unittest.TestCase):
    def test_icon_css_does_not_override_vendor_color(self):
        css = (ROOT / "src/symbols.css").read_text()
        first_rule = css.split(":where(.syn-root .syn-icon, .syn-root.syn-icon)", 1)[1].split("}", 1)[0]
        self.assertNotIn("color: inherit", first_rule)

    def test_icon_button_has_independent_square_touch_geometry(self):
        css = (ROOT / "src/components/buttons.css").read_text()
        self.assertIn("&.syn-button--icon", css)
        self.assertIn("--syn-icon-button-size", css)
        self.assertIn("min-inline-size", css)
        self.assertIn("min-block-size", css)

    def test_manifest_rejects_untrusted_svg_shapes(self):
        safe = [{"id": "safe", "label": "Safe", "body": '<path d="M1 2l3 4"/>'}]
        validate_icons(safe)
        for malicious in (
            '<script>alert(1)</script>',
            '<path d="M1 2" onclick="alert(1)"/>',
            '<foreignObject><p>bad</p></foreignObject>',
            '<path d="M1 2" fill="url(https://evil.example/)"/>',
            '<use href="https://evil.example/icon.svg#x"/>',
        ):
            with self.subTest(malicious=malicious), self.assertRaises(ValueError):
                validate_icons([{"id": "bad", "label": "Bad", "body": malicious}])
        with self.assertRaises(ValueError):
            validate_icons(safe + safe)

    def test_icon_explorer_supports_search_and_copy_without_required_js(self):
        icons = json.loads((ROOT / "blocks/icons.json").read_text())["icons"]
        self.assertGreaterEqual(len(icons), 36)
        page = (ROOT / "docs/blocks.html").read_text()
        script = (ROOT / "docs/blocks.js").read_text()
        self.assertIn('id="icons-search"', page)
        self.assertIn('id="icons-results"', page)
        self.assertEqual(page.count("data-icon-copy"), len(icons))
        self.assertIn("filterIcons", script)
        self.assertIn("navigator.clipboard", script)
        self.assertIn("SVG source for ", page)
        self.assertIn("data-icon-source", page)


if __name__ == "__main__":
    unittest.main()
