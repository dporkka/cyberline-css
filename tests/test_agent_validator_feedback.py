"""Agent-friendly feedback from the optional Syntyr static HTML checker."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from syntyr_check import validate_html  # noqa: E402


class AgentValidatorFeedbackTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = json.loads((ROOT / "metadata/syntyr-contract.json").read_text())

    def test_unknown_class_suggests_real_classes_with_stylesheet_requirements(self):
        diagnostics = validate_html('<button class="syn-buttn">Save</button>', self.contract)
        self.assertEqual([d["code"] for d in diagnostics], ["unknown-class"])
        suggestion = next(s for s in diagnostics[0]["suggestions"] if s["name"] == "syn-button")
        self.assertIn("syntyr.core.css", suggestion["stylesheets"])
        self.assertTrue(all(s["name"].startswith("syn-") for s in diagnostics[0]["suggestions"]))

    def test_unrelated_unknown_class_does_not_invent_a_replacement(self):
        diagnostics = validate_html('<main class="syn-zzzzzzzzzz"></main>', self.contract)
        self.assertEqual(diagnostics[0]["suggestions"], [])

    def test_invalid_attribute_has_machine_readable_allowed_values(self):
        diagnostics = validate_html('<main data-syn-theme="purple"></main>', self.contract)
        self.assertEqual(diagnostics[0]["code"], "invalid-attribute-value")
        self.assertEqual(diagnostics[0]["attribute"], "data-syn-theme")
        self.assertIn("studio", diagnostics[0]["allowed_values"])
        self.assertNotIn("purple", diagnostics[0]["allowed_values"])

    def test_missing_module_reports_all_valid_stylesheets(self):
        html = '<link rel="stylesheet" href="syntyr.core.css"><main class="syn-root syn-pipeline"></main>'
        diagnostics = validate_html(html, self.contract)
        self.assertEqual([d["code"] for d in diagnostics], ["missing-stylesheet"])
        self.assertIn("syntyr.recipes.css", diagnostics[0]["required_stylesheets"])
        self.assertEqual(diagnostics[0]["loaded_stylesheets"], ["syntyr.core.css"])

    def test_cli_accepts_stdin_and_keeps_existing_json_shape(self):
        result = subprocess.run(
            [sys.executable, "scripts/syntyr_check.py", "--format", "json", "-"],
            cwd=ROOT, text=True, input='<button class="syn-buttn">Save</button>',
            capture_output=True,
        )
        self.assertEqual(result.returncode, 1, result.stderr)
        diagnostics = json.loads(result.stdout)
        self.assertIsInstance(diagnostics, list)
        self.assertEqual(diagnostics[0]["file"], "<stdin>")
        self.assertEqual(diagnostics[0]["suggestions"][0]["name"], "syn-button")

    def test_cli_stdin_success_and_explicit_stylesheet_context(self):
        result = subprocess.run(
            [sys.executable, "scripts/syntyr_check.py", "--format", "json",
             "--stylesheets", "syntyr.core.css", "-"],
            cwd=ROOT, text=True, input='<main class="syn-root syn-panel"></main>',
            capture_output=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), [])


if __name__ == "__main__":
    unittest.main()
