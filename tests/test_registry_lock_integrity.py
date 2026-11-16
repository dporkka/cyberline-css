"""Registry lockfile integrity and failure recovery."""
import json
from pathlib import Path
from unittest import mock
import tempfile
import unittest

from scripts import registry_install
from scripts.registry_install import plan_install, apply_install, verify_install, RegistryError


class RegistryIntegrityTests(unittest.TestCase):
    def test_apply_records_exact_bytes_and_verify_identifies_modified_file(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            plan = plan_install("settings-form", project)
            apply_install(plan, project)
            lock = json.loads((project / "syntyr.lock.json").read_text())
            self.assertEqual(lock["schema"], 1)
            self.assertIn("settings-form", lock["items"])
            self.assertIn("syntyr/css/syntyr.core.css", lock["files"])
            self.assertEqual(verify_install(project), [])
            (project / "syntyr/css/syntyr.core.css").write_bytes(b"custom css")
            self.assertIn("modified-file", [d["code"] for d in verify_install(project)])
            with self.assertRaises(RegistryError):
                apply_install(plan_install("recipes", project), project)

    def test_write_error_rolls_back_only_new_files_and_lockfile(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            plan = plan_install("settings-form", project)
            original = registry_install._write_new_file
            def fail_later(path, data):
                if path.name == "settings-form.html":
                    raise OSError("disk full")
                return original(path, data)
            with mock.patch.object(registry_install, "_write_new_file", side_effect=fail_later):
                with self.assertRaises(OSError):
                    apply_install(plan, project)
            self.assertFalse((project / "syntyr/css/syntyr.core.css").exists())
            self.assertFalse((project / "syntyr/LICENSE").exists())
            self.assertFalse((project / "syntyr.lock.json").exists())

    def test_repeated_add_merges_lockfile_without_discarding_other_items(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            apply_install(plan_install("settings-form", project), project)
            apply_install(plan_install("resource-workspace", project), project)
            lock = json.loads((project / "syntyr.lock.json").read_text())
            self.assertEqual(lock["items"], ["resource-workspace", "settings-form"])
            self.assertEqual(verify_install(project), [])

    def test_modified_lockfile_rejected_without_overwriting_user_data(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            apply_install(plan_install("core", project), project)
            lockfile = project / "syntyr.lock.json"
            lockfile.write_text("user content", encoding="utf-8")
            with self.assertRaises(RegistryError):
                apply_install(plan_install("recipes", project), project)
            self.assertEqual(lockfile.read_text(), "user content")
            self.assertFalse((project / "syntyr/css/syntyr.recipes.css").exists())


    def test_partial_disk_write_is_removed_without_lockfile(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            plan = plan_install("core", project)
            original = registry_install.os.fdopen
            class FailingOutput:
                def __init__(self, stream):
                    self.stream = stream
                def __enter__(self):
                    return self
                def __exit__(self, *args):
                    self.stream.close()
                def write(self, data):
                    self.stream.write(data[:8])
                    raise OSError("disk full mid-write")
            with mock.patch.object(registry_install.os, "fdopen", side_effect=lambda fd, mode: FailingOutput(original(fd, mode))):
                with self.assertRaises(OSError):
                    apply_install(plan, project)
            self.assertFalse((project / "syntyr/css/syntyr.core.css").exists())
            self.assertFalse((project / "syntyr.lock.json").exists())


    def test_verify_rejects_lockfile_from_a_different_release(self):
        with tempfile.TemporaryDirectory() as folder:
            project = Path(folder)
            apply_install(plan_install("core", project), project)
            file = project / "syntyr.lock.json"
            lock = json.loads(file.read_text())
            lock["version"] = "0.0.0"
            file.write_text(json.dumps(lock))
            self.assertIn("version-mismatch", [d["code"] for d in verify_install(project)])


if __name__ == "__main__":
    unittest.main()
