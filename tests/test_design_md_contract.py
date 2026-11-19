"""Tests for Syntyr's source-backed, agent-readable DESIGN.md contract."""
from pathlib import Path
import importlib.util
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "DESIGN.md"
TOKENS = ROOT / "src/tokens.css"
SCRIPT = ROOT / "scripts/sync_design_md.py"


class DesignMarkdownContract(unittest.TestCase):
    def test_document_follows_stitch_interoperable_frontmatter(self):
        content = DESIGN.read_text(encoding="utf-8")
        self.assertTrue(content.startswith("---\n"))
        sections = content.split("---\n", 2)
        self.assertEqual(len(sections), 3)
        frontmatter = sections[1]
        for key in ("version: alpha", "name: Syntyr Studio", "colors:", "typography:", "spacing:", "rounded:", "components:"):
            self.assertIn(key, frontmatter)
        self.assertIn('primary: "#2458c6"', frontmatter)
        self.assertIn('textColor: "{colors.on-primary}"', frontmatter)
        self.assertNotIn("borderColor:", frontmatter, "Google DESIGN.md component schema has no borderColor key")

    def test_design_tokens_never_drift_from_css(self):
        proc = subprocess.run(
            [sys.executable, str(SCRIPT), "--check"],
            cwd=ROOT, capture_output=True, text=True
        )
        self.assertEqual(proc.returncode, 0, proc.stdout + proc.stderr)

    def test_generator_tracks_css_changes_without_hand_edited_duplicates(self):
        spec = importlib.util.spec_from_file_location("sync_design_md", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        css = TOKENS.read_text(encoding="utf-8")
        original = module.build_frontmatter(css)
        modified = module.build_frontmatter(css.replace("--syn-accent: #2458c6;", "--syn-accent: #3458c6;", 1))
        self.assertIn('primary: "#2458c6"', original)
        self.assertIn('primary: "#3458c6"', modified)
        self.assertNotEqual(original, modified)

    def test_body_type_role_tracks_override_without_changing_type_base(self):
        spec = importlib.util.spec_from_file_location("sync_design_md", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        css = TOKENS.read_text(encoding="utf-8")
        original = module.build_frontmatter(css)
        changed = module.build_frontmatter(
            css.replace("--syn-type-body: var(--syn-type-base);",
                        "--syn-type-body: 1.125rem;", 1)
        )
        self.assertIn('fontSize: "1rem"', original)
        self.assertIn('fontSize: "1.125rem"', changed)
        self.assertNotEqual(original, changed)

    def test_markdown_contract_table_uses_literal_attribute_pipes(self):
        doc = DESIGN.read_text(encoding="utf-8")
        import re
        for row in doc.splitlines():
            if row.startswith("| Density |") or row.startswith("| Visual intensity |"):
                self.assertEqual(len(re.split(r"(?<!\\)\|", row)), 5, row)

    def test_public_discovery_and_release_allowlists(self):
        self.assertIn("[Canonical DESIGN.md contract](DESIGN.md)", (ROOT / "README.md").read_text())
        self.assertIn("https://syntyr-css.pages.dev/DESIGN.md", (ROOT / "llms.txt").read_text())
        site_script = (ROOT / "scripts/build_cloudflare_site.py").read_text()
        package_script = (ROOT / "scripts/package_release.py").read_text()
        self.assertIn('ROOT / "DESIGN.md"', site_script)
        self.assertRegex(site_script, r"/DESIGN\.md\s+X-Robots-Tag: noindex")
        self.assertIn('"DESIGN.md",', package_script)
        self.assertIn('"scripts/sync_design_md.py"', package_script)

    def test_design_contract_covers_nonvisual_constraints(self):
        doc = DESIGN.read_text(encoding="utf-8")
        for guidance in (
            "Zero-JavaScript baseline", "Token source of truth",
            "Accessibility", "AI-agent implementation rules",
            "data-syn-theme", "data-syn-density", "data-syn-intensity",
            "prefers-reduced-motion", "forced-colors", "syn-semantic",
            "Do not copy", "Component and state contract",
        ):
            self.assertIn(guidance, doc)


if __name__ == "__main__":
    unittest.main()
