"""Optional explicit CSS composition without runtime or scan heuristics."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
COMMAND = [sys.executable, str(ROOT / "scripts/build_selective.py")]


class SelectiveBuildTests(unittest.TestCase):
    def run_builder(self, *args):
        return subprocess.run(
            COMMAND + list(map(str, args)),
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_explicit_modules_include_only_requested_sources(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "selected.css"
            result = self.run_builder(
                "--components", "buttons",
                "--modules", "print,semantic",
                "--output", out,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            css = out.read_text()
            self.assertIn("@layer syn.tokens", css)
            self.assertIn("@layer syn.base", css)
            self.assertIn("@layer syn.components", css)
            self.assertIn("&.syn-button {", css)
            self.assertIn("@layer syn.semantic {", css)
            self.assertIn("@layer syn.print {", css)
            self.assertNotIn("&.syn-panel {", css)
            self.assertNotIn("&.syn-input {", css)
            self.assertNotIn("@layer syn.effects {", css)
            self.assertLess(css.index("@layer syn.semantic {"), css.index("@layer syn.print {"))

    def test_default_equals_versioned_core_distribution(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "core.css"
            result = self.run_builder("--output", out)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(out.read_bytes(),
                             (ROOT / "dist/syntyr.core.css").read_bytes())

    def test_form_composition_includes_base_form_controls(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "fields.css"
            result = self.run_builder(
                "--components", "form-composition", "--output", out
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            css = out.read_text()
            self.assertIn("&.syn-input, &.syn-select, &.syn-textarea", css)
            self.assertIn("&.syn-input-group", css)

    def test_output_and_report_are_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            out1, out2 = root / "a.css", root / "b.css"
            report1, report2 = root / "a.json", root / "b.json"
            options = ("--components", "data,buttons",
                       "--modules", "effects,symbols")
            a = self.run_builder(*options, "--output", out1, "--report", report1)
            b = self.run_builder(*options, "--output", out2, "--report", report2)
            self.assertEqual(a.returncode, 0, a.stderr)
            self.assertEqual(b.returncode, 0, b.stderr)
            self.assertEqual(out1.read_bytes(), out2.read_bytes())
            self.assertEqual(report1.read_bytes(), report2.read_bytes())
            report = json.loads(report1.read_text())
            self.assertEqual(report["included_sources"][:2], ["tokens.css", "base.css"])
            self.assertIn("components/buttons.css", report["included_sources"])
            self.assertGreater(report["raw_bytes"], report["gzip_bytes"])

    def test_invalid_components_and_modules_fail_before_writing(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "output.css"
            for opts in (("--components", "buttons,unknown"),
                         ("--components", ""),
                         ("--modules", "unknown"),
                         ("--modules", "effects,,print")):
                with self.subTest(options=opts):
                    result = self.run_builder(*opts, "--output", out)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertFalse(out.exists())
                    self.assertIn("error", result.stderr.lower())

    def test_never_overwrite_versioned_or_generated_dist_files(self):
        blocked = ROOT / "dist" / "syntyr.core.css"
        before = blocked.read_bytes()
        result = self.run_builder(
            "--components", "buttons", "--output", blocked
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(blocked.read_bytes(), before)
        self.assertIn("dist", result.stderr.lower())

    def test_report_cannot_overwrite_css_or_distributions(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "generated.css"
            result = self.run_builder(
                "--components", "buttons", "--output", out, "--report", out
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(out.exists())


if __name__ == "__main__":
    unittest.main()
