"""Documentation navigation, publication, and version boundaries stay aligned."""
from pathlib import Path
import unittest

from scripts.build_cloudflare_site import source_files

ROOT = Path(__file__).resolve().parents[1]


class DocumentationEntryPointsTests(unittest.TestCase):
    def test_new_guides_are_published_and_linked(self):
        published = source_files()
        for slug in ("getting-started", "troubleshooting"):
            with self.subTest(slug=slug):
                self.assertIn(f"docs/{slug}.md", published)
                self.assertIn(f"docs/{slug}.html", published)
                self.assertIn(f"{slug}.html", (ROOT / "docs/guides.html").read_text())
                self.assertIn(f"docs/{slug}.md", (ROOT / "llms.txt").read_text())

    def test_published_release_is_not_confused_with_source_candidate(self):
        readme = (ROOT / "README.md").read_text()
        first_steps = (ROOT / "docs/getting-started.md").read_text()
        for content in (readme, first_steps):
            self.assertIn("v0.3.0-alpha.4", content)
            self.assertIn("unreleased", content.lower())
            self.assertIn("syntyr.semantic-bundle.css", content)
        self.assertIn("unreleased", readme.lower())
        self.assertIn("published alpha.4", first_steps.lower())


if __name__ == "__main__":
    unittest.main()
