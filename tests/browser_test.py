"""Opt-in Playwright browser smoke and interaction tests against real Chromium.

Run: python3 tests/browser_test.py
Browser infrastructure is developer-only, never a Syntyr runtime dependency.
"""
from pathlib import Path
import os
import shutil
import unittest

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
# Inlining local CSS avoids network/file:// navigation blocked by some hardened CI browsers.

class BrowserTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p = sync_playwright().start()
        kwargs = dict(headless=True)
        executable = (os.environ.get('PLAYWRIGHT_CHROMIUM_EXECUTABLE')
                      or shutil.which('chromium')
                      or shutil.which('chromium-browser'))
        if executable:
            kwargs['executable_path'] = executable
            kwargs['args'] = ['--no-sandbox']
        cls.browser = cls.p.chromium.launch(**kwargs)

    @classmethod
    def tearDownClass(cls):
        cls.browser.close()
        cls.p.stop()

    def setUp(self):
        self.context = self.browser.new_context(viewport={'width': 1280, 'height': 900}, device_scale_factor=1)
        self.page = self.context.new_page()
        self.errors = []
        self.page.on('pageerror', lambda error: self.errors.append(str(error)))
        html = (ROOT / 'docs/index.html').read_text(encoding='utf-8')
        css = (ROOT / 'dist/syntyr.all.css').read_text(encoding='utf-8')
        docs_css = (ROOT / 'docs/docs.css').read_text(encoding='utf-8')
        html = html.replace('<link rel="stylesheet" href="../dist/syntyr.all.css">', f'<style>{css}</style>')
        html = html.replace('<link rel="stylesheet" href="docs.css">', f'<style>{docs_css}</style>')
        self.page.set_content(html, wait_until='load')

    def tearDown(self):
        self.assertFalse(self.errors, self.errors)
        self.context.close()

    def test_theme_tokens_are_applied_and_nested(self):
        root = self.page.locator('body')
        grid = self.page.locator('#themes [data-syn-theme="grid"]')
        noir = self.page.locator('#themes [data-syn-theme="noir"]')
        self.assertEqual(root.evaluate("e => getComputedStyle(e).getPropertyValue('--syn-accent').trim()"), '#76e7f7')
        self.assertEqual(grid.evaluate("e => getComputedStyle(e).getPropertyValue('--syn-accent').trim()"), '#76e7f7')
        self.assertEqual(noir.evaluate("e => getComputedStyle(e).getPropertyValue('--syn-accent').trim()"), '#f1b574')
        self.assertEqual(grid.locator('.syn-panel').count(), 0) # this panel *is* the theme root

    def test_semantic_mode_is_scoped_and_styled(self):
        semantic_button = self.page.locator('#semantic .syn-semantic button')
        self.assertEqual(semantic_button.count(), 1)
        self.assertEqual(semantic_button.evaluate('e => getComputedStyle(e).minHeight'), '44px')
        semantic_article = self.page.locator('#semantic .syn-semantic article')
        self.assertEqual(semantic_article.evaluate('e => getComputedStyle(e).backgroundColor'), 'rgb(17, 31, 44)')
        self.page.evaluate("""() => {
          const b = document.createElement('button');
          b.id = 'unstyled-external';
          b.textContent = 'Outside';
          document.body.appendChild(b);
        }""")
        external = self.page.locator('#unstyled-external')
        self.assertNotEqual(external.evaluate('e => getComputedStyle(e).minHeight'), '44px')

    def test_semantic_mode_leaves_range_input_native(self):
        self.page.evaluate("""() => {
          const range = document.createElement('input');
          range.id = 'range-audit';
          range.type = 'range';
          document.querySelector('.syn-semantic article').appendChild(range);
        }""")
        range_border = self.page.locator('#range-audit').evaluate('e => getComputedStyle(e).borderTopWidth')
        self.assertEqual(range_border, '0px')

    def test_embedded_root_does_not_force_viewport_height(self):
        self.page.evaluate("""() => {
          const section = document.createElement('section');
          section.id = 'embedded-root';
          section.className = 'syn-root';
          section.innerHTML = '<span>Small widget</span>';
          document.body.appendChild(section);
        }""")
        min_height = self.page.locator('#embedded-root').evaluate('e => getComputedStyle(e).minHeight')
        self.assertNotEqual(min_height, '900px')

    def test_popover_opens_and_escape_dismisses(self):
        popover = self.page.locator('#command-popover')
        self.assertFalse(popover.evaluate('e => e.matches(":popover-open")'))
        self.page.get_by_role('button', name='OPEN COMMAND').click()
        self.assertTrue(popover.evaluate('e => e.matches(":popover-open")'))
        self.page.keyboard.press('Escape')
        self.assertFalse(popover.evaluate('e => e.matches(":popover-open")'))

    def test_invoker_dialog_opens_and_closes(self):
        dialog = self.page.locator('#diagnostic-dialog')
        self.page.get_by_role('button', name='OPEN DIALOG').click()
        self.assertTrue(dialog.evaluate('e => e.open'))
        self.assertTrue(dialog.evaluate('e => e.matches(":modal")'))
        self.page.get_by_role('button', name='ACKNOWLEDGE').click()
        self.assertFalse(dialog.evaluate('e => e.open'))

    def test_disclosure_and_keyboard_focus(self):
        disclosure = self.page.locator('#components details').first
        self.assertFalse(disclosure.evaluate('e => e.open'))
        disclosure.locator('summary').click()
        self.assertTrue(disclosure.evaluate('e => e.open'))
        self.page.keyboard.press('Tab')
        # Focus styles should never be set to none by the framework.
        focus_color = self.page.locator(':focus').evaluate('e => getComputedStyle(e).outlineStyle')
        self.assertNotEqual(focus_color, 'none')

    def test_mobile_has_no_document_horizontal_overflow(self):
        self.page.set_viewport_size({'width': 375, 'height': 812})
        values = self.page.evaluate('() => ({sw:document.documentElement.scrollWidth, cw:document.documentElement.clientWidth})')
        self.assertLessEqual(values['sw'], values['cw'] + 1, values)

    def test_reduced_motion_disables_transitions(self):
        self.page.emulate_media(reduced_motion='reduce')
        duration = self.page.locator('.syn-button--primary').first.evaluate('e => getComputedStyle(e).transitionDuration')
        self.assertIn(duration, ('0s', '0s, 0s, 0s'), duration)

    def test_container_query_cards_adapt_to_parent_not_viewport(self):
        region = self.page.locator('#recipes .syn-region').first
        stats = region.locator('.syn-stats')
        def columns():
            return len(stats.evaluate('e => getComputedStyle(e).gridTemplateColumns').split())
        region.evaluate('e => e.style.width = "380px"')
        self.assertEqual(columns(), 1)
        region.evaluate('e => e.style.width = "550px"')
        self.assertEqual(columns(), 2)
        region.evaluate('e => e.style.width = "950px"')
        self.assertEqual(columns(), 3)

    def test_attribute_variants_preserve_semantics(self):
        self.page.emulate_media(reduced_motion='reduce')
        self.page.evaluate("""() => {
          const button = document.createElement('button');
          button.id = 'v03-state';
          button.className = 'syn-button';
          button.textContent = 'Toggle';
          document.querySelector('#recipes').appendChild(button);
        }""")
        b = self.page.locator('#v03-state')
        base = b.evaluate('e => getComputedStyle(e).color')
        b.evaluate('e => e.setAttribute("aria-pressed", "true")')
        pressed = b.evaluate('e => getComputedStyle(e).color')
        self.assertNotEqual(base, pressed)
        self.assertEqual(b.get_attribute('aria-pressed'), 'true')
        b.evaluate('e => e.setAttribute("aria-busy", "true")')
        self.assertEqual(b.evaluate('e => getComputedStyle(e).cursor'), 'progress')

    def test_unlayered_host_theme_overrides_token(self):
        self.page.add_style_tag(content='.syn-root[data-syn-theme="grid"] { --syn-accent: #99ffcc; }')
        self.assertEqual(self.page.locator('body').evaluate(
            'e => getComputedStyle(e).getPropertyValue("--syn-accent").trim()'), '#99ffcc')

    def test_noir_pricing_example_is_responsive_and_local(self):
        html = (ROOT / 'examples/pricing.html').read_text(encoding='utf-8')
        core = (ROOT / 'dist/syntyr.core.css').read_text(encoding='utf-8')
        effects = (ROOT / 'dist/syntyr.effects.css').read_text(encoding='utf-8')
        html = html.replace('<link rel="stylesheet" href="../dist/syntyr.core.css">', f'<style>{core}</style>')
        html = html.replace('<link rel="stylesheet" href="../dist/syntyr.effects.css">', f'<style>{effects}</style>')
        self.page.set_viewport_size({'width': 390, 'height': 844})
        self.page.set_content(html)
        pricing = self.page.locator('.syn-pricing')
        self.assertEqual(len(pricing.evaluate('e => getComputedStyle(e).gridTemplateColumns').split()), 1)
        self.assertLessEqual(self.page.evaluate('document.documentElement.scrollWidth'), 391)
        self.page.set_viewport_size({'width': 1280, 'height': 900})
        self.assertEqual(len(pricing.evaluate('e => getComputedStyle(e).gridTemplateColumns').split()), 3)
        self.assertEqual(self.page.locator('.syn-price-card').count(), 3)

    def test_forced_colors_still_has_visible_control_border(self):
        self.page.emulate_media(forced_colors='active')
        color = self.page.get_by_role('button', name='OPEN COMMAND').evaluate('e => getComputedStyle(e).borderTopStyle')
        self.assertEqual(color, 'solid')

    def test_studio_theme_is_scoped_and_uses_light_controls(self):
        studio = self.page.locator('#themes [data-syn-theme="studio"]')
        self.assertEqual(studio.count(), 1)
        self.assertEqual(studio.evaluate(
            "e => getComputedStyle(e).getPropertyValue('--syn-accent').trim()"), '#2458c6')
        self.assertEqual(studio.evaluate("e => getComputedStyle(e).colorScheme"), 'light')
        self.assertEqual(self.page.locator('body').evaluate(
            "e => getComputedStyle(e).colorScheme"), 'dark')

    def test_nested_studio_recipe_surfaces_have_matching_foreground_and_background(self):
        core = (ROOT / "dist/syntyr.core.css").read_text()
        recipes = (ROOT / "dist/syntyr.recipes.css").read_text()
        self.page.set_content(f"""<style>{core}{recipes}</style>
        <main class="syn-root" data-syn-theme="grid">
            <section data-syn-theme="studio">
                <aside class="syn-app-rail" id="nested-rail">Studio rail</aside>
                <article class="syn-app-card" id="nested-card">Studio card</article>
                <section class="syn-site-hero" id="nested-hero">Studio hero</section>
                <section class="syn-feature-card" id="nested-feature">Studio feature</section>
            </section>
        </main>""")
        for selector in ("#nested-rail", "#nested-card", "#nested-hero", "#nested-feature"):
            with self.subTest(selector=selector):
                computed = self.page.locator(selector).evaluate(
                    "e => ({fg: getComputedStyle(e).color, bg: getComputedStyle(e).backgroundColor})")
                self.assertEqual(computed["fg"], "rgb(21, 35, 58)")
                self.assertEqual(computed["bg"], "rgb(255, 255, 255)")

    def test_new_recipes_have_no_mobile_overflow_and_work_at_desktop_width(self):
        core = (ROOT / 'dist/syntyr.core.css').read_text()
        recipes = (ROOT / 'dist/syntyr.recipes.css').read_text()
        for example in ('saas.html', 'business.html', 'terminal.html'):
            with self.subTest(example=example):
                html = (ROOT / 'examples' / example).read_text()
                html = html.replace('<link rel="stylesheet" href="../dist/syntyr.core.css">',
                                    f'<style>{core}</style>')
                html = html.replace('<link rel="stylesheet" href="../dist/syntyr.recipes.css">',
                                    f'<style>{recipes}</style>')
                for width in (360, 1280):
                    with self.subTest(width=width):
                        self.page.set_viewport_size({'width': width, 'height': 900})
                        self.page.set_content(html)
                        metrics = self.page.evaluate(
                            "() => ({scrollWidth: document.documentElement.scrollWidth, "
                            "clientWidth: document.documentElement.clientWidth})")
                        self.assertLessEqual(metrics['scrollWidth'],
                                             metrics['clientWidth'] + 1, metrics)
                        self.assertEqual(self.page.locator('main').count(), 1)
                if example == 'saas.html':
                    self.assertEqual(self.page.locator('.syn-app-shell').count(), 1)
                    self.assertEqual(self.page.locator('.syn-table .syn-status').count(), 3)
                if example == 'business.html':
                    self.assertGreater(
                        self.page.locator('.business-visual').bounding_box()['x'], 600)
                if example == 'terminal.html':
                    self.assertEqual(self.page.locator('.syn-terminal').evaluate(
                        'e => getComputedStyle(e).backgroundColor'), 'rgb(11, 22, 37)')
                    positions = self.page.locator('.syn-terminal-line').evaluate_all(
                        'els => els.map(e => e.getBoundingClientRect().top)')
                    self.assertLessEqual(positions[1] - positions[0], 30)
                    studio_chip = self.page.locator('.cli-options [data-syn-theme="studio"]')
                    self.assertEqual(studio_chip.evaluate(
                        'e => getComputedStyle(e).backgroundColor'), 'rgb(255, 255, 255)')


    def test_opt_in_deferred_sections_render_and_print_without_becoming_hidden(self):
        core = (ROOT / 'dist/syntyr.core.css').read_text()
        recipes = (ROOT / 'dist/syntyr.recipes.css').read_text()
        self.page.set_content(f'''<style>{core}{recipes}</style>
          <main class="syn-root syn-page" data-syn-theme="studio">
            <section style="height: 1400px">Top section</section>
            <section class="syn-defer-section" id="deferred"
                     style="--syn-defer-size: 24rem">
              <h2>Detailed report</h2><button class="syn-button">Open</button>
            </section>
            <section id="normal">Always rendered</section>
          </main>''')
        deferred = self.page.locator('#deferred')
        self.assertEqual(deferred.evaluate('e => getComputedStyle(e).contentVisibility'), 'auto')
        self.assertEqual(self.page.locator('#normal').evaluate(
            'e => getComputedStyle(e).contentVisibility'), 'visible')
        deferred.scroll_into_view_if_needed()
        self.assertTrue(deferred.get_by_role('button', name='Open').is_visible())
        self.page.emulate_media(media='print')
        self.assertEqual(deferred.evaluate('e => getComputedStyle(e).contentVisibility'), 'visible')
        self.assertEqual(deferred.evaluate('e => getComputedStyle(e).containIntrinsicSize'), 'none')


if __name__ == '__main__':
    unittest.main(verbosity=2)
