"""Presentation controls remain CSS-only, nested, and independently composable."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PresentationPreview(HTMLParser):
    def __init__(self):
        super().__init__()
        self.densities = set()
        self.themes = set()
        self.scripts = 0

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if 'data-syn-density' in values:
            self.densities.add(values['data-syn-density'])
        if 'data-syn-theme' in values:
            self.themes.add(values['data-syn-theme'])
        if tag == 'script':
            self.scripts += 1


class PresentationSystemContract(unittest.TestCase):
    def test_three_opt_in_density_modes_with_overridable_role_tokens(self):
        tokens = (ROOT / 'src/tokens.css').read_text()
        for mode in ('compact', 'comfortable', 'spacious'):
            with self.subTest(mode=mode):
                self.assertIn(f'.syn-root[data-syn-density="{mode}"]', tokens)
                self.assertIn(f'.syn-root [data-syn-density="{mode}"]', tokens)
        for name in ('control-height', 'control-padding-block', 'control-padding-inline',
                     'row-padding-block', 'table-padding-inline', 'card-padding',
                     'panel-padding', 'price-padding'):
            self.assertIn('--syn-' + name + ':', tokens)
        for mode in ('compact', 'spacious'):
            rule = re.search(r'\[data-syn-density="' + mode + r'"\]\)\s*\{([^}]+)\}', tokens)
            self.assertIsNotNone(rule, mode)
            for name in ('control-height', 'row-padding-block', 'card-padding',
                         'panel-padding', 'price-padding'):
                self.assertIn('--syn-' + name + ':', rule.group(1))

    def test_density_affects_real_components_not_only_unused_tokens(self):
        css = {
            name: (ROOT / 'src/components' / name).read_text()
            for name in ('buttons.css', 'forms.css', 'layout.css', 'data.css', 'patterns.css')
        }
        self.assertIn('var(--syn-control-padding-inline)', css['buttons.css'])
        self.assertIn('var(--syn-control-padding-inline)', css['forms.css'])
        self.assertIn('var(--syn-panel-padding)', css['layout.css'])
        self.assertIn('var(--syn-table-padding-inline)', css['data.css'])
        self.assertIn('var(--syn-card-padding)', css['patterns.css'])
        self.assertIn('var(--syn-price-padding)', css['patterns.css'])
        semantic = (ROOT / 'src/semantic.css').read_text()
        self.assertEqual(
            semantic.count('padding: var(--syn-control-padding-block) var(--syn-control-padding-inline);'),
            2, 'classless buttons and inputs must share density tokens',
        )
        self.assertIn('padding: var(--syn-panel-padding);', semantic)
        self.assertIn('var(--syn-row-padding-block) var(--syn-table-padding-inline)', semantic)

    def test_surface_and_button_variants_reuse_theme_aware_tokens(self):
        layout = (ROOT / 'src/components/layout.css').read_text()
        buttons = (ROOT / 'src/components/buttons.css').read_text()
        tokens = (ROOT / 'src/tokens.css').read_text()
        for selector in ('.syn-panel--raised', '.syn-panel--recessed'):
            self.assertIn(selector, layout)
        self.assertIn('--syn-shadow-md:', tokens)
        self.assertIn('var(--syn-shadow-md)', layout)
        self.assertIn('var(--syn-surface-raised)', layout)
        self.assertIn('var(--syn-surface-recessed)', layout)
        self.assertIn('.syn-button--soft', buttons)
        self.assertIn('var(--syn-accent-soft)', buttons)
        self.assertIn('@media (forced-colors: active)', layout)

    def test_no_javascript_design_gallery_documents_presentation(self):
        page = (ROOT / 'examples/design-system.html')
        self.assertTrue(page.is_file())
        source = page.read_text()
        parser = PresentationPreview()
        parser.feed(source)
        self.assertTrue({'studio', 'grid', 'noir'} <= parser.themes)
        self.assertEqual(parser.densities, {'compact', 'comfortable', 'spacious'})
        self.assertEqual(parser.scripts, 0)
        for cls in ('syn-panel--raised', 'syn-panel--recessed', 'syn-button--soft',
                    'syn-table', 'syn-input', 'syn-button--primary'):
            self.assertIn(cls, source)
        self.assertIn('design-system.html', (ROOT / 'examples/themes.html').read_text())
        guide = (ROOT / 'docs/theme-customization.md').read_text()
        self.assertIn('data-syn-density="spacious"', guide)
        self.assertIn('syn-panel--raised', guide)


if __name__ == '__main__':
    unittest.main()
