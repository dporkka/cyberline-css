"""Ensure Go, Rails and Laravel project-search examples share Syntyr UI contracts."""
from pathlib import Path
import unittest
from scripts.build_cloudflare_site import PUBLIC_DOCS

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


class BackendComparisonTests(unittest.TestCase):
    def test_same_examples_expose_matching_controls_and_demo_records(self):
        markup = {
            "Go": EXAMPLES / "go-stdlib-projects/templates/index.gohtml",
            "Rails": EXAMPLES / "rails-hotwire/app/views/syntyr_projects/index.html.erb",
            "Laravel": EXAMPLES / "laravel-blade/resources/views/syntyr/projects.blade.php",
        }
        records = {
            "Go": EXAMPLES / "go-stdlib-projects/main.go",
            "Rails": EXAMPLES / "rails-hotwire/app/controllers/syntyr_projects_controller.rb",
            "Laravel": EXAMPLES / "laravel-blade/routes/syntyr-projects.php",
        }
        for framework, path in markup.items():
            with self.subTest(framework=framework):
                source = path.read_text()
                for contract in (
                    'name="q"', 'method="get"', 'type="search"', 'class="syn-panel"',
                    'class="syn-input"', 'class="syn-table"', 'scope="col"',
                    'aria-live="polite"', 'data-syn-theme="studio"',
                    'No matching projects', 'Projects matching your search',
                ):
                    self.assertIn(contract, source)
                self.assertNotIn('<script', source.lower())
                data = records[framework].read_text()
                for project in ('Station expansion', 'Airport displays', 'Downtown refresh'):
                    self.assertIn(project, data)

    def test_comparison_page_is_public_and_links_to_all_three_recipes(self):
        guide = ROOT / "docs/backend-integration-comparison.md"
        doc = guide.read_text()
        self.assertIn("backend-integration-comparison.md", PUBLIC_DOCS)
        for path in ("go-stdlib-projects/README.md", "rails-hotwire/README.md",
                     "laravel-blade/README.md"):
            self.assertIn(path, doc)
        self.assertIn("Zero required Syntyr JavaScript", doc)
        self.assertIn("Go", doc)
        self.assertIn("Rails", doc)
        self.assertIn("Laravel", doc)
        index = (ROOT / "docs/framework-integrations.md").read_text()
        self.assertIn("backend-integration-comparison.md", index)


if __name__ == "__main__":
    unittest.main()
