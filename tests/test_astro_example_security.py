"""Prevent reintroducing insecure Astro 5 dependency into optional example."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AstroExampleSecurity(unittest.TestCase):
    def test_example_uses_patched_astro_7_series_and_declares_node_engine(self):
        data = json.loads((ROOT / "examples/astro/package.json").read_text())
        self.assertTrue(data["private"])
        self.assertEqual(data["dependencies"]["astro"], "^7.4.12")
        self.assertEqual(data["engines"]["node"], ">=22.23.4")
        self.assertEqual(data["dependencies"]["@syntyr/css"], "file:../..")

    def test_documentation_has_supported_build_commands(self):
        readme = (ROOT / "examples/astro/README.md").read_text()
        self.assertIn("Node.js 22.23.4", readme)
        self.assertIn("npm run build", readme)
        self.assertIn("no Syntyr JavaScript runtime", readme)

if __name__ == "__main__":
    unittest.main()
