"""Contracts for docs-only Design Lab and validated copy-owned page compositions."""
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import unittest

from scripts.syntyr_check import validate_html

ROOT = Path(__file__).resolve().parents[1]


class PageStructure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.refs = []
        self.frames = []
        self.scripts = []
        self.links = []
        self.headings = []

    def handle_starttag(self, tag, attrs):
        attr = dict(attrs)
        if attr.get('id'):
            self.ids.append(attr['id'])
        for ref_attr in ('aria-labelledby', 'aria-describedby'):
            self.refs.extend((attr.get(ref_attr) or '').split())
        if attr.get('for'):
            self.refs.append(attr['for'])
        if tag == 'iframe':
            self.frames.append(attr)
        if tag == 'script':
            self.scripts.append(attr)
        if tag == 'link':
            self.links.append(attr.get('href', ''))
        if tag in ('h1', 'h2', 'h3'):
            self.headings.append(tag)


class DesignLabContract(unittest.TestCase):
    def test_comparison_controls_and_sandboxed_previews(self):
        page = (ROOT / 'docs/playground.html').read_text()
        parser = PageStructure()
        parser.feed(page)
        for control in ('playground-compare', 'playground-compare-theme',
                        'playground-viewport', 'playground-density', 'playground-radius',
                        'playground-radius-value', 'playground-copy-configured',
                        'playground-preview', 'playground-preview-compare'):
            self.assertIn(control, parser.ids)
        self.assertEqual(len(parser.frames), 2)
        for frame in parser.frames:
            self.assertEqual(frame.get('sandbox'), 'allow-same-origin')
            self.assertNotIn('allow-scripts', frame.get('sandbox', ''))
        self.assertEqual(len(parser.ids), len(set(parser.ids)))
        self.assertTrue(set(parser.refs) <= set(parser.ids), set(parser.refs)-set(parser.ids))

    def test_comparison_is_docs_only_and_build_free(self):
        script = (ROOT / 'docs/playground.js').read_text()
        styles = (ROOT / 'docs/playground.css').read_text()
        for text in ('playground-preview-compare', 'data-syn-density',
                     '--syn-radius', 'playground-viewport', 'playground-copy-configured',
                     'srcdoc'):
            self.assertIn(text, script)
        for text in ('playground-frame-grid', 'playground-device',
                     'overflow', '@media'):
            self.assertIn(text, styles)
        self.assertNotIn('fetch(', script)
        self.assertNotIn('localStorage', script)
        self.assertNotIn('<script', (ROOT / 'examples/composition-operations-dashboard.html').read_text().lower())

    def test_generated_agent_compositions_match_existing_css(self):
        manifest = json.loads((ROOT / 'metadata/agent-compositions.json').read_text())
        blocks = {block['id']: block for block in json.loads((ROOT / 'blocks/manifest.json').read_text())['blocks']}
        self.assertEqual(manifest['version'], 1)
        self.assertEqual({r['id'] for r in manifest['recipes']},
                         {'operations-dashboard', 'product-marketing'})
        contract = json.loads((ROOT / 'metadata/syntyr-contract.json').read_text())
        for recipe in manifest['recipes']:
            with self.subTest(recipe=recipe['id']):
                self.assertGreaterEqual(len(recipe['blocks']), 3)
                self.assertEqual(len(recipe['blocks']), len(set(recipe['blocks'])))
                self.assertTrue(set(recipe['blocks']) <= set(blocks))
                self.assertIn(recipe['theme'], ('studio', 'grid', 'noir'))
                page_path = ROOT / 'examples' / f"composition-{recipe['id']}.html"
                page = page_path.read_text()
                parser = PageStructure(); parser.feed(page)
                self.assertEqual(len(parser.ids), len(set(parser.ids)), page_path.name)
                self.assertTrue(set(parser.refs) <= set(parser.ids))
                self.assertEqual(parser.scripts, [])
                self.assertEqual(parser.headings.count('h1'), 1)
                self.assertEqual(parser.links, sorted(parser.links))
                self.assertFalse(any(s.startswith(('https:', 'http:', '//')) for s in parser.links))
                modules = {module for block in recipe['blocks'] for module in blocks[block]['modules']}
                for module in modules:
                    self.assertIn(f'../dist/syntyr.{module}.css', parser.links)
                self.assertEqual(validate_html(page, contract), [])

    def test_generator_is_deterministic_and_examples_are_discoverable(self):
        run = subprocess.run([sys.executable, 'scripts/build_agent_compositions.py', '--check'],
                             cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        for file in ('composition-operations-dashboard.html', 'composition-product-marketing.html'):
            self.assertIn(file, (ROOT / 'docs/index.html').read_text())
            self.assertIn(file, (ROOT / 'scripts/build_cloudflare_site.py').read_text())
        self.assertIn('metadata/agent-compositions.json', (ROOT / 'docs/agent-integration.md').read_text())


if __name__ == '__main__':
    unittest.main()
