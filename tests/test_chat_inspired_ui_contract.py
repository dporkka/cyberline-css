"""CSS-only neutral UI and conversation recipe behavior contracts."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class ChatInspiredUIContract(unittest.TestCase):
    def test_manual_contrast_is_nested_and_system_preference_always_wins(self):
        tokens = (ROOT / "src/tokens.css").read_text()
        self.assertIn('.syn-root[data-syn-contrast="more"]', tokens)
        self.assertIn('.syn-root [data-syn-contrast="normal"]', tokens)
        self.assertIn('--syn-border-subtle: var(--syn-frame-strong);', tokens)
        # Under an OS contrast preference, explicitly nested contrast modes must
        # remain high contrast, not silently defeat accessibility preferences.
        system = tokens.split('@media (prefers-contrast: more)', 1)[1]
        self.assertIn('.syn-root [data-syn-contrast]', system)
        self.assertIn('--syn-border-subtle: var(--syn-frame-strong);', system)

    def test_contrast_weight_inherits_across_palette_boundaries(self):
        tokens = (ROOT / "src/tokens.css").read_text()
        derived = tokens.split("/* Derived surfaces", 1)[1].split("/* Compact presentation", 1)[0]
        manual = tokens.split("/* Explicit contrast", 1)[1].split("/* Higher contrast", 1)[0]
        # An inherited numeric mode lets each nested palette recompute borders
        # from its own frame tokens without losing the nearest contrast opt-out.
        self.assertIn("var(--_syn-contrast-strong, 0%)", derived)
        self.assertIn("--_syn-contrast-strong: 100%;", manual)
        self.assertIn("--_syn-contrast-strong: 0%;", manual)

    def test_system_high_contrast_suppresses_overlay_shadow(self):
        system = (ROOT / "src/tokens.css").read_text().split(
            "@media (prefers-contrast: more)", 1)[1]
        self.assertIn("--syn-shadow-overlay: none;", system)

    def test_invalid_composer_never_loses_its_error_border(self):
        recipe = (ROOT / "src/recipes.css").read_text().split(
            "/* Conversational UI", 1)[1].split("/* End conversational UI */", 1)[0]
        self.assertIn('&.syn-composer .syn-textarea:where(:user-invalid, [aria-invalid="true"])', recipe)
        self.assertIn("border-color: var(--syn-danger);", recipe)

    def test_studio_and_minimal_have_quiet_rounded_panels_not_theme_forks(self):
        tokens = (ROOT / "src/tokens.css").read_text()
        for theme in ("studio", "minimal"):
            section = tokens.split(f'[data-syn-theme="{theme}"]', 1)[1].split("}", 1)[0]
            self.assertIn("--syn-panel-radius: var(--syn-radius);", section)
        self.assertIn('--syn-panel-radius, 0', (ROOT / "src/components/layout.css").read_text())
        for theme in ("grid", "noir", "industrial", "terminal", "corporate", "auto"):
            section = tokens.split(f'[data-syn-theme="{theme}"]', 1)[1].split("}", 1)[0]
            self.assertIn("--syn-panel-radius: 0;", section)


    def test_conversation_recipe_is_optional_and_theme_agnostic(self):
        source = (ROOT / "src/recipes.css").read_text()
        core = (ROOT / "dist/syntyr.core.css").read_text()
        for name in (".syn-conversation", ".syn-message--outgoing", ".syn-message--incoming",
                     ".syn-composer", ".syn-composer-actions"):
            with self.subTest(name=name):
                self.assertIn(name, source)
                self.assertNotIn(name, core)
        recipe = source.split("/* Conversational UI", 1)[1].split("/* End conversational UI */", 1)[0]
        self.assertIn("var(--syn-surface-raised)", recipe)
        self.assertIn("var(--syn-border-subtle)", recipe)
        self.assertNotIn("data-syn-theme=", recipe)
        self.assertNotIn("!important", recipe)

    def test_example_is_publicly_allowlisted_but_noindexed(self):
        from scripts.build_cloudflare_site import NOINDEX_HTML, source_files
        name = "examples/chat-interface.html"
        self.assertIn(name, NOINDEX_HTML)
        self.assertIn(name, source_files())

    def test_example_has_accessible_static_composer_and_no_fake_chat(self):
        path = ROOT / "examples/chat-interface.html"
        self.assertTrue(path.is_file())
        html = path.read_text()
        parser = Markup()
        parser.feed(html)
        self.assertIn('syntyr.recipes.css', html)
        self.assertIn('data-syn-theme="minimal"', html)
        self.assertIn('data-syn-contrast="more"', html)
        self.assertIn('data-syn-intensity="quiet"', html)
        self.assertNotIn("<script", html.lower())
        self.assertNotIn("http://", html.lower())
        self.assertNotIn("https://", html.lower())
        labels = [a.get("for") for t, a in parser.tags if t == "label"]
        ids = [a.get("id") for _, a in parser.tags]
        self.assertIn("message-prompt", labels)
        self.assertIn("message-prompt", ids)
        self.assertTrue(any(t == "button" and "disabled" in a for t, a in parser.tags))
        self.assertIn("static", html.lower())


if __name__ == "__main__":
    unittest.main()
