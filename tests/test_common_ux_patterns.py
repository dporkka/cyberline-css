"""Contract tests for native-first common website and app interactions."""
from html.parser import HTMLParser
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.nodes = []

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))

    def elements(self, tag):
        return [attrs for name, attrs in self.nodes if name == tag]


class CommonUXContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.example = ROOT / 'examples/common-ux.html'
        cls.html = cls.example.read_text() if cls.example.exists() else ''
        cls.markup = Markup()
        cls.markup.feed(cls.html)

    def test_native_dropdown_is_regular_navigation_not_fake_menu_role(self):
        targets = {b.get('popovertarget') for b in self.markup.elements('button')}
        popovers = {n.get('id') for n in self.markup.elements('div') if 'popover' in n}
        self.assertTrue(targets & popovers)
        self.assertNotIn('role="menu"', self.html)
        self.assertIn('syn-action-menu', self.html)

    def test_drawer_and_gallery_use_native_modal_invokers_and_close_buttons(self):
        dialogs = {d.get('id'): d for d in self.markup.elements('dialog')}
        invokers = [b for b in self.markup.elements('button') if b.get('command') == 'show-modal']
        self.assertGreaterEqual(len(invokers), 4)
        self.assertTrue(all(b.get('commandfor') in dialogs for b in invokers))
        self.assertTrue(all('aria-labelledby' in d for d in dialogs.values()))
        self.assertGreaterEqual(len([f for f in self.markup.elements('form') if f.get('method') == 'dialog']), 4)
        self.assertIn('syn-drawer', self.html)
        self.assertIn('syn-gallery', self.html)
        self.assertGreaterEqual(len(self.markup.elements('img')), 6)
        self.assertTrue(all(img.get('alt') is not None for img in self.markup.elements('img')))

    def test_native_date_range_is_labeled_get_form_with_distinct_names(self):
        dates = [i for i in self.markup.elements('input') if i.get('type') == 'date']
        self.assertEqual({i.get('name') for i in dates}, {'date_from', 'date_to'})
        labels = {l.get('for') for l in self.markup.elements('label')}
        self.assertTrue(all(i.get('id') in labels for i in dates))
        self.assertTrue(any(f.get('method') == 'get' for f in self.markup.elements('form')))
        self.assertIn('validate the date order on the server', self.html)

    def test_copy_has_scoped_status_without_inline_event_handlers(self):
        buttons = [b for b in self.markup.elements('button') if b.get('data-syn-copy-target')]
        self.assertEqual(len(buttons), 1)
        self.assertTrue(any('data-syn-feedback-scope' in n for _, n in self.markup.nodes))
        statuses = [n for _, n in self.markup.nodes if 'data-syn-feedback-status' in n]
        self.assertEqual(len(statuses), 1)
        self.assertEqual(statuses[0].get('role'), 'status')
        self.assertTrue(all(not any(k.startswith('on') for k in n) for _, n in self.markup.nodes))
        self.assertIn('src="./common-ux.mjs"', self.html)
        self.assertIn('enhanceFeedback(', (ROOT / 'examples/common-ux.mjs').read_text())
        self.assertNotIn('<script type="module">', self.html)
        self.assertIn('data-syn-copy-target', (ROOT / 'src/feedback.mjs').read_text())

    def test_optional_assets_and_docs_are_discoverable(self):
        css = (ROOT / 'src/native-recipes.css').read_text()
        for name in ('.syn-action-menu', '.syn-drawer', '.syn-gallery', '.syn-gallery-dialog', '.syn-toast-region'):
            with self.subTest(selector=name):
                self.assertIn(name, css)
        build = (ROOT / 'scripts/build.py').read_text()
        self.assertIn("'syntyr.feedback.mjs': 'feedback.mjs'", build)
        self.assertIn('syntyr.feedback.mjs', (ROOT / 'docs/native-patterns.md').read_text())
        self.assertIn('common-ux.html', (ROOT / 'docs/native-patterns.md').read_text())
        self.assertEqual((ROOT / 'dist/syntyr.feedback.mjs').read_bytes(), (ROOT / 'src/feedback.mjs').read_bytes())
        self.assertIn('.syn-gallery-dialog', (ROOT / 'dist/syntyr.native-recipes.css').read_text())
        package = json.loads((ROOT / 'package.json').read_text())
        self.assertEqual(package['exports'].get('./feedback'), {
            'types': './dist/syntyr.feedback.d.mts',
            'default': './dist/syntyr.feedback.mjs',
        })
        from scripts.package_release import FILES
        self.assertIn('dist/syntyr.feedback.mjs', FILES)
        self.assertIn('dist/syntyr.feedback.d.mts', FILES)
        from scripts.build_cloudflare_site import source_files
        public = source_files()
        self.assertIn('examples/common-ux.html', public)
        self.assertIn('examples/common-ux.mjs', public)
        self.assertIn('dist/syntyr.feedback.mjs', public)


if __name__ == '__main__':
    unittest.main()
