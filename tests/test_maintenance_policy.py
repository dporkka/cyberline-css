"""Regression tests for source ownership and low-entropy CSS distribution."""
from pathlib import Path
import tempfile
import unittest

from scripts.maintenance_policy import find_issues


class MaintenancePolicyTests(unittest.TestCase):
    def test_current_source_and_distribution_registry_have_no_drift(self):
        self.assertEqual(find_issues(), [])

    def test_root_font_role_aliases_have_one_canonical_default(self):
        tokens = (Path(__file__).resolve().parents[1] / "src/tokens.css").read_text()
        self.assertEqual(tokens.count("--syn-font-ui: var(--syn-font);"), 1)
        self.assertEqual(tokens.count("--syn-font-display: var(--syn-font);"), 1)

    def test_duplicate_bundle_sources_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory)
            (src / "tokens.css").write_text("@layer syn.tokens {}")
            issues = find_issues(src, {"syntyr.core.css": ("tokens.css", "tokens.css")})
            self.assertTrue(any("duplicate source" in issue for issue in issues), issues)

    def test_unregistered_css_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory)
            (src / "tokens.css").write_text("@layer syn.tokens {}")
            (src / "abandoned.css").write_text(".unused { color: red; }")
            issues = find_issues(src, {"syntyr.core.css": ("tokens.css",)})
            self.assertTrue(any("unregistered source: abandoned.css" in issue for issue in issues), issues)

    def test_missing_registered_css_source_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            issues = find_issues(Path(directory), {"syntyr.core.css": ("missing.css",)})
            self.assertTrue(any("missing source: missing.css" in issue for issue in issues), issues)

    def test_component_theme_forks_are_rejected_but_token_themes_allowed(self):
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory)
            (src / "components").mkdir()
            (src / "tokens.css").write_text(':where(.syn-root[data-syn-theme="noir"]) { --syn-bg: black; }')
            (src / "components" / "card.css").write_text('/* [data-syn-theme="ignored"] */\n.syn-card[data-syn-theme="noir"] { color: red; }')
            bundles = {"syntyr.core.css": ("tokens.css", "components/card.css")}
            issues = find_issues(src, bundles)
            self.assertTrue(any("component theme fork" in issue for issue in issues), issues)
            (src / "components" / "card.css").write_text('/* [data-syn-theme="ignored"] */\n.syn-card { color: var(--syn-bg); }')
            self.assertEqual(find_issues(src, bundles), [])

    def test_optional_recipes_cannot_fork_presentation_by_theme(self):
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory)
            (src / "recipes.css").write_text('.syn-card[data-syn-theme="noir"] { border: 1px solid red; }')
            issues = find_issues(src, {"syntyr.recipes.css": ("recipes.css",)})
            self.assertTrue(any("theme fork" in issue for issue in issues), issues)

    def test_important_declarations_outside_accessibility_base_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            src = Path(directory)
            (src / "components").mkdir()
            (src / "base.css").write_text("@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }")
            (src / "components" / "card.css").write_text(".syn-card { color: red !important; }")
            bundles = {"syntyr.core.css": ("base.css", "components/card.css")}
            issues = find_issues(src, bundles)
            self.assertTrue(any("!important outside base.css" in issue for issue in issues), issues)
            (src / "components" / "card.css").write_text("/* !important is discouraged */ .syn-card { color: red; }")
            self.assertEqual(find_issues(src, bundles), [])


if __name__ == "__main__":
    unittest.main()
