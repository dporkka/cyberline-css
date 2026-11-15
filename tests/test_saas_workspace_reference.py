"""Contract for Syntyr's script-free SaaS workspace reference and Rust SSR adapter."""
from html.parser import HTMLParser
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class Markup(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.links = []
        self.labels = set()
        self.inputs = []
        self.buttons = []
        self.forms = []
        self.scripts = 0
        self.inline_handlers = []
        self.landmarks = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if attrs.get('id'):
            self.ids.append(attrs['id'])
        if tag == 'a':
            self.links.append(attrs.get('href', ''))
        if tag == 'label' and attrs.get('for'):
            self.labels.add(attrs['for'])
        if tag in ('input', 'select', 'textarea'):
            self.inputs.append(attrs)
        if tag == 'button':
            self.buttons.append(attrs)
        if tag == 'form':
            self.forms.append(attrs)
        if tag == 'script':
            self.scripts += 1
        if tag in ('main', 'nav'):
            self.landmarks.append((tag, attrs))
        self.inline_handlers.extend(key for key in attrs if key.startswith('on'))


class SaaSWorkspaceReference(unittest.TestCase):
    def test_reference_is_accessible_script_free_and_not_a_fake_backend(self):
        page = (ROOT / 'examples/saas-workspace.html').read_text()
        html = Markup(); html.feed(page)
        self.assertEqual(html.scripts, 0)
        self.assertFalse(html.inline_handlers)
        self.assertEqual(len(html.ids), len(set(html.ids)), 'IDs must be unique')
        self.assertEqual(sum(1 for name, _ in html.landmarks if name == 'main'), 1)
        for section in ('main', 'workspace', 'members', 'billing', 'developer', 'states'):
            self.assertIn(section, html.ids)
        for dest in html.links:
            if dest.startswith('#') and len(dest) > 1:
                self.assertIn(dest[1:], html.ids)
        self.assertIn('#main', html.links, 'keyboard skip navigation')
        self.assertIn('aria-current="page"', page)
        self.assertIn('syn-app-shell', page)
        self.assertIn('syn-table-wrap', page)
        self.assertIn('syn-meter', page)
        self.assertIn('syn-empty', page)
        self.assertIn('syn-skeleton', page)
        self.assertIn('role="status"', page)
        self.assertIn('role="alert"', page)
        self.assertIn('type="email"', page)
        self.assertTrue({'invite-email', 'invite-role'} <= html.labels)
        self.assertTrue({'invite-email', 'invite-role'} <= set(html.ids))
        self.assertTrue(all('disabled' in field for field in html.inputs if field.get('name') in ('email','role')))
        self.assertTrue(all('disabled' in button for button in html.buttons if button.get('type') == 'submit'))
        self.assertFalse(html.forms, 'static example must not claim to submit actual changes')
        self.assertIn('fictional', page.lower())
        self.assertIn('server', page.lower())

    def test_all_assets_local_and_demo_styles_scoped(self):
        root = ROOT / 'examples'
        page = (root / 'saas-workspace.html').read_text()
        for href in ('../dist/syntyr.core.css', '../dist/syntyr.recipes.css', 'saas-workspace.css'):
            self.assertIn('href="' + href + '"', page)
            self.assertTrue((root / href).is_file())
        css = (root / 'saas-workspace.css').read_text()
        self.assertIn('.workspace-demo-', css)
        self.assertNotIn('@import', css)
        self.assertNotIn('url(', css)
        self.assertNotIn('@keyframes', css)

    def test_rust_template_has_server_owned_html_and_csrf(self):
        template = (ROOT / 'integrations/rust-saas-foundation/workspace.askama.html').read_text()
        html = Markup(); html.feed(template)
        self.assertEqual(html.scripts, 0)
        self.assertIn('class="syn-root syn-page"', template)
        self.assertIn('{{ workspace_name }}', template)
        self.assertIn('{% for member in members %}', template)
        self.assertIn('{{ csrf_token }}', template)
        self.assertIn('name="csrf_token"', template)
        self.assertIn('method="post"', template)
        self.assertIn('name="email"', template)
        self.assertIn('name="role"', template)
        self.assertIn('role="alert"', template)
        self.assertIn('aria-live="polite"', template)

    def test_documentation_and_public_discovery(self):
        readme = (ROOT / 'README.md').read_text()
        guide = (ROOT / 'docs/rust-saas-integration.md').read_text()
        docs_index = (ROOT / 'docs/index.html').read_text()
        allowlist = (ROOT / 'scripts/build_cloudflare_site.py').read_text()
        for filename in ('saas-workspace.html', 'saas-workspace.css'):
            self.assertIn(filename, allowlist)
        self.assertIn('examples/saas-workspace.html', readme)
        self.assertIn('saas-workspace.html', docs_index)
        self.assertIn('workspace.askama.html', guide)
        self.assertIn('authorization', guide.lower())
        self.assertIn('CSRF', guide)
        self.assertIn('server-rendered', guide.lower())


if __name__ == '__main__':
    unittest.main()
