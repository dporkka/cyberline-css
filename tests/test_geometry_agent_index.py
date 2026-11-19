"""Keep opt-in geometry discoverable in machine-readable agent documentation."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class GeometryAgentIndexTests(unittest.TestCase):
    def test_llms_index_links_geometry_guide_and_mixer(self):
        index = (ROOT / "llms.txt").read_text()
        self.assertIn("https://syntyr-css.pages.dev/docs/geometry-terminal.md", index)
        self.assertIn("https://syntyr-css.pages.dev/docs/playground.html#geometry-title", index)
        self.assertIn("alpha.5", index, "avoid implying this API is in the published alpha.4")

    def test_full_llm_reference_includes_geometry_guide(self):
        from scripts.build_agent_docs import SOURCES
        self.assertIn("docs/geometry-terminal.md", SOURCES)
        combined = (ROOT / "llms-full.txt").read_text()
        self.assertIn("## Source: docs/geometry-terminal.md", combined)
        self.assertIn("--syn-frame-border-paint", combined)
        self.assertIn("--syn-frame-cut-tl", combined)


if __name__ == "__main__":
    unittest.main()
