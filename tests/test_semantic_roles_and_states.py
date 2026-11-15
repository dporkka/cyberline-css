"""Public design-system roles and interaction states stay theme-neutral and HTML-first."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def source(path):
    return (ROOT / path).read_text(encoding="utf-8")


class SemanticRolesAndStates(unittest.TestCase):
    def test_nested_themes_inherit_semantic_surface_and_interaction_roles(self):
        css = source("src/tokens.css")
        self.assertIn(".syn-root [data-syn-theme]", css)
        for token in ("--syn-text-subtle:", "--syn-border-default:", "--syn-border-hover:",
                      "--syn-focus-ring:", "--syn-surface-interactive:", "--syn-surface-hover:",
                      "--syn-surface-pressed:"):
            with self.subTest(token=token):
                self.assertIn(token, css)

    def test_typography_has_coherent_reusable_roles(self):
        tokens = source("src/tokens.css")
        typography = source("src/components/typography.css")
        for role in ("--syn-type-display:", "--syn-type-heading:", "--syn-type-body:",
                     "--syn-leading-body:", "--syn-tracking-display:"):
            self.assertIn(role, tokens)
        for selector in (".syn-display", ".syn-body", ".syn-text-support", ".syn-prose"):
            self.assertIn(selector, typography)
        self.assertIn("var(--syn-type-display)", typography)
        self.assertIn("var(--syn-tracking-display)", typography)

    def test_interaction_styling_uses_semantic_roles(self):
        base = source("src/base.css")
        buttons = source("src/components/buttons.css")
        forms = source("src/components/forms.css")
        self.assertIn("var(--syn-focus-ring)", base)
        self.assertIn(":active", buttons)
        self.assertIn("var(--syn-surface-interactive)", buttons)
        self.assertIn("var(--syn-surface-pressed)", buttons)
        self.assertIn("var(--syn-border-hover)", forms)
        self.assertIn("var(--syn-border-focus)", forms)
        self.assertIn("[aria-busy=\"true\"]", buttons)
        self.assertIn("forced-colors: active", buttons)

    def test_button_density_uses_shared_control_padding_token(self):
        buttons = source("src/components/buttons.css")
        self.assertIn(
            "padding: var(--syn-control-padding-block) var(--syn-control-padding-inline);",
            buttons,
        )

    def test_classless_semantic_mode_shares_interactive_roles_and_disabled_rules(self):
        semantic = source("src/semantic.css")
        self.assertIn("var(--syn-surface-interactive)", semantic)
        self.assertIn("var(--syn-surface-hover)", semantic)
        self.assertIn("var(--syn-border-hover)", semantic)
        self.assertIn("var(--syn-border-focus)", semantic)
        self.assertIn(':where(:not(:disabled):not([aria-disabled="true"]):hover)', semantic)
        self.assertIn(':where(:not(:disabled):not([aria-disabled="true"]):active)', semantic)
        self.assertIn('[aria-busy="true"]', semantic)

    def test_invalid_forms_and_selected_toggles_survive_hover_and_focus(self):
        buttons = source("src/components/buttons.css")
        forms = source("src/components/forms.css")
        semantic = source("src/semantic.css")
        # Keep interactive pseudo-class specificity below explicit state styling.
        self.assertIn(':where(:not(:disabled):not([aria-disabled="true"]):hover)', buttons)
        self.assertIn(":where(:not(:disabled):hover)", forms)
        for selector in (".syn-input:where(:focus)", ".syn-select:where(:focus)",
                         ".syn-textarea:where(:focus)"):
            self.assertIn(selector, forms)
        self.assertNotIn(".syn-input:focus", forms)
        self.assertNotIn(".syn-select:focus", forms)
        self.assertIn(":where(:not(:disabled):hover)", semantic)
        self.assertIn(":where(:focus)", semantic)
        self.assertLess(buttons.index(":hover"), buttons.index('[aria-pressed="true"]'))

    def test_accessible_design_state_demonstration_is_published_without_runtime_js(self):
        demo = source("examples/design-states.html")
        self.assertIn('class="syn-root', demo)
        self.assertIn('aria-invalid="true"', demo)
        self.assertIn('aria-describedby=', demo)
        self.assertIn('data-syn-theme="studio"', demo)
        self.assertIn('data-syn-theme="grid"', demo)
        self.assertIn('data-syn-density="compact"', demo)
        self.assertNotIn("<script", demo.lower())
        build = source("scripts/build_cloudflare_site.py")
        self.assertIn('"design-states.html"', build)


if __name__ == "__main__":
    unittest.main()
