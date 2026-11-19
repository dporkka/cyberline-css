"""Regression contracts for readable dense tables and composable panels."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class ComponentReadability(unittest.TestCase):
    def test_table_prose_wraps_by_default_but_identifiers_can_opt_out(self):
        css = (ROOT / 'src/components/data.css').read_text()
        cells = re.search(r'&\.syn-table th, &\.syn-table td\s*\{([^}]+)\}', css)
        self.assertIsNotNone(cells)
        self.assertIn('overflow-wrap: anywhere', cells.group(1))
        self.assertNotIn('white-space: nowrap', cells.group(1))
        self.assertRegex(css, r'&\.syn-table \.syn-cell--nowrap\s*\{[^}]*white-space:\s*nowrap')
        self.assertRegex(css, r'&\.syn-table \.syn-cell--numeric\s*\{[^}]*white-space:\s*nowrap')

    def test_theme_palette_text_and_primary_hover_remain_readable(self):
        css = (ROOT / 'src/tokens.css').read_text()
        def luminance(rgb):
            channels = [v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4
                        for v in rgb]
            return sum(c * w for c, w in zip(channels, (.2126, .7152, .0722)))
        def ratio(fg, bg):
            x, y = sorted((luminance(fg), luminance(bg)), reverse=True)
            return (x + .05) / (y + .05)
        def rgb(hex_color):
            return tuple(int(hex_color[i:i+2], 16) / 255 for i in (1, 3, 5))
        for name in ('studio', 'corporate', 'minimal', 'grid', 'noir', 'industrial', 'terminal'):
            with self.subTest(theme=name):
                block = re.search(r'\[data-syn-theme="' + name + r'"\][^{]*\{([^}]+)\}', css)
                self.assertIsNotNone(block)
                palette = dict(re.findall(r'(--syn-[\w-]+):\s*(#[\da-fA-F]{6})', block.group(1)))
                for fg, bg in (('--syn-text', '--syn-bg'),
                               ('--syn-muted', '--syn-surface'),
                               ('--syn-on-accent', '--syn-accent')):
                    self.assertGreaterEqual(ratio(rgb(palette[fg]), rgb(palette[bg])), 4.5,
                                            (name, fg, bg))
                accent = rgb(palette['--syn-accent'])
                hover = tuple(.9 * value + .1 for value in accent)
                self.assertGreaterEqual(ratio(rgb(palette['--syn-on-accent']), hover), 4.5,
                                        (name, 'primary hover contrast'))

    def test_panel_cut_can_match_an_underlying_surface(self):
        css = (ROOT / 'src/components/layout.css').read_text()
        corner = re.search(r'&\.syn-panel--cut::after\s*\{([^}]+)\}', css)
        self.assertIsNotNone(corner)
        self.assertIn('var(--syn-panel-cut-fill, var(--syn-bg))', corner.group(1))

    def test_layout_change_has_public_migration_guidance(self):
        stability = (ROOT / "docs/api-stability.md").read_text()
        self.assertIn(".syn-cell--nowrap", stability)
        self.assertIn("prerelease", stability.lower())
        index = (ROOT / "llms.txt").read_text()
        self.assertIn("docs/components.md", index)
        self.assertIn("table", index.lower())

    def test_component_docs_explain_table_and_corner_customization(self):
        docs = (ROOT / 'docs/components.md').read_text()
        self.assertIn('.syn-cell--nowrap', docs)
        self.assertIn('--syn-panel-cut-fill', docs)


if __name__ == '__main__':
    unittest.main()
