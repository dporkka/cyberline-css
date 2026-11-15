"""Dependency-free contract checks for the Syntyr starter."""
from pathlib import Path
from html.parser import HTMLParser
import unittest

ROOT = Path(__file__).resolve().parents[1]

class DemoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.scripts = []
        self.popovers = set()
        self.targets = []
        self.commands = []
        self.resources = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append(tag)
        if tag == 'script': self.scripts.append(attrs)
        if 'popover' in attrs: self.popovers.add(attrs.get('id'))
        if 'popovertarget' in attrs: self.targets.append(attrs['popovertarget'])
        if 'commandfor' in attrs: self.commands.append((attrs['commandfor'], attrs.get('command')))
        if tag in ('link', 'img'):
            self.resources.append(attrs.get('href', attrs.get('src', '')))

def luminance(color):
    vals = [int(color[i:i+2], 16)/255 for i in (1, 3, 5)]
    return sum(channel * weight for channel, weight in zip(
        [(v / 12.92 if v <= .04045 else ((v+.055)/1.055)**2.4) for v in vals],
        (.2126, .7152, .0722)))

def contrast(a,b):
    x,y = sorted([luminance(a), luminance(b)], reverse=True)
    return (x+.05)/(y+.05)

class ContractTests(unittest.TestCase):
    def test_built_css_exists_and_keeps_declared_layers(self):
        css = (ROOT/'dist/syntyr.css').read_bytes()
        self.assertGreater(len(css), 0)
        self.assertIn(b'@layer syn.tokens, syn.base, syn.components, syn.semantic, syn.recipes, syn.geometry, syn.symbols, syn.effects, syn.motion, syn.utilities;', css[:400])

    def test_theme_tokens_and_components(self):
        css = (ROOT/'dist/syntyr.css').read_text()
        for item in ('[data-syn-theme="grid"]', '[data-syn-theme="noir"]',
                     '.syn-button', '.syn-panel', '.syn-badge', '.syn-popover',
                     '.syn-dialog', '.syn-input', '.syn-grid', '.syn-meter'):
            with self.subTest(item=item): self.assertIn(item, css)
        self.assertIn('prefers-reduced-motion: reduce', css)
        self.assertIn('forced-colors: active', css)
        self.assertIn(':focus-visible', css)

    def test_demo_no_javascript_and_native_controls(self):
        p = DemoParser()
        p.feed((ROOT/'index.html').read_text())
        self.assertEqual(p.scripts, [])
        self.assertTrue({'details', 'summary', 'dialog', 'progress', 'form'} <= set(p.tags))
        self.assertTrue(set(p.targets) <= p.popovers)
        self.assertTrue(p.targets)
        self.assertIn(('grid-dialog','show-modal'), p.commands)
        self.assertTrue(all(not x.startswith(('http:', 'https:', '//')) for x in p.resources))

    def test_wcag_aa_core_theme_contrast(self):
        for name, bg, surface, text, muted, accent, on_accent in (
            ('grid', '#080f19', '#111f2c', '#edf9ff', '#adbfca', '#76e7f7', '#07121a'),
            ('noir', '#0e0e12', '#1c1b20', '#f8eee5', '#c3b5aa', '#f1b574', '#1c100b'),
        ):
            for label, front, back in (
                ('body text', text, bg), ('panel text', text, surface),
                ('muted on panel', muted, surface), ('button label', on_accent, accent),
            ):
                with self.subTest(theme=name, label=label):
                    self.assertGreaterEqual(contrast(front, back),4.5)

    def test_no_package_manager_or_remote_assets(self):
        self.assertFalse((ROOT/'package.json').exists())
        self.assertFalse((ROOT/'node_modules').exists())

if __name__ == '__main__': unittest.main()
