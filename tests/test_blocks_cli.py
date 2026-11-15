"""Dependency-free, safe installation contract for free Syntyr blocks."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts/blocks_cli.py"


def invoke(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CLI), *arguments],
        cwd=ROOT, text=True, capture_output=True,
    )


class BlocksCliTests(unittest.TestCase):
    def test_catalog_json_is_machine_readable_and_does_not_require_install(self):
        result = invoke("list", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        catalog = json.loads(result.stdout)
        self.assertEqual(catalog["version"], 1)
        self.assertEqual(len(catalog["blocks"]), 20)
        self.assertIn("metric-overview", {block["id"] for block in catalog["blocks"]})
        self.assertTrue(all(block["modules"][0] == "core" for block in catalog["blocks"]))

    def test_catalog_category_filter_is_case_insensitive(self):
        result = invoke("list", "--category", "applications", "--json")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertGreater(len(json.loads(result.stdout)["blocks"]), 0)
        self.assertTrue(all(
            b["category"] == "Applications"
            for b in json.loads(result.stdout)["blocks"]
        ))

    def test_install_copies_only_requested_blocks_and_required_css(self):
        with tempfile.TemporaryDirectory() as root:
            destination = Path(root) / "project"
            result = invoke(
                "install", "metric-overview", "hero-product",
                "--output", str(destination),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            installed = destination / "syntyr"
            expected = {
                "blocks/metric-overview.html", "blocks/hero-product.html",
                "css/syntyr.core.css", "css/syntyr.recipes.css",
                "README.md", "LICENSE-MIT", "installed.json",
            }
            self.assertEqual(
                {str(p.relative_to(installed)) for p in installed.rglob("*") if p.is_file()},
                expected,
            )
            manifest = json.loads((installed / "installed.json").read_text())
            self.assertEqual(manifest["schema_version"], 1)
            self.assertEqual(manifest["syntyr_version"], (ROOT / "VERSION").read_text().strip())
            self.assertEqual(manifest["blocks"], ["metric-overview", "hero-product"])
            self.assertEqual(manifest["modules"], ["core", "recipes"])
            for name, digest in manifest["sha256"].items():
                self.assertEqual(
                    hashlib.sha256((installed / name).read_bytes()).hexdigest(),
                    digest,
                )
            self.assertEqual(
                (installed / "LICENSE-MIT").read_bytes(),
                (ROOT / "LICENSE").read_bytes(),
            )
            self.assertEqual(
                (installed / "css/syntyr.core.css").read_bytes(),
                (ROOT / "dist/syntyr.core.css").read_bytes(),
            )
            self.assertIn("static examples", (installed / "README.md").read_text())
            self.assertIn("syntyr.core.css", (installed / "README.md").read_text())

    def test_invalid_id_fails_before_creating_any_files(self):
        with tempfile.TemporaryDirectory() as root:
            destination = Path(root) / "project"
            result = invoke(
                "install", "metric-overview", "../../secrets",
                "--output", str(destination),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Unknown block", result.stderr)
            self.assertFalse(destination.exists())

    def test_collision_does_not_overwrite_or_partially_install(self):
        with tempfile.TemporaryDirectory() as root:
            dest = Path(root) / "project"
            target = dest / "syntyr/blocks/metric-overview.html"
            target.parent.mkdir(parents=True)
            target.write_text("DO NOT OVERWRITE")
            result = invoke(
                "install", "metric-overview", "hero-product",
                "--output", str(dest),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(target.read_text(), "DO NOT OVERWRITE")
            self.assertFalse((dest / "syntyr/blocks/hero-product.html").exists())
            self.assertFalse((dest / "syntyr/css").exists())

    def test_dry_run_has_no_file_system_side_effects(self):
        with tempfile.TemporaryDirectory() as root:
            destination = Path(root) / "project"
            result = invoke(
                "install", "metric-overview",
                "--output", str(destination), "--dry-run",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("syntyr/blocks/metric-overview.html", result.stdout)
            self.assertFalse(destination.exists())

    def test_symlink_in_an_ancestor_of_output_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            real_directory = root / "real"
            real_directory.mkdir()
            (root / "alias").symlink_to(real_directory, target_is_directory=True)
            result = invoke(
                "install", "metric-overview",
                "--output", str(root / "alias/project"),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlink", result.stderr.lower())
            self.assertFalse((real_directory / "project").exists())

    def test_symlinked_output_tree_is_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            root = Path(root)
            dest = root / "project"
            (dest / "syntyr").mkdir(parents=True)
            (dest / "syntyr/css").symlink_to(root, target_is_directory=True)
            result = invoke(
                "install", "metric-overview",
                "--output", str(dest),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlink", result.stderr.lower())
            self.assertFalse((root / "syntyr.core.css").exists())


if __name__ == "__main__":
    unittest.main()
