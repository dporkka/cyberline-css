"""Consumer-facing CLI behavior and distribution tests."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/syntyr_cli.py"
PACKAGE = ROOT / "scripts/package_cli.py"
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()


def run_cli(*args, cwd=ROOT, cli=CLI):
    return subprocess.run([sys.executable, str(cli), *map(str, args)],
                          cwd=cwd, capture_output=True, input="", text=True)


class SyntyrCliTests(unittest.TestCase):
    def test_version_and_discovery_are_machine_readable(self):
        version = run_cli("version", "--format", "json")
        self.assertEqual(version.returncode, 0, version.stderr)
        self.assertEqual(json.loads(version.stdout), {"version": VERSION})
        listed = run_cli("list", "--category", "blocks", "--format", "json")
        self.assertEqual(listed.returncode, 0, listed.stderr)
        items = json.loads(listed.stdout)
        self.assertTrue(any(item["name"] == "settings-form" for item in items))
        self.assertFalse(any(item["name"] == "core" for item in items))
        self.assertTrue(all("description" in item for item in items))

    def test_dry_run_apply_verify_and_detect_drift(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            preview = run_cli("add", "settings-form", "--project", project, "--format", "json")
            self.assertEqual(preview.returncode, 0, preview.stderr)
            self.assertTrue(json.loads(preview.stdout)["files"])
            self.assertFalse((project / "syntyr").exists())
            applied = run_cli("add", "settings-form", "--project", project, "--apply", "--format", "json")
            self.assertEqual(applied.returncode, 0, applied.stderr)
            lock = project / "syntyr.lock.json"
            self.assertTrue(lock.is_file())
            verified = run_cli("verify", "--project", project, "--format", "json")
            self.assertEqual(verified.returncode, 0, verified.stderr)
            self.assertEqual(json.loads(verified.stdout)["status"], "ok")
            (project / "syntyr/blocks/settings-form.html").write_text("changed", encoding="utf-8")
            drift = run_cli("verify", "--project", project, "--format", "json")
            self.assertEqual(drift.returncode, 1)
            self.assertIn("modified-file", [d["code"] for d in json.loads(drift.stdout)["diagnostics"]])

    def test_check_delegates_to_static_validator_and_preserves_exit_status(self):
        with tempfile.TemporaryDirectory() as folder:
            html = Path(folder) / "page.html"
            html.write_text('<html><body class="syn-root"><button class="syn-buttn">Save</button></body></html>', encoding="utf-8")
            result = run_cli("check", "--format", "json", html)
            self.assertEqual(result.returncode, 1)
            self.assertIn("unknown-class", [d["code"] for d in json.loads(result.stdout)])

    def test_packaged_cli_executes_from_unrelated_project(self):
        with tempfile.TemporaryDirectory() as folder:
            output = Path(folder) / "syntyr-cli.zip"
            built = subprocess.run([sys.executable, str(PACKAGE), str(output)],
                                   cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            with ZipFile(output) as archive:
                names = archive.namelist()
                self.assertTrue(any(n.endswith("scripts/syntyr_cli.py") for n in names))
                self.assertFalse(any("/business/" in n or "/.env" in n for n in names))
                archive.extractall(folder)
            extracted = Path(folder) / f"syntyr-cli-{VERSION}" / "scripts/syntyr_cli.py"
            project = Path(folder) / "app"
            project.mkdir()
            self.assertEqual(run_cli("version", "--format", "json", cli=extracted).returncode, 0)
            installed = run_cli("add", "settings-form", "--project", project,
                                "--apply", "--format", "json", cli=extracted)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            self.assertEqual(run_cli("verify", "--project", project, cli=extracted).returncode, 0)
            checked = run_cli("check", "--format", "json", "-", cli=extracted)
            # stdin is empty; the checker still works with bundled contract.
            self.assertEqual(checked.returncode, 0, checked.stderr)
            doctor_html = project / "duplicate.html"
            doctor_html.write_text('<html><head><link rel="stylesheet" href="syntyr.core.css"><link rel="stylesheet" href="syntyr.core.css"></head></html>')
            diagnosed = run_cli("doctor", "--format", "json", doctor_html, cli=extracted)
            self.assertEqual(diagnosed.returncode, 0, diagnosed.stderr)
            self.assertIn("duplicate-stylesheet", [d["code"] for d in json.loads(diagnosed.stdout)])


    def test_check_warning_is_nonfatal_unless_fail_on_warning_is_requested(self):
        with tempfile.TemporaryDirectory() as folder:
            html = Path(folder) / "warnings.html"
            html.write_text('<html><body><table><tr><th>Name</th></tr></table></body></html>')
            normal = run_cli("check", "--semantic", "--format", "json", html)
            self.assertEqual(normal.returncode, 0, normal.stderr)
            self.assertIn("table-missing-name", [d["code"] for d in json.loads(normal.stdout)])
            strict = run_cli("check", "--semantic", "--fail-on", "warning", "--format", "json", html)
            self.assertEqual(strict.returncode, 1, strict.stderr)
            self.assertIn("table-missing-name", [d["code"] for d in json.loads(strict.stdout)])


    def test_doctor_command_is_discoverable_and_flags_duplicate_stylesheets(self):
        usage = run_cli("--help")
        self.assertEqual(usage.returncode, 0, usage.stderr)
        self.assertIn("doctor", usage.stdout)
        self.assertIn("check", usage.stdout)
        with tempfile.TemporaryDirectory() as folder:
            html = Path(folder) / "page.html"
            html.write_text('''<html><head>
<link rel="stylesheet" href="/dist/syntyr.core.css">
<link rel="stylesheet" href="/dist/syntyr.core.css">
</head><body></body></html>''' )
            report = run_cli("doctor", "--format", "json", html)
            self.assertEqual(report.returncode, 0, report.stderr)
            self.assertIn("duplicate-stylesheet", [d["code"] for d in json.loads(report.stdout)])
            strict = run_cli("doctor", "--fail-on", "warning", "--format", "json", html)
            self.assertEqual(strict.returncode, 1, strict.stderr)

    def test_doctor_rejects_mixed_versioned_css_pins(self):
        with tempfile.TemporaryDirectory() as folder:
            html = Path(folder) / "page.html"
            html.write_text('''<html><head>
<link rel="stylesheet" href="/v/0.3.0-alpha.4/syntyr.core.css">
<link rel="stylesheet" href="/v/0.3.0-alpha.5/syntyr.recipes.css">
</head><body></body></html>''' )
            report = run_cli("doctor", "--format", "json", html)
            self.assertEqual(report.returncode, 1, report.stderr)
            self.assertIn("mixed-stylesheet-versions", [d["code"] for d in json.loads(report.stdout)])


if __name__ == "__main__":
    unittest.main()
