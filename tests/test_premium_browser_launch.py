"""Regression checks for the optional premium Playwright launcher (stdlib only)."""
import importlib.util
import os
from pathlib import Path
import sys
from types import ModuleType
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]


def load_runner():
    """Load launcher without requiring Playwright in the Python-only CI lane."""
    fake_pkg = ModuleType("playwright")
    fake_api = ModuleType("playwright.sync_api")
    fake_api.sync_playwright = lambda: None
    spec = importlib.util.spec_from_file_location(
        "syntyr_premium_runner", ROOT / "tests/premium_compositions_browser.py"
    )
    module = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"playwright": fake_pkg, "playwright.sync_api": fake_api}):
        spec.loader.exec_module(module)
    return module


class PremiumBrowserLaunch(unittest.TestCase):
    def test_explicit_chromium_override_wins(self):
        runner = load_runner()
        with patch.dict(os.environ, {"PLAYWRIGHT_CHROMIUM_EXECUTABLE": "/custom/chromium"}, clear=True):
            with patch.object(runner.shutil, "which", return_value="/usr/bin/chromium"):
                opts = runner.chromium_launch_options()
        self.assertEqual(opts["executable_path"], "/custom/chromium")
        self.assertTrue(opts["headless"])

    def test_system_chromium_browser_fallback(self):
        runner = load_runner()
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(runner.shutil, "which", side_effect=[None, "/usr/bin/chromium-browser"]) as which:
                opts = runner.chromium_launch_options()
        self.assertEqual(which.call_args_list[0].args, ("chromium",))
        self.assertEqual(which.call_args_list[1].args, ("chromium-browser",))
        self.assertEqual(opts["executable_path"], "/usr/bin/chromium-browser")
        self.assertEqual(opts["args"], ["--no-sandbox"])

    def test_headless_default_without_local_executable(self):
        runner = load_runner()
        with patch.dict(os.environ, {}, clear=True):
            with patch.object(runner.shutil, "which", return_value=None):
                self.assertEqual(runner.chromium_launch_options(), {"headless": True})


if __name__ == "__main__":
    unittest.main()
