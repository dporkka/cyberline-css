"""The opt-in Base UI adapter never changes Syntyr's CSS-only runtime."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
ADAPTER = ROOT / "integrations/base-ui/states.css"


class BaseUIIntegration(unittest.TestCase):
    def test_adapter_covers_documented_component_parts_and_states(self):
        css = ADAPTER.read_text(encoding="utf-8")
        for part in ("trigger", "popup", "item", "separator", "backdrop",
                     "dialog-viewport", "dialog-title", "dialog-description",
                     "switch", "switch-thumb", "checkbox", "checkbox-indicator",
                     "tabs-list", "tab", "tabs-panel", "field", "field-error"):
            with self.subTest(part=part):
                self.assertIn(".syn-base-" + part, css)
        for state in ("[data-open]", "[data-popup-open]", "[data-checked]",
                      "[data-disabled]", "[data-invalid]", "[data-highlighted]",
                      "[data-selected]", "[data-focus-visible]",
                      "[data-starting-style]", "[data-ending-style]"):
            with self.subTest(state=state):
                self.assertIn(state, css)
        self.assertIn("@layer syn.components {", css)
        self.assertIn(":where(.syn-root, .syn-root *)", css)
        self.assertIn("padding-inline", css)
        self.assertIn("border-inline-start", css)
        self.assertIn("@media (forced-colors: active)", css)
        self.assertIn("@media (prefers-reduced-motion: reduce)", css)

    def test_adapter_is_scoped_noninvasive_and_css_only(self):
        css = ADAPTER.read_text(encoding="utf-8")
        for forbidden in ("@import", "@apply", "!important", "url(", "outline: none",
                          "display: none", "pointer-events: none", ":root {", ".dark {"):
            with self.subTest(forbidden=forbidden):
                self.assertNotIn(forbidden, css)
        self.assertFalse(re.search(r"(?m)^\s*\[data-(?:open|checked|disabled)", css))
        from scripts.build import all_distributions
        for name, sources in all_distributions().items():
            with self.subTest(name=name):
                self.assertNotIn("integrations/base-ui/states.css", sources)
        self.assertNotIn(".syn-base-popup", (ROOT / "dist/syntyr.core.css").read_text())

    def test_exported_in_release_zip_without_consumer_dependencies(self):
        pkg = json.loads((ROOT / "package.json").read_text())
        self.assertEqual(pkg["exports"]["./base-ui.css"], "./integrations/base-ui/states.css")
        self.assertIn("integrations/base-ui/", pkg["files"])
        self.assertNotIn("@base-ui/react", pkg.get("dependencies", {}))
        from scripts.package_release import FILES
        self.assertIn("integrations/base-ui/states.css", FILES)
        self.assertIn("docs/base-ui-integration.md", FILES)

    def test_real_react_fixture_and_keyboard_regression_are_opt_in(self):
        demo = ROOT / "examples/base-ui-react"
        pkg = json.loads((demo / "package.json").read_text())
        self.assertTrue(pkg["private"])
        self.assertIn("@base-ui/react", pkg["dependencies"])
        self.assertIn("react", pkg["dependencies"])
        self.assertIn("@playwright/test", pkg["devDependencies"])
        self.assertTrue((demo / "package-lock.json").exists())
        jsx = (demo / "src/App.tsx").read_text()
        for tag in ("Menu.Root", "Menu.Positioner", "Menu.Item",
                    "Dialog.Root", "Dialog.Portal", "Switch.Root",
                    "Tabs.Root", "data-syn-theme"):
            self.assertIn(tag, jsx)
        self.assertIn("container={portalRef}", jsx)
        self.assertTrue((demo / "tests/adapter.spec.ts").is_file())

    def test_documented_portal_scoping_and_owning_behavior(self):
        doc = (ROOT / "docs/base-ui-integration.md").read_text()
        for requirement in ("@base-ui/react", "Portal", "container", "syn-root",
                            "focus", "keyboard", "RTL", "native HTML",
                            "syntyr.core.css", "base-ui.css", "no runtime"):
            with self.subTest(requirement=requirement):
                self.assertIn(requirement.lower(), doc.lower())
        self.assertIn("docs/base-ui-integration.md", (ROOT / "README.md").read_text())
        from scripts.build_cloudflare_site import source_files
        self.assertIn("integrations/base-ui/states.css", source_files())
        self.assertIn("docs/base-ui-integration.html", source_files())


if __name__ == "__main__":
    unittest.main()
