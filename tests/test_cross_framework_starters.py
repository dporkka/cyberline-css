"""Cross-framework adoption contracts: usable templates, scoped CSS, no framework runtime in Syntyr."""
from pathlib import Path
import json
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CrossFrameworkStarterTests(unittest.TestCase):
    def test_vue3_starter_is_buildable_and_preserves_native_form_semantics(self):
        base = ROOT / "examples/vue"
        package = json.loads((base / "package.json").read_text())
        self.assertEqual(package["dependencies"]["@syntyr/css"], "file:../..")
        self.assertIn("vue", package["dependencies"])
        self.assertIn("@vitejs/plugin-vue", package["devDependencies"])
        self.assertIn("build", package["scripts"])
        self.assertIn("@syntyr/css/core.css", (base / "src/main.js").read_text())
        component = (base / "src/App.vue").read_text()
        for expected in ("syn-root", "syn-panel", "syn-input", "syn-button",
                         "v-model", "@submit.prevent", ":aria-invalid", ":disabled",
                         "aria-live", 'data-syn-theme="studio"'):
            self.assertIn(expected, component)
        self.assertIn('for="campaign-name"', component)
        self.assertIn('id="campaign-name"', component)
        self.assertTrue((base / "package-lock.json").is_file())
        self.assertTrue((base / "README.md").is_file())

    def test_svelte5_starter_is_buildable_and_binds_native_state(self):
        base = ROOT / "examples/svelte"
        package = json.loads((base / "package.json").read_text())
        self.assertEqual(package["dependencies"]["@syntyr/css"], "file:../..")
        self.assertIn("svelte", package["dependencies"])
        self.assertIn("@sveltejs/vite-plugin-svelte", package["devDependencies"])
        self.assertIn("build", package["scripts"])
        self.assertIn("@syntyr/css/core.css", (base / "src/main.js").read_text())
        component = (base / "src/App.svelte").read_text()
        for expected in ("syn-root", "syn-panel", "syn-input", "syn-button",
                         "bind:value", "onsubmit=", "aria-invalid=", "disabled=",
                         "aria-live", 'data-syn-theme="studio"'):
            self.assertIn(expected, component)
        self.assertIn('for="campaign-name"', component)
        self.assertIn('id="campaign-name"', component)
        self.assertTrue((base / "package-lock.json").is_file())
        self.assertTrue((base / "README.md").is_file())

    def test_spring_thymeleaf_example_uses_escaped_values_and_get_search(self):
        base = ROOT / "examples/server-rendered"
        template = (base / "spring-thymeleaf.html").read_text()
        controller = (base / "CampaignSearchController.java").read_text()
        for expected in ("syn-root", "syn-panel", "syn-input",
                         "th:action", "th:value", "th:text", "th:each",
                         'method="get"', "syntyr.core.css"):
            self.assertIn(expected, template)
        self.assertIn("@Controller", controller)
        self.assertIn("@GetMapping", controller)
        self.assertIn("model.addAttribute", controller)
        self.assertNotIn("th:utext", template)

    def test_aspnet_razor_pages_example_escapes_output_and_binds_get_query(self):
        base = ROOT / "examples/server-rendered/dotnet/Pages"
        view = (base / "Campaigns.cshtml").read_text()
        model = (base / "Campaigns.cshtml.cs").read_text()
        for expected in ("@page", "@model", "syn-root", "syn-panel", "syn-input",
                         'method="get"', "asp-append-version", "syntyr.core.css",
                         "@Model.Query", "@foreach"):
            self.assertIn(expected, view)
        self.assertIn("PageModel", model)
        self.assertIn("[BindProperty(SupportsGet = true)]", model)
        self.assertIn("OnGet", model)
        self.assertNotIn("Html.Raw(", view)

    def test_documentation_explains_framework_specific_boundaries_without_new_core_dependencies(self):
        guide = (ROOT / "docs/framework-integrations.md").read_text()
        for expected in ("## Vue 3", "## Svelte 5", "## Java / Spring MVC",
                         "## C# / ASP.NET Core Razor", "examples/vue",
                         "examples/svelte", "spring-thymeleaf.html",
                         "Campaigns.cshtml"):
            self.assertIn(expected, guide)
        manifest = json.loads((ROOT / "package.json").read_text())
        for category in ("dependencies", "devDependencies", "peerDependencies", "optionalDependencies"):
            self.assertNotIn(category, manifest)


if __name__ == "__main__":
    unittest.main()
