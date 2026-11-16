"""Accessible, optional CSS-only UI patterns for applications using AI agents."""
import json
import re
import unittest
from pathlib import Path

from agent_mcp.catalog import CatalogError, SyntyrCatalog
from scripts.build_blocks import build

ROOT = Path(__file__).resolve().parents[1]
PATTERNS = {"ai-conversation", "ai-tool-run", "ai-approval"}


class AiAgentPatternsTests(unittest.TestCase):
    def test_three_copy_owned_patterns_are_discoverable_with_explicit_modules(self):
        blocks = json.loads((ROOT / 'blocks/manifest.json').read_text())['blocks']
        indexed = {item['id']: item for item in blocks}
        self.assertTrue(PATTERNS.issubset(indexed))
        for name in PATTERNS:
            with self.subTest(name=name):
                self.assertEqual(indexed[name]['category'], 'AI interfaces')
                self.assertEqual(indexed[name]['modules'], ['core', 'recipes'])
                self.assertTrue(indexed[name]['description'])
                self.assertTrue((ROOT / 'blocks/snippets' / f'{name}.html').is_file())

    def test_patterns_use_real_scoped_css_and_no_runtime_javascript(self):
        css = (ROOT / 'src/recipes.css').read_text()
        catalog = SyntyrCatalog()
        for name in PATTERNS:
            html = (ROOT / 'blocks/snippets' / f'{name}.html').read_text()
            self.assertIn('class="syn-root ', html)
            self.assertNotIn('<script', html.lower())
            self.assertNotIn('onclick=', html.lower())
            self.assertNotIn('href="#"', html)
            classes = {c for attr in re.findall(r'class="([^"]+)"', html)
                       for c in attr.split() if c.startswith('syn-ai-')}
            self.assertTrue(classes)
            for cls in classes:
                self.assertIn('.' + cls, css, (name, cls))
            valid = catalog.validate_markup(html, '0.3.0-alpha.5',
                                            ['syntyr.core.css', 'syntyr.recipes.css'])
            self.assertEqual(valid['unknown_classes'], [], (name, valid))
            self.assertEqual(valid['missing_stylesheets'], [], (name, valid))
            core_only = catalog.validate_markup(html, '0.3.0-alpha.5', ['syntyr.core.css'])
            self.assertIn('syntyr.recipes.css', core_only['missing_stylesheets'])

    def test_native_semantics_and_honest_approval_states(self):
        conversation = (ROOT / 'blocks/snippets/ai-conversation.html').read_text()
        self.assertIn('<ol class="syn-ai-thread"', conversation)
        self.assertIn('Assistant', conversation)
        self.assertIn('You', conversation)
        self.assertNotIn('aria-live="assertive"', conversation)
        tool = (ROOT / 'blocks/snippets/ai-tool-run.html').read_text()
        self.assertIn('<details class="syn-ai-tool"', tool)
        self.assertIn('<summary', tool)
        self.assertIn('<code>', tool)
        approval = (ROOT / 'blocks/snippets/ai-approval.html').read_text()
        self.assertIn('Awaiting approval', approval)
        self.assertIn('type="button" disabled', approval)
        self.assertNotIn('<form', approval)  # Demo cannot submit a fake approval.

    def test_agent_mcp_and_composition_catalog_follow_release_boundaries(self):
        catalog = SyntyrCatalog()
        result = catalog.get_component('AI agent interfaces', '0.3.0-alpha.5')
        self.assertIn('syn-ai-thread', result['component']['classes'])
        with self.assertRaises(CatalogError):
            catalog.get_component('AI agent interfaces', '0.3.0-alpha.4')
        metadata = json.loads((ROOT / 'metadata/components.json').read_text())
        self.assertTrue(any(c['name'] == 'AI agent interfaces' for c in metadata['components']))

    def test_static_gallery_lists_patterns_without_hardcoded_count(self):
        markup = build()
        self.assertIn('23 production-shaped blocks.', markup)
        self.assertIn('23 blocks available.', markup)
        self.assertIn('value="AI interfaces"', markup)
        for name in PATTERNS:
            self.assertIn(f'data-block-id="{name}"', markup)
        self.assertIn('AI interface patterns', (ROOT / 'docs/agent-integration.md').read_text())


if __name__ == '__main__':
    unittest.main()
