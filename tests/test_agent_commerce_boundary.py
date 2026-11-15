"""An optional commerce Worker must never get bundled into the static MIT site."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


class AgentCommerceBoundaryTests(unittest.TestCase):
    def test_public_docs_exist_but_worker_sources_are_private(self):
        with TemporaryDirectory() as tmp:
            output = Path(tmp) / "site"
            result = subprocess.run([
                sys.executable, str(ROOT / "scripts/build_cloudflare_site.py"),
                "--output", str(output),
            ], cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue((output / "docs/agent-commerce.md").is_file())
            self.assertTrue((output / "docs/agent-commerce.html").is_file())
            self.assertFalse((output / "commerce").exists())
            self.assertFalse((output / "src/app.js").exists())
            self.assertFalse(list(output.rglob("wrangler*.toml")))
            self.assertNotIn("whsec_", (output / "docs/agent-commerce.html").read_text())
            self.assertIn("agent-commerce.html", (output / "docs/reference.html").read_text())

    def test_root_package_keeps_zero_runtime_payment_dependencies(self):
        package = (ROOT / "package.json").read_text()
        self.assertNotIn("@x402", package)
        self.assertNotIn("stripe", package)


if __name__ == "__main__":
    unittest.main()
