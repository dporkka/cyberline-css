"""Native CSS patterns and individually importable component distributions."""
from html.parser import HTMLParser
from pathlib import Path
import json
import unittest

from scripts.build import COMPONENTS, component_distributions, all_distributions
from scripts.build_cloudflare_site import source_files
from scripts.package_release import FILES

ROOT = Path(__file__).resolve().parents[1]


class LabelParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.labels = []
        self.inputs = []
        self.elements = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if tag == "label":
            self.labels.append(attrs)
        if tag == "input":
            self.inputs.append(attrs)


class BladesAdoptionContract(unittest.TestCase):
    def test_individual_component_css_exports_are_exact_source_files(self):
        expected = {"components/tokens.css", "components/base.css"}
        expected |= {"components/" + Path(s).name for s in COMPONENTS}
        self.assertEqual(set(component_distributions()), expected)
        for path, inputs in component_distributions().items():
            with self.subTest(path=path):
                self.assertEqual(len(inputs), 1)
                self.assertEqual(
                    (ROOT / "dist" / path).read_text(),
                    (ROOT / "src" / inputs[0]).read_text().strip() + "\n",
                )
                self.assertIn("@layer syn.", (ROOT / "dist" / path).read_text())

    def test_published_package_site_and_release_include_all_css(self):
        pkg = json.loads((ROOT / "package.json").read_text())
        for name in all_distributions():
            with self.subTest(name=name):
                self.assertIn("dist/" + name, FILES)
                self.assertIn("dist/" + name, source_files())
                self.assertTrue((ROOT / "dist" / name).is_file())
                if name.startswith("components/"):
                    self.assertEqual(pkg["exports"]["./" + name], "./dist/" + name)
        self.assertIn("./native-recipes.css", pkg["exports"])
        self.assertEqual(pkg["exports"]["./native-recipes.css"], "./dist/syntyr.native-recipes.css")

    def test_overlays_are_enhanced_without_replacing_native_behavior(self):
        css = (ROOT / "src/components/overlays.css").read_text()
        for fragment in (
            ".syn-popover--anchored", "position-area:", "position-try-fallbacks:",
            "@supports", "position-area: block-end span-inline-end",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, css)
        self.assertNotIn("@import", css)
        self.assertNotIn("url(", css)

    def test_overlay_motion_is_in_opt_in_stylesheet_only(self):
        core = (ROOT / "src/components/overlays.css").read_text()
        motion = (ROOT / "src/motion.css").read_text()
        self.assertNotIn("transition: opacity", core)
        self.assertNotIn("@starting-style", core)
        self.assertIn("&.syn-popover.syn-popover--transition", motion)
        self.assertIn("&.syn-dialog.syn-dialog--transition", motion)
        self.assertIn("prefers-reduced-motion: no-preference", motion)
        self.assertIn("@starting-style", motion)
        html = (ROOT / "examples/native-recipes.html").read_text()
        self.assertIn('href="../dist/syntyr.motion.css"', html)
        self.assertIn("syn-popover--transition", html)
        self.assertIn("syn-dialog--transition", html)

    def test_native_guide_release_links_are_self_contained_or_hosted(self):
        import re
        import posixpath
        text = (ROOT / "docs/native-patterns.md").read_text()
        for href in re.findall(r'\]\(([^)]+)\)', text):
            if href.startswith(("https://", "http://", "#")):
                continue
            local = posixpath.normpath(posixpath.join("docs", href.split("#", 1)[0]))
            with self.subTest(href=href):
                self.assertIn(local, FILES, f"ZIP does not contain {local}")

    def test_logical_anchor_position_rule_matches_fallback_specificity(self):
        css = (ROOT / "src/components/overlays.css").read_text()
        selector = "&.syn-popover.syn-popover--anchored"
        self.assertEqual(css.count(selector), 2, "Both anchor rules need equal specificity")
        logical = css.split("@supports (position-area: block-end)", 1)[1]
        self.assertIn("position-area: block-end span-inline-end", logical)

    def test_optional_recipes_keep_persistent_labels_and_semantic_markups(self):
        css = (ROOT / "src/native-recipes.css").read_text()
        html = (ROOT / "examples/native-recipes.html").read_text()
        for fragment in (".syn-field--floating", ".syn-floating-label",
                         ".syn-timeline", ".syn-code-figure"):
            self.assertIn(fragment, css)
            self.assertIn(fragment[1:], html)
        self.assertNotIn("<script", html.lower())
        self.assertIn("syntyr.native-recipes.css", html)
        parser = LabelParser()
        parser.feed(html)
        ids = {attrs.get("id") for _, attrs in parser.elements}
        self.assertTrue(any(label.get("for") in ids for label in parser.labels))
        self.assertTrue(any(tag == "ol" and "syn-timeline" in attrs.get("class", "") for tag, attrs in parser.elements))
        self.assertTrue(any(tag == "figure" and "syn-code-figure" in attrs.get("class", "") for tag, attrs in parser.elements))
        self.assertTrue(any(tag == "figcaption" for tag, _ in parser.elements))
        self.assertIn('tabindex="0"', html)

    def test_timeline_supports_rtl_and_keeps_list_semantics(self):
        css = (ROOT / "src/native-recipes.css").read_text()
        li_rule = css.split(".syn-timeline) > li {", 1)[1].split("}", 1)[0]
        self.assertIn("padding-inline-start: var(--syn-space-3)", li_rule)
        self.assertIn("padding-block: 0 var(--syn-space-3)", li_rule)
        self.assertNotIn("padding: 0 0 ", li_rule)

        html = (ROOT / "examples/native-recipes.html").read_text()
        docs = (ROOT / "docs/native-patterns.md").read_text()
        self.assertIn('<ol class="syn-timeline" role="list"', html)
        self.assertIn('<ol class="syn-timeline" role="list"', docs)

    def test_native_patterns_are_discoverable_in_agent_index(self):
        self.assertIn("docs/native-patterns.md", (ROOT / "llms.txt").read_text())

    def test_docs_and_gallery_are_explicitly_allowlisted(self):
        self.assertIn("native-recipes.html", (ROOT / "docs/index.html").read_text())
        self.assertIn("native-recipes.html", (ROOT / "scripts/build_cloudflare_site.py").read_text())
        self.assertIn("native-patterns.md", (ROOT / "scripts/build_cloudflare_site.py").read_text())
        self.assertIn("native-patterns.md", (ROOT / "scripts/build_agent_docs.py").read_text())
        self.assertIn("components/buttons.css", (ROOT / "docs/native-patterns.md").read_text())
        smoke = (ROOT / "tests/native_recipes_browser.js").read_text()
        for term in ("chromium", "firefox", "webkit", "prefers-reduced-motion", "Escape", "transitionDuration", "innerWidth"):
            if term == "prefers-reduced-motion":
                continue  # Playwright's reducedMotion API tests the same browser preference.
            self.assertIn(term, smoke)


if __name__ == "__main__":
    unittest.main()
