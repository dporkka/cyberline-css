"""Progressive enhancements remain scoped, optional and framework-independent."""
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from build import distributions


class ProgressiveDesignContract(unittest.TestCase):
    def test_native_auto_theme_is_in_core_and_only_print_is_an_addon(self):
        built = distributions()
        self.assertNotIn("syntyr.auto.css", built)
        self.assertEqual(built["syntyr.print.css"], ("print.css",))
        self.assertIn("print.css", built["syntyr.all.css"])
        self.assertNotIn("print.css", built["syntyr.core.css"])
        tokens = (ROOT / "src/tokens.css").read_text()
        self.assertIn('data-syn-theme="auto"', tokens)
        self.assertIn("light-dark(", tokens)
        self.assertIn("@supports (color: light-dark(", tokens)
        printed = (ROOT / "src/print.css").read_text()
        self.assertIn("@media print", printed)
        self.assertIn("@layer syn.print", printed)
        self.assertIn(".syn-table-wrap", printed)

    def test_semantic_styles_are_bounded_to_syn_root(self):
        css = (ROOT / "src/semantic.css").read_text()
        self.assertNotIn("  .syn-semantic :where(", css)
        self.assertIn(":is(.syn-root.syn-semantic, .syn-root .syn-semantic) :where(", css)

    def test_intrinsic_two_column_layout_works_in_narrow_embeds(self):
        css = (ROOT / "src/components/layout.css").read_text()
        layout = re.search(r"\.syn-layout\s*\{([^}]+)\}", css)
        self.assertIsNotNone(layout)
        self.assertIn("repeat(auto-fit", layout.group(1))
        self.assertNotIn("@media (max-width: 45rem)", css)

    def test_readable_design_uses_scalable_type_tokens(self):
        tokens = (ROOT / "src/tokens.css").read_text()
        typography = (ROOT / "src/components/typography.css").read_text()
        forms = (ROOT / "src/components/forms.css").read_text()
        self.assertIn("--syn-type-xs: .75rem", tokens)
        self.assertIn("--syn-type-sm: .875rem", tokens)
        self.assertIn("var(--syn-type-xs)", typography)
        self.assertIn("var(--syn-type-sm)", forms)

    def test_html_first_guidance_includes_fallback(self):
        content = (ROOT / "docs/progressive-enhancement.md").read_text()
        for snippet in ('<form', 'method="get"', 'syntyr.print.css',
                        'command="show-modal"', 'data-syn-theme="auto"'):
            self.assertIn(snippet, content)
        self.assertNotIn("syntyr.auto.css", content)


if __name__ == "__main__":
    unittest.main()
