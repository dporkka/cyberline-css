"""Design workflows stay docs-only, useful, and truthful about commercial availability."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class DesignWorkflowTests(unittest.TestCase):
    def test_playground_has_responsive_and_state_controls(self):
        html = (ROOT / "docs/playground.html").read_text()
        js = (ROOT / "docs/playground.js").read_text()
        for identifier in ("playground-size", "playground-density", "playground-state",
                           "playground-viewport", "playground-copy-setup"):
            self.assertIn(f'id="{identifier}"', html)
            if identifier != "playground-viewport":
                self.assertIn(identifier, js)
        self.assertIn("playground-viewport", (ROOT / "docs/playground.css").read_text())
        for value in ("375", "768", "1280", "compact", "spacious", "disabled", "invalid"):
            self.assertIn(value, html)
        self.assertIn("sandbox=\"allow-same-origin\"", html)
        self.assertIn("form-action 'none'", js)
        self.assertNotIn("allow-scripts", html)

    def test_theme_editor_exports_actual_semantic_and_typographic_tokens(self):
        html = (ROOT / "docs/theme-editor.html").read_text()
        js = (ROOT / "docs/theme-editor.js").read_text()
        for identifier in ("background", "surface", "text-color", "muted", "frame",
                           "radius", "body-size", "density", "generated-tokens",
                           "copy-css", "copy-tokens", "copy-status"):
            self.assertIn(f'id="{identifier}"', html)
        for token in ("--syn-bg", "--syn-surface", "--syn-text", "--syn-muted",
                      "--syn-frame", "--syn-accent", "--syn-on-accent",
                      "--syn-radius", "--syn-type-body"):
            self.assertIn(token, js)
        self.assertIn("JSON.stringify", js)
        self.assertIn("contrastRatio", js)
        self.assertIn("getComputedStyle", js)
        self.assertNotIn("fetch(", js)

    def test_console_kit_research_provides_real_evaluation_steps(self):
        page = (ROOT / "docs/console-kit.html").read_text()
        self.assertIn('id="kit-evaluation"', page)
        self.assertIn("../examples/operations-console.html", page)
        self.assertIn("NOT AVAILABLE FOR PURCHASE", page)
        self.assertIn("console-kit-feedback.yml", page)
        self.assertNotIn("BUY NOW", page)


if __name__ == "__main__":
    unittest.main()
