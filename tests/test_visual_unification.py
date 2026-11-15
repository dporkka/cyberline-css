"""Regression contracts for a consistent, CSS-only Syntyr marketing experience."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGES = ('index.html', 'docs/index.html', 'docs/catalog.html', 'docs/blocks.html')


class NavLabels(HTMLParser):
    def __init__(self):
        super().__init__()
        self.inside_nav = False
        self.inside_link = False
        self.labels = []
        self.current = ''

    def handle_starttag(self, tag, attrs):
        fields = dict(attrs)
        if tag == 'nav' and fields.get('aria-label') == 'Main navigation':
            self.inside_nav = True
        elif tag == 'a' and self.inside_nav:
            self.inside_link = True
            self.current = ''

    def handle_data(self, text):
        if self.inside_link:
            self.current += text

    def handle_endtag(self, tag):
        if tag == 'a' and self.inside_link:
            self.labels.append(self.current.strip())
            self.inside_link = False
        if tag == 'nav' and self.inside_nav:
            self.inside_nav = False


def contrast(fg, bg):
    def luminance(hexcolor):
        rgb = [int(hexcolor[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [x / 12.92 if x <= 0.04045 else ((x + .055) / 1.055) ** 2.4 for x in rgb]
        return .2126 * linear[0] + .7152 * linear[1] + .0722 * linear[2]
    a, b = sorted([luminance(fg), luminance(bg)], reverse=True)
    return (a + .05) / (b + .05)


class VisualUnificationTests(unittest.TestCase):
    def test_messaging_and_navigation_are_consistent_across_entrypoints(self):
        for page in PAGES:
            with self.subTest(page=page):
                content = (ROOT / page).read_text()
                nav = NavLabels()
                nav.feed(content)
                self.assertEqual(nav.labels, ['Get started', 'Components', 'Blocks', 'Themes', 'Docs', 'Semantic starter', 'Examples', 'GitHub'])
                self.assertIn('SYNTYR', content)
        self.assertIn('data-syn-theme="studio"', (ROOT / 'docs/index.html').read_text().split('<body', 1)[1].split('>', 1)[0])

    def test_theme_picker_changes_visible_preview_without_scripts(self):
        html = (ROOT / 'index.html').read_text()
        self.assertIn('<fieldset class="site-theme-picker"', html)
        self.assertEqual(html.count('name="site-preview-theme"'), 3)
        for theme in ('studio', 'grid', 'noir'):
            self.assertIn(f'value="{theme}"', html)
            self.assertIn(f'data-site-preview="{theme}"', html)
            self.assertIn(f'href="examples/flagship-{theme}.html"', html)
        self.assertIn('value="grid" checked', html)
        self.assertNotIn('<script', html.lower())
        self.assertIn(':has(.site-theme-picker', html)
        self.assertIn('input:focus-visible + span', html)

    def test_preview_is_realistic_and_not_decorative_bars_only(self):
        html = (ROOT / 'index.html').read_text()
        for label in ('Active accounts', 'Revenue', 'Needs review', 'Recent activity', 'Workspace'):
            self.assertIn(label, html)
        self.assertIn('ILLUSTRATIVE SAMPLE', html)

    def test_control_boundaries_are_visible_in_all_themes(self):
        tokens = (ROOT / 'src/tokens.css').read_text()
        forms = (ROOT / 'src/components/forms.css').read_text()
        self.assertIn('--syn-control-border: var(--syn-frame-strong)', tokens)
        self.assertIn('1px solid var(--syn-control-border)', forms)
        for theme in ('studio', 'grid', 'noir', 'industrial', 'terminal', 'corporate', 'minimal'):
            with self.subTest(theme=theme):
                match = re.search(r'\[data-syn-theme="' + theme + r'"\][^{]*\{([^}]+)\}', tokens)
                self.assertIsNotNone(match)
                colors = dict(re.findall(r'(--syn-[\w-]+):\s*(#[\da-fA-F]{6})\s*;', match.group(1)))
                self.assertGreaterEqual(contrast(colors['--syn-frame-strong'], colors['--syn-bg']), 3.0)

    def test_technical_theme_keeps_body_text_readable(self):
        tokens = (ROOT / 'src/tokens.css').read_text()
        self.assertIn('Grid display typography is technical', tokens)
        self.assertIn('--syn-font-display: var(--syn-mono)', tokens)
        self.assertIn('--syn-font-ui: var(--syn-mono)', tokens)  # Terminal only

    def test_popovers_have_quiet_edges_unless_explicitly_accented(self):
        overlays = (ROOT / 'src/components/overlays.css').read_text()
        self.assertIn('border: 1px solid var(--syn-border-floating)', overlays)
        self.assertNotIn('border: 1px solid var(--syn-accent)', overlays)


if __name__ == '__main__':
    unittest.main()
