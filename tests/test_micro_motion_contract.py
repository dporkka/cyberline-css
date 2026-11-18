"""Opt-in motion must remain dependency-free and accessible."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class MicroMotionContract(unittest.TestCase):
    def test_five_recipes_are_supported_by_optional_styles_and_native_js(self):
        source = (ROOT / 'src/motion.css').read_text()
        for recipe in ('insert', 'notice', 'saved', 'expand'):
            self.assertIn(f'data-syn-motion="{recipe}"', source)
        self.assertIn('prefers-reduced-motion: no-preference', source)
        self.assertIn('::details-content', source)
        self.assertIn('interpolate-size: allow-keywords', source)
        self.assertIn('withViewTransition', (ROOT / 'src/animate.mjs').read_text())

    def test_external_lottie_player_is_not_a_runtime_dependency(self):
        package = json.loads((ROOT / 'package.json').read_text())
        self.assertNotIn('@lottiefiles/dotlottie-wc', package.get('dependencies', {}))
        self.assertNotIn('@lottiefiles/dotlottie-web', package.get('dependencies', {}))
        self.assertEqual(package['exports']['./dotlottie'], {
            'types': './dist/syntyr.dotlottie.d.mts',
            'default': './dist/syntyr.dotlottie.mjs',
        })
        self.assertIn('connectDotLottie', (ROOT / 'src/dotlottie.mjs').read_text())
        self.assertNotIn('dotlottie', (ROOT / 'dist/syntyr.core.css').read_text().lower())

    def test_optional_lottie_distribution_and_documentation_are_shipped(self):
        from scripts.build import javascript_distributions
        from scripts.package_release import FILES
        from scripts.build_cloudflare_site import source_files
        self.assertEqual(javascript_distributions()['syntyr.dotlottie.mjs'], 'dotlottie.mjs')
        for name in ('syntyr.dotlottie.mjs', 'syntyr.dotlottie.d.mts'):
            self.assertEqual((ROOT / 'src' / name.replace('syntyr.', '')).read_bytes(),
                             (ROOT / 'dist' / name).read_bytes())
            self.assertIn('dist/' + name, FILES)
        self.assertIn('docs/dotlottie.md', FILES)
        self.assertIn('docs/dotlottie.md', source_files())
        self.assertIn('tests/dotlottie.test.mjs', (ROOT / '.woodpecker/js-adoption.yaml').read_text())


if __name__ == '__main__':
    unittest.main()
