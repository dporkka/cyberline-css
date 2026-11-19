"""Augmented geometry extensions must remain opt-in, stable and discoverable."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GeometryMixerContract(unittest.TestCase):
    def test_independent_corners_and_shape_following_inner_border(self):
        css = (ROOT / "src/geometry.css").read_text()
        for corner in ("tl", "tr", "br", "bl"):
            self.assertIn(f"--syn-frame-cut-{corner}", css)
        self.assertIn("--_syn-inner-shape", css)
        self.assertIn("clip-path: var(--_syn-inner-shape)", css)
        self.assertIn("--syn-frame-border-paint", css)
        self.assertIn("0.585786", css, "diagonal inset needs a stroke correction")
        self.assertIn("forced-colors: active", css)
        for shape in ("bevel", "notch", "step", "facet"):
            self.assertIn(f".syn-frame--{shape}", css)

    def test_playground_has_no_runtime_library_dependency(self):
        html = (ROOT / "docs/playground.html").read_text()
        script = (ROOT / "docs/playground.js").read_text()
        for identifier in ("geometry-shape", "geometry-cut-tl", "geometry-cut-tr",
                           "geometry-cut-br", "geometry-cut-bl",
                           "geometry-stroke", "geometry-border-paint",
                           "geometry-preview", "geometry-copy"):
            self.assertIn(f'id="{identifier}"', html)
        self.assertIn("geometry-shape", script)
        self.assertIn("geometry-copy", script)
        self.assertIn("textContent", script)
        self.assertIn("playground-preview", html)
        for path in (ROOT / "src/geometry.css", ROOT / "dist/syntyr.geometry.css"):
            self.assertNotIn("<script", path.read_text())

    def test_static_gallery_demonstrates_new_profiles_without_javascript(self):
        example = (ROOT / "examples/geometry-terminal.html").read_text()
        self.assertIn("syn-frame--step", example)
        self.assertIn("syn-frame--facet", example)
        self.assertIn("--syn-frame-border-paint", example)
        self.assertIn("--syn-frame-inlay-paint", example)
        self.assertNotIn("<script", example)

    def test_api_and_documentation_cover_new_shapes_and_tokens(self):
        api = json.loads((ROOT / "metadata/syntyr-api.json").read_text())
        classes = {entry["name"] for entry in api["classes"]}
        tokens = {entry["name"] for entry in api["tokens"]}
        for shape in ("step", "facet"):
            self.assertIn(f"syn-frame--{shape}", classes)
        self.assertIn("--syn-frame-border-paint", tokens)
        for corner in ("tl", "tr", "br", "bl"):
            self.assertIn(f"--syn-frame-cut-{corner}", tokens)
        guide = (ROOT / "docs/geometry-terminal.md").read_text()
        self.assertIn("Per-corner", guide)
        self.assertIn("gradient", guide)
        self.assertIn("geometry editor", guide.lower())


if __name__ == "__main__":
    unittest.main()
