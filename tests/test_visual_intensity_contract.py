"""Optional cyberpunk intensity and geometry composition contracts."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class VisualIntensityContract(unittest.TestCase):
    def test_intensity_is_scoped_and_independent_of_theme(self):
        tokens = (ROOT / "src/tokens.css").read_text()
        for intensity in ("quiet", "standard", "cinematic"):
            self.assertIn(f'data-syn-intensity="{intensity}"', tokens)
        self.assertIn('.syn-root [data-syn-intensity="quiet"]', tokens)
        self.assertIn('.syn-root [data-syn-intensity="cinematic"]', tokens)
        for token in ("--syn-grid-alpha:", "--syn-glow-alpha:", "--syn-wash-alpha:",
                      "--syn-horizon-alpha:", "--syn-scanline-alpha:"):
            self.assertIn(token, tokens)
        self.assertNotIn("data-syn-theme=\"grid\"][data-syn-intensity", tokens)

    def test_effects_read_intensity_tokens_without_js(self):
        effects = (ROOT / "src/effects.css").read_text()
        for token in ("--syn-grid-alpha", "--syn-glow-alpha", "--syn-wash-alpha",
                      "--syn-horizon-alpha", "--syn-scanline-alpha"):
            self.assertIn(f"var({token}", effects)
        self.assertIn("forced-colors: active", effects)
        self.assertNotIn("@keyframes", effects)
        self.assertNotIn("data-syn-intensity", (ROOT / "dist/syntyr.semantic.css").read_text())

    def test_frames_reset_prior_pseudo_element_dimensions_and_clips(self):
        geometry = (ROOT / "src/geometry.css").read_text()
        common = geometry.split(".syn-frame::before,", 1)[1].split("}", 1)[0]
        for prop in ("width: auto", "height: auto", "clip-path: none", "inset: 0"):
            self.assertIn(prop, common)
        self.assertIn(".syn-frame--accent", geometry)
        self.assertIn("forced-colors: active", geometry)

    def test_documentation_editor_and_examples_show_both_modes(self):
        ops = (ROOT / "examples/operations-console.html").read_text()
        landing = (ROOT / "examples/landing.html").read_text()
        editor = (ROOT / "docs/theme-editor.html").read_text()
        docs = (ROOT / "docs/visual-intensity.md").read_text()
        self.assertIn('data-syn-intensity="quiet"', ops)
        self.assertIn('data-syn-intensity="cinematic"', landing)
        self.assertIn('id="intensity"', editor)
        for name in ("quiet", "standard", "cinematic"):
            self.assertIn(name, docs)
        self.assertIn("visual-intensity.md", (ROOT / "README.md").read_text())
        self.assertNotIn("<script", ops.lower())
        self.assertNotIn("<script", landing.lower())

    def test_editor_metadata_exposes_intensity_attribute_and_values(self):
        import json
        payload = json.loads((ROOT / "metadata/syntyr.html-custom-data.json").read_text())
        attrs = {a["name"]: a for a in payload["globalAttributes"]}
        self.assertIn("data-syn-intensity", attrs)
        values = {entry["name"] for entry in attrs["data-syn-intensity"]["values"]}
        self.assertEqual(values, {"quiet", "standard", "cinematic"})

    def test_candidate_documentation_and_gallery_are_publishable(self):
        from scripts.build_cloudflare_site import source_files
        from scripts.package_release import FILES
        published = source_files()
        self.assertIn("docs/visual-intensity.md", published)
        self.assertIn("examples/intensity-geometry.html", published)
        self.assertIn("docs/visual-intensity.md", FILES)
        self.assertIn("docs/visual-intensity.md", (ROOT / "scripts/build_agent_docs.py").read_text())
        self.assertIn("intensity-geometry.html", (ROOT / "docs/index.html").read_text())


if __name__ == "__main__":
    unittest.main()
