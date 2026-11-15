"""Regressions for Syntyr's optional, CSS-native motion layer."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MotionContract(unittest.TestCase):
    def test_motion_is_independently_loadable_and_only_in_full_bundle(self):
        from scripts.build import distributions
        bundles = distributions()
        self.assertEqual(bundles['syntyr.motion.css'], ('motion.css',))
        self.assertIn('motion.css', bundles['syntyr.all.css'])
        for name in ('syntyr.core.css', 'syntyr.css', 'syntyr.effects.css'):
            self.assertNotIn('motion.css', bundles[name])
        self.assertEqual((ROOT / 'dist/syntyr.motion.css').read_text(),
                         (ROOT / 'src/motion.css').read_text().strip() + '\n')

    def test_motion_is_scoped_and_uses_independent_opt_in_presets(self):
        css = (ROOT / 'src/motion.css').read_text()
        self.assertIn('@layer syn.motion', css)
        self.assertIn('.syn-root', css)
        for name in ('fade', 'enter', 'scale', 'reveal'):
            self.assertIn(f'[data-syn-animate="{name}"]', css)
        for direction in ('up', 'down', 'left', 'right'):
            self.assertIn(f'[data-syn-from="{direction}"]', css)
        self.assertIn('--syn-motion-index', css)
        self.assertIn('--syn-motion-delay', css)
        self.assertIn('prefers-reduced-motion: no-preference', css)
        self.assertIn('animation-fill-mode: backwards', css)
        self.assertNotIn('animation-iteration-count: infinite', css)

    def test_css_native_overlay_and_loading_effects_are_opt_in(self):
        css = (ROOT / 'src/motion.css').read_text()
        self.assertIn('transition-behavior: allow-discrete', css)
        self.assertIn('@starting-style', css)
        self.assertIn(':popover-open', css)
        self.assertIn('.syn-motion-dialog', css)
        self.assertIn('.syn-motion-popover', css)
        self.assertIn('.syn-loader', css)
        self.assertIn('forced-colors: active', css)

    def test_motion_showcase_is_public_and_free_of_runtime_scripts(self):
        html = (ROOT / 'examples/motion.html').read_text()
        self.assertIn('syntyr.motion.css', html)
        self.assertIn('data-syn-animate="enter"', html)
        self.assertIn('class="syn-loader"', html)
        self.assertNotIn('<script', html.lower())
        self.assertIn('href="../examples/motion.html"',
                      (ROOT / 'docs/index.html').read_text())
        from scripts.build_cloudflare_site import source_files
        self.assertIn('examples/motion.html', source_files())

    def test_tokens_keep_motion_overrideable_without_runtime(self):
        css = (ROOT / 'src/tokens.css').read_text()
        for token in ('--syn-motion-duration', '--syn-motion-duration-slow',
                      '--syn-motion-distance', '--syn-motion-stagger',
                      '--syn-ease-out'):
            self.assertIn(token, css)
        self.assertIn('syn.motion', css.partition('\n')[0])
        self.assertFalse((ROOT / 'dist/syntyr.core.css').read_text().count('[data-syn-animate="enter"]'))

    def test_motion_guide_documents_accessible_opt_in_and_html_fallback(self):
        docs = (ROOT / 'docs/motion.md').read_text()
        for term in ('syntyr.motion.css', 'prefers-reduced-motion',
                     'data-syn-animate="enter"', 'data-syn-from="left"',
                     'data-syn-animate="reveal"', 'data-syn-stagger',
                     'aria-hidden="true"', 'View Transitions', 'AutoAnimate'):
            self.assertIn(term, docs)


if __name__ == '__main__':
    unittest.main()
