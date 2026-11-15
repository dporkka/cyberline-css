"""Contracts for reusable, CSS-only priority queues and data-grid visual states."""
import sys
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from build import distributions, assemble


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.scripts = 0
        self.remote = []
        self.root = False
        self.ids = set()
        self.labels = set()
        self.controls = set()
        self.links = []
        self.tables = 0
        self.captions = 0
        self.th_scopes = []
        self.scroll_regions = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get('class', '').split()
        self.root |= 'syn-root' in classes
        if tag == 'script':
            self.scripts += 1
        if tag in ('script', 'link', 'img'):
            url = attrs.get('src') or attrs.get('href', '')
            if url.startswith(('http:', 'https:', '//')):
                self.remote.append(url)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        if tag == 'label' and attrs.get('for'):
            self.labels.add(attrs['for'])
        if tag in ('input', 'select') and attrs.get('id'):
            self.controls.add(attrs['id'])
        if tag == 'a' and attrs.get('href', '').startswith('#'):
            self.links.append(attrs['href'][1:])
        if tag == 'table':
            self.tables += 1
        if tag == 'caption':
            self.captions += 1
        if tag == 'th':
            self.th_scopes.append(attrs.get('scope'))
        if 'syn-data-grid-scroll' in classes:
            self.scroll_regions.append((attrs.get('tabindex'), attrs.get('aria-label')))


class AdacavoPatternsTests(unittest.TestCase):
    def test_modules_are_optional_not_in_core_and_ship_in_all(self):
        manifest = distributions()
        for name, filename in [('syntyr.operations.css', 'operations.css'), ('syntyr.data-grid.css', 'data-grid.css')]:
            self.assertEqual(manifest[name], (filename,))
            self.assertIn(filename, manifest['syntyr.all.css'])
            self.assertNotIn(filename, manifest['syntyr.core.css'])
            self.assertEqual((ROOT / 'dist' / name).read_text(), assemble((filename,)))
        package = (ROOT / 'package.json').read_text()
        self.assertIn('"./operations.css"', package)
        self.assertIn('"./data-grid.css"', package)

    def test_queue_exposes_priority_not_fake_actions(self):
        css = (ROOT / 'src/operations.css').read_text()
        for selector in ('.syn-work-queue', '.syn-work-item', '.syn-work-marker', '.syn-work-content', '.syn-work-meta', '.syn-work-actions', '[data-syn-priority="critical"]', '[data-syn-priority="high"]', ':focus-visible', 'forced-colors: active'):
            self.assertIn(selector, css)
        self.assertIn('prefers-reduced-motion', css)
        self.assertIn('.syn-root', css)
        self.assertNotIn('@import', css)
        self.assertNotIn('!important', css)

    def test_grid_states_are_host_driven_and_semantic(self):
        css = (ROOT / 'src/data-grid.css').read_text()
        for selector in ('.syn-data-grid-scroll', '.syn-data-grid-table', '.syn-data-grid-cell', '.syn-data-grid-bulkbar', '[data-syn-state="selected"]', '[data-syn-state="dirty"]', '[data-syn-state="invalid"]', '[data-syn-state="readonly"]', '[aria-invalid="true"]', ':focus-within', '[aria-sort="ascending"]', 'forced-colors: active'):
            self.assertIn(selector, css)
        self.assertIn('tabular-nums', css)
        self.assertIn('prefers-reduced-motion', css)
        self.assertNotIn('@import', css)
        self.assertNotIn('!important', css)

    def test_example_is_a_no_js_read_only_real_html_reference(self):
        page = (ROOT / 'examples/operations-ui-states.html').read_text()
        audit = Markup()
        audit.feed(page)
        self.assertTrue(audit.root)
        self.assertEqual(audit.scripts, 0)
        self.assertEqual(audit.remote, [])
        self.assertEqual(audit.tables, 1)
        self.assertEqual(audit.captions, 1)
        self.assertTrue(set(audit.th_scopes) <= {'col', 'row'})
        self.assertEqual(set(audit.links) - audit.ids, set())
        self.assertTrue(audit.controls <= audit.labels)
        self.assertTrue(all(tab == '0' and label for tab, label in audit.scroll_regions))
        self.assertIn('syntyr.operations.css', page)
        self.assertIn('syntyr.data-grid.css', page)
        self.assertIn('Illustrative records', page)
        self.assertIn('not implemented', page)
        self.assertNotIn('type="submit"', page)


if __name__ == '__main__':
    unittest.main()
