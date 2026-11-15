"""Optional developer browser binary overrides must not affect consumers."""
import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location("browser_options",ROOT/"tests/browser_options.py")

def load():
    module=importlib.util.module_from_spec(SPEC)
    SPEC.loader.exec_module(module)
    return module

class BrowserOptionsContract(unittest.TestCase):
    def test_webkit_wrapper_can_be_supplied_without_runtime_packages(self):
        opts=load().launch_options("webkit", env={"PLAYWRIGHT_WEBKIT_EXECUTABLE":"/tmp/user-local-wrapper"}, which=lambda _:None)
        self.assertEqual(opts,{"headless":True,"executable_path":"/tmp/user-local-wrapper"})

    def test_firefox_path_is_respected(self):
        opts=load().launch_options("firefox",env={"PLAYWRIGHT_FIREFOX_EXECUTABLE":"/tmp/firefox"},which=lambda _:None)
        self.assertEqual(opts["executable_path"],"/tmp/firefox")
        self.assertNotIn("args",opts)

    def test_chromium_system_fallback_and_no_sandbox(self):
        opts=load().launch_options("chromium",env={},which=lambda n:"/usr/bin/chromium" if n=="chromium" else None)
        self.assertEqual(opts["executable_path"],"/usr/bin/chromium")
        self.assertIn("--no-sandbox",opts["args"])

    def test_unconfigured_webkit_uses_playwright_default(self):
        self.assertEqual(load().launch_options("webkit",env={},which=lambda _:None),{"headless":True})

    def test_unsupported_engine_is_rejected(self):
        with self.assertRaises(ValueError):
            load().launch_options("safari",env={},which=lambda _:None)

if __name__=="__main__":
    unittest.main()
