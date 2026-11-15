"""CI should gate releases without adding a consumer-side dependency."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]


def active_workflow_command_position(source: str, command: str) -> int:
    """Find a real list entry, excluding commented-out Woodpecker steps."""
    match = re.search(r"(?m)^[ \t]*-[ \t]+" + re.escape(command) + r"[ \t]*$", source)
    return match.start() if match else -1


class ContinuousIntegrationContract(unittest.TestCase):
    def test_pull_requests_and_main_pushes_run_standard_library_gates(self):
        workflow = ROOT / ".woodpecker" / "quality.yaml"
        self.assertTrue(workflow.is_file(), "A PR quality workflow is required")
        content = workflow.read_text(encoding="utf-8")
        for contract in (
            "event: pull_request",
            "event: push",
            "branch: main",
            "python:3.14-slim",
            "python3 scripts/build.py --check",
            "python3 -m unittest discover -s tests -v",
            "python3 scripts/build_cloudflare_site.py",
            "python3 scripts/build_cloudflare_site.py --check",
            "python3 scripts/package_release.py",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, content)

    def test_quality_runner_installs_git_before_git_tracking_tests(self):
        # Python slim has no Git CLI. Several brand/distribution tests use
        # git ls-files, so the CI image must supply Git before running them.
        content = (ROOT / ".woodpecker" / "quality.yaml").read_text()
        install = "apt-get install -y --no-install-recommends git"
        self.assertIn("apt-get update", content)
        self.assertIn(install, content)
        self.assertIn("git --version", content)
        self.assertLess(content.index(install), content.index("python3 -m unittest discover"))

    def test_commented_blocks_command_is_not_an_active_release_step(self):
        command = "python3 tests/blocks_browser.py --browsers chromium firefox webkit"
        self.assertEqual(active_workflow_command_position("#      - " + command, command), -1)
        self.assertEqual(active_workflow_command_position("      # - " + command, command), -1)
        self.assertGreaterEqual(active_workflow_command_position("      - " + command, command), 0)

    def test_blocks_gallery_is_in_three_engine_release_browser_gate(self):
        workflow = (ROOT / ".woodpecker" / "browser.yaml").read_text(encoding="utf-8")
        blocks = active_workflow_command_position(
            workflow, "python3 tests/blocks_browser.py --browsers chromium firefox webkit")
        matrix = active_workflow_command_position(
            workflow, "python3 tests/browser_matrix.py --browsers chromium firefox webkit")
        self.assertGreaterEqual(blocks, 0, "Blocks browser test must be an active workflow step")
        self.assertGreaterEqual(matrix, 0, "Browser matrix must be an active workflow step")
        self.assertIn("event: manual", workflow)
        self.assertIn("event: tag", workflow)
        self.assertLess(matrix, blocks)

    def test_release_browser_matrix_is_explicit_and_not_a_runtime_dependency(self):
        workflow = ROOT / ".woodpecker" / "browser.yaml"
        self.assertTrue(workflow.is_file(), "Require a reproducible release browser workflow")
        content = workflow.read_text(encoding="utf-8")
        for contract in (
            "event: manual",
            "event: tag",
            "playwright/python:v1.65.2-noble",
            "python3 tests/browser_matrix.py --browsers chromium firefox webkit",
            "python3 tests/reflow_test.py --browsers chromium firefox webkit",
            "python3 tests/theme_editor_browser.py",
            "python3 tests/design_workflow_browser.py --browsers chromium firefox webkit",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, content)


if __name__ == "__main__":
    unittest.main()
