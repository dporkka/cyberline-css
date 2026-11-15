"""Contracts for dependency-free Go, Rails ERB/Turbo and Laravel Blade recipes."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples"


class ServerTemplateRecipesTest(unittest.TestCase):
    def test_rails_recipe_is_safe_progressive_get_search(self):
        controller = (EXAMPLES / "rails-hotwire/app/controllers/syntyr_projects_controller.rb").read_text()
        view = (EXAMPLES / "rails-hotwire/app/views/syntyr_projects/index.html.erb").read_text()
        guide = (EXAMPLES / "rails-hotwire/README.md").read_text()
        for fragment in ("class SyntyrProjectsController", "def index", "params[:q]", "PROJECTS", "include?"):
            self.assertIn(fragment, controller)
        for fragment in ('method="get"', 'data-turbo-frame="syntyr-project-results"',
                         '<turbo-frame id="syntyr-project-results">', 'class="syn-root"',
                         'class="syn-input"', 'class="syn-button', 'scope="col"',
                         'aria-live="polite"', '<%= h(@query) %>', '<%= h(project[:name]) %>'):
            self.assertIn(fragment, view)
        self.assertNotIn("<script", view.lower())
        self.assertNotIn("html_safe", controller + view)
        self.assertIn('get "/syntyr/projects"', guide)
        self.assertIn("syntyr.core.css", guide)
        self.assertIn("app/views/syntyr_projects/index.html.erb", guide)
        self.assertIn("bin/rails test", guide)
        self.assertIn("assert_response :success", (EXAMPLES / "rails-hotwire/test/controllers/syntyr_projects_controller_test.rb").read_text())

    def test_laravel_recipe_uses_escaped_blade_with_native_get(self):
        route = (EXAMPLES / "laravel-blade/routes/syntyr-projects.php").read_text()
        view = (EXAMPLES / "laravel-blade/resources/views/syntyr/projects.blade.php").read_text()
        guide = (EXAMPLES / "laravel-blade/README.md").read_text()
        for fragment in ("Route::get(", "Request $request", "is_string($raw)", "trim($raw)", "->filter("):
            self.assertIn(fragment, route)
        for fragment in ('method="get"', "route('syntyr.projects')",
                         "asset('css/syntyr.core.css')", 'class="syn-root',
                         'class="syn-input"', 'class="syn-button', 'scope="col"',
                         'aria-live="polite"', '{{ $query }}', '{{ $project[\'name\'] }}'):
            self.assertIn(fragment, view)
        self.assertNotIn("{!!", view)
        self.assertNotIn("<script", view.lower())
        self.assertIn("routes/web.php", guide)
        self.assertIn("public/css/syntyr.core.css", guide)
        self.assertIn("resources/views/syntyr/projects.blade.php", guide)
        self.assertIn("php artisan test", guide)
        self.assertIn("assertDontSee", (EXAMPLES / "laravel-blade/tests/Feature/SyntyrProjectsTest.php").read_text())

    def test_go_template_remains_same_framework_neutral_contract(self):
        go = (EXAMPLES / "server-rendered/search.templ").read_text()
        self.assertIn('class="syn-root"', go)
        self.assertIn('name="q"', go)
        self.assertIn('value={ query }', go)
        self.assertIn('method="get"', go)
        self.assertNotIn("<script", go.lower())

    def test_recipe_index_is_in_framework_docs(self):
        guide = (ROOT / "docs/framework-integrations.md").read_text()
        for fragment in ("examples/rails-hotwire/README.md", "examples/laravel-blade/README.md",
                         "examples/server-rendered/search.templ", "zero-JavaScript", "public/css/syntyr.core.css"):
            self.assertIn(fragment, guide)
        self.assertIn("Rails", (ROOT / "README.md").read_text())
        self.assertIn("Laravel", (ROOT / "README.md").read_text())


if __name__ == "__main__":
    unittest.main()
