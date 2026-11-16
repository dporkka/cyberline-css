"""Consumer-facing onboarding and optional diagnostics shipped in the release archive."""
import json
import re
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile

from scripts.package_release import FILES, package
from scripts.build_cloudflare_site import source_files

ROOT = Path(__file__).resolve().parents[1]


def css_has_class(css, cls):
    return re.search(rf"\.{re.escape(cls)}(?![\w\\-])", css) is not None


class ReleaseDeveloperExperienceTests(unittest.TestCase):
    def test_css_class_lookup_requires_complete_class_names(self):
        css = ".syn-textarea {} .syn-text-support {} .syn-text_foo {} .syn-text2 {}"
        self.assertFalse(css_has_class(css, "syn-text"))
        self.assertTrue(css_has_class(css, "syn-textarea"))
        self.assertTrue(css_has_class(".syn-text:hover {}", "syn-text"))

    def test_release_contains_version_matched_optional_html_checker(self):
        for path in ("scripts/syntyr_check.py", "metadata/syntyr-contract.json"):
            self.assertIn(path, FILES)

        with tempfile.TemporaryDirectory(prefix="syntyr-dx-") as tmp:
            archive_path = Path(tmp) / "syntyr.zip"
            package(archive_path)
            with ZipFile(archive_path) as archive:
                archive.extractall(Path(tmp) / "unpacked")
            roots = list((Path(tmp) / "unpacked").glob("syntyr-css-*"))
            self.assertEqual(len(roots), 1)
            installed = roots[0]
            self.assertEqual(
                json.loads((installed / "metadata/syntyr-contract.json").read_text())["source_version"],
                (ROOT / "VERSION").read_text().strip(),
            )
            checker = installed / "scripts/syntyr_check.py"
            self.assertTrue(checker.is_file())

            def check(html):
                proc = subprocess.run(
                    [sys.executable, str(checker), "--format", "json", "-"],
                    input=html, capture_output=True, text=True,
                    cwd=installed,
                )
                return proc, json.loads(proc.stdout)

            valid = ('<html><head><link rel="stylesheet" href="dist/syntyr.core.css">'
                     '</head><body class="syn-root"><button class="syn-button '
                     'syn-button--primary">Save</button></body></html>')
            good_proc, good_diagnostics = check(valid)
            self.assertEqual(good_proc.returncode, 0, good_proc.stderr)
            self.assertEqual(good_diagnostics, [])

            bad_proc, bad_diagnostics = check(valid.replace("syn-button--primary", "syn-buttn"))
            self.assertEqual(bad_proc.returncode, 1, bad_proc.stderr)
            self.assertIn("unknown-class", [d["code"] for d in bad_diagnostics])
            self.assertTrue(any(d.get("suggestions") for d in bad_diagnostics))

    def test_first_use_guide_is_discoverable_and_version_accurate(self):
        self.assertIn("docs/getting-started.md", FILES)
        guide = (ROOT / "docs/getting-started.md").read_text(encoding="utf-8")
        self.assertIn("0.3.0-alpha.4", guide)
        self.assertIn("0.3.0-alpha.5", guide)
        self.assertIn("syntyr.core.css", guide)
        self.assertIn("syn-root", guide)
        self.assertIn("scripts/syntyr_check.py", guide)
        self.assertIn("not yet published to npm", guide.lower())
        example = guide.split("```html\n", 1)[1].split("\n```", 1)[0]
        released_css = (ROOT / "site-releases/0.3.0-alpha.4/syntyr.core.css").read_text()
        classes = [c for attr in re.findall(r'class="([^"]+)"', example) for c in attr.split()]
        for cls in classes:
            with self.subTest(cls=cls):
                self.assertTrue(css_has_class(released_css, cls), f"{cls} is not shipped in alpha.4")
        self.assertIn("docs/getting-started.md", (ROOT / "README.md").read_text())
        self.assertIn('href="getting-started.html"', (ROOT / "docs/guides.html").read_text())

        site = source_files()
        self.assertIn("docs/getting-started.md", site)
        self.assertIn("docs/getting-started.html", site)


if __name__ == "__main__":
    unittest.main()
