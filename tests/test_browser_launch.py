"""Portable developer-only Playwright browser selection."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from browser_launch import launch_options


class BrowserLaunch(unittest.TestCase):
    def test_explicit_custom_binaries_apply_to_every_engine(self):
        for engine in ('chromium', 'firefox', 'webkit'):
            with self.subTest(engine=engine):
                env = {f'PLAYWRIGHT_{engine.upper()}_EXECUTABLE': f'/local/{engine}'}
                with patch.dict(os.environ, env, clear=True):
                    options = launch_options(engine)
                self.assertEqual(options['executable_path'], f'/local/{engine}')
                self.assertTrue(options['headless'])

    def test_non_chromium_engines_use_playwright_default_without_override(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(launch_options('firefox'), {'headless': True})
            self.assertEqual(launch_options('webkit'), {'headless': True})

    def test_chromium_uses_local_fallback_only_without_override(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch('browser_launch.shutil.which', side_effect=lambda name: '/usr/bin/chromium' if name == 'chromium' else None):
                options = launch_options('chromium')
        self.assertEqual(options['executable_path'], '/usr/bin/chromium')
        self.assertIn('--no-sandbox', options['args'])


if __name__ == '__main__':
    unittest.main()
