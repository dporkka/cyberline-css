"""Version-aware, read-only tool contracts for the optional agent adapter."""
import unittest

from agent_mcp.catalog import CatalogError, SyntyrCatalog

catalog = SyntyrCatalog()


class AgentMcpCatalogTests(unittest.TestCase):
    def test_default_is_immutable_published_version(self):
        data = catalog.search_components("button")
        self.assertEqual(data["release"], "0.3.0-alpha.4")
        self.assertEqual(data["release_status"], "published")
        self.assertTrue(any(x["name"] == "Button" for x in data["components"]))

    def test_candidate_only_composition_fails_closed_on_published_release(self):
        with self.assertRaisesRegex(CatalogError, "unavailable"):
            catalog.get_component("Form compositions", "0.3.0-alpha.4")
        result = catalog.get_component("Form compositions", "0.3.0-alpha.5")
        self.assertEqual(result["release_status"], "unreleased_candidate")
        self.assertIn("syn-field", result["component"]["classes"])

    def test_unknown_release_and_selector_are_not_silently_accepted(self):
        with self.assertRaisesRegex(CatalogError, "Unsupported release"):
            catalog.search_components("form", "latest")
        with self.assertRaisesRegex(CatalogError, "Unknown"):
            catalog.lookup_api("syn-nonexistent", "0.3.0-alpha.4")
        with self.assertRaisesRegex(CatalogError, "Unknown"):
            catalog.lookup_api("--syn-definitely-not-a-token", "0.3.0-alpha.5")

    def test_lookup_published_css_uses_actual_release_artifact(self):
        api = catalog.lookup_api("syn-button--primary", "0.3.0-alpha.4")
        self.assertEqual(api["entry"]["stylesheet"], "syntyr.core.css")
        self.assertEqual(api["entry"]["kind"], "class")
        self.assertEqual(api["release_status"], "published")

    def test_validation_rejects_candidate_class_on_published_version(self):
        result = catalog.validate_markup('<main class="syn-root"><div class="syn-field"></div></main>',
                                         "0.3.0-alpha.4", ["syntyr.core.css"])
        self.assertEqual(result["unknown_classes"], ["syn-field"])
        self.assertEqual(result["missing_stylesheets"], [])
        self.assertEqual(result["release_status"], "published")

    def test_validation_reports_modules_required_but_not_loaded(self):
        result = catalog.validate_markup('<section class="syn-root syn-app-shell"></section>',
                                         "0.3.0-alpha.4", ["syntyr.core.css"])
        self.assertEqual(result["unknown_classes"], [])
        self.assertIn("syntyr.recipes.css", result["missing_stylesheets"])
        complete = catalog.validate_markup('<section class="syn-root syn-app-shell"></section>',
                                           "0.3.0-alpha.4", ["syntyr.core.css", "syntyr.recipes.css"])
        self.assertEqual(complete["missing_stylesheets"], [])

    def test_validation_bounds_input_and_treats_custom_classes_as_host_owned(self):
        result = catalog.validate_markup('<div class="custom syn-panel"></div>',
                                         "0.3.0-alpha.4", ["syntyr.core.css"])
        self.assertEqual(result["unknown_classes"], [])
        with self.assertRaisesRegex(CatalogError, "too long"):
            catalog.validate_markup("<p>" + "x" * 25000 + "</p>")

    def test_tokens_are_names_not_promised_runtime_values(self):
        result = catalog.get_theme_tokens("accent", "0.3.0-alpha.4")
        self.assertIn("grid", result["themes"])
        self.assertTrue(all(t["name"].startswith("--syn-") for t in result["tokens"]))
        self.assertTrue(all("value" not in t for t in result["tokens"]))
        self.assertNotIn("industrial", result["themes"])

    def test_mcp_source_is_not_exposed_in_static_site_or_css_npm_package(self):
        from scripts.build_cloudflare_site import source_files
        from scripts.package_release import FILES
        import json
        from pathlib import Path
        root = Path(__file__).resolve().parents[1]
        package = json.loads((root / "package.json").read_text())
        self.assertNotIn("agent_mcp/", " ".join(package.get("files", [])))
        self.assertNotIn("agent_mcp/server.py", source_files())
        self.assertNotIn("agent_mcp/server.py", FILES)

    def test_unknown_components_are_not_invented(self):
        result = catalog.search_components("fictionalxyz", "0.3.0-alpha.4")
        self.assertEqual(result["components"], [])
        with self.assertRaisesRegex(CatalogError, "Unknown"):
            catalog.get_component("fictionalxyz", "0.3.0-alpha.4")


if __name__ == "__main__":
    unittest.main()
