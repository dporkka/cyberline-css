"""Opt-in human/agent collaboration UI contract."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
CLASSES = (
    "syn-conversation", "syn-conversation__stream", "syn-message",
    "syn-message__avatar", "syn-message__meta", "syn-message__body",
    "syn-message__actions", "syn-identity", "syn-presence",
    "syn-attachment", "syn-composer", "syn-composer__toolbar",
    "syn-collab-layout", "syn-thread-panel", "syn-agent-run",
)


class DemoParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.classes = set()
        self.themes = set()
        self.scripts = 0
        self.textareas = []
        self.labels = []
        self.open_labels = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self.classes.update(a.get("class", "").split())
        if "data-syn-theme" in a:
            self.themes.add(a["data-syn-theme"])
        if tag == "script":
            self.scripts += 1
        if tag == "label":
            label = {"for": a.get("for"), "id": a.get("id"), "text": []}
            self.labels.append(label)
            self.open_labels.append(label)
        if tag == "textarea":
            a["_wrapping_label"] = self.open_labels[-1] if self.open_labels else None
            self.textareas.append(a)

    def handle_data(self, data):
        for label in self.open_labels:
            label["text"].append(data)

    def handle_endtag(self, tag):
        if tag == "label" and self.open_labels:
            self.open_labels.pop()

    def textarea_has_name(self, textarea):
        if (textarea.get("aria-label") or "").strip():
            return True
        references = set((textarea.get("aria-labelledby") or "").split())
        field_id = textarea.get("id")
        for label in self.labels:
            linked = (
                (field_id and label["for"] == field_id)
                or (label is textarea.get("_wrapping_label"))
                or (label["id"] and label["id"] in references)
            )
            if linked and "".join(label["text"]).strip():
                return True
        return False


class CollaborationRecipes(unittest.TestCase):
    def test_optional_module_is_built_but_excluded_from_core(self):
        from scripts.build import all_distributions
        self.assertIn("syntyr.collaboration.css", all_distributions())
        source = (ROOT / "src/collaboration.css").read_text(encoding="utf-8")
        compiled = (ROOT / "dist/syntyr.collaboration.css").read_text(encoding="utf-8")
        self.assertEqual(source.strip(), compiled.strip())
        for name in CLASSES:
            with self.subTest(name=name):
                self.assertIn("." + name, compiled)
                self.assertNotIn("." + name, (ROOT / "dist/syntyr.core.css").read_text())
        self.assertIn(".syn-conversation", (ROOT / "dist/syntyr.all.css").read_text())

    def test_module_is_scoped_and_themeable_with_no_js(self):
        source = (ROOT / "src/collaboration.css").read_text()
        self.assertIn("@layer syn.recipes", source)
        self.assertIn(":where(.syn-root, .syn-root *)", source)
        for token in ("--syn-surface", "--syn-border-subtle", "--syn-text",
                      "--syn-muted", "--syn-accent", "--syn-focus-ring"):
            self.assertIn("var(" + token, source)
        self.assertIn(":focus-visible", source)
        identity_rule = source.split("&.syn-identity {", 1)[1].split("}", 1)[0]
        self.assertIn("overflow-wrap: anywhere", identity_rule,
                      "unbroken author names must wrap within the message")
        self.assertIn("--syn-collab-avatar: min(2rem, 36px)", source)
        self.assertIn("forced-colors: active", source)
        self.assertIn("prefers-reduced-motion: reduce", source)
        self.assertIn("@media (max-width:", source)
        self.assertNotIn("@import", source)
        self.assertNotRegex(source.lower(), r"@keyframes\s+(blink|pulse|thinking)")
        self.assertNotIn("javascript:", source.lower())

    def test_static_three_theme_example_is_accessible_and_server_ready(self):
        demo = (ROOT / "examples/collaboration.html").read_text(encoding="utf-8")
        parser = DemoParser()
        parser.feed(demo)
        self.assertTrue({"minimal", "grid", "noir"} <= parser.themes)
        self.assertEqual(parser.scripts, 0)
        for name in CLASSES:
            with self.subTest(name=name):
                self.assertIn(name, parser.classes)
        self.assertIn('syntyr.collaboration.css', demo)
        self.assertIn('<time datetime=', demo)
        self.assertIn('role="status"', demo)
        self.assertIn('aria-label="', demo)
        self.assertIn('disabled', demo)  # no fake posting or execution
        for textarea in parser.textareas:
            self.assertTrue(parser.textarea_has_name(textarea),
                            "textarea must have a real, nonempty accessible name")
        self.assertNotRegex(demo, r'<button(?![^>]*disabled)[^>]*>\s*(?:Send|Approve|Run)')
        self.assertNotIn("onclick=", demo.lower())

    def test_id_alone_is_not_a_textarea_name(self):
        parser = DemoParser()
        parser.feed('<textarea id="field"></textarea>')
        self.assertFalse(parser.textarea_has_name(parser.textareas[0]))
        with_label = DemoParser()
        with_label.feed('<label for="field">Description</label><textarea id="field"></textarea>')
        self.assertTrue(with_label.textarea_has_name(with_label.textareas[0]))
        empty_label = DemoParser()
        empty_label.feed('<label for="field">  </label><textarea id="field"></textarea>')
        self.assertFalse(empty_label.textarea_has_name(empty_label.textareas[0]))

    def test_release_documentation_and_packaging(self):
        from scripts.package_release import FILES
        self.assertIn("dist/syntyr.collaboration.css", FILES)
        self.assertIn("docs/collaboration.md", FILES)
        self.assertIn("examples/collaboration.html", FILES)
        guide = (ROOT / "docs/collaboration.md").read_text()
        self.assertIn("syntyr.collaboration.css", guide)
        self.assertIn("application", guide.lower())
        self.assertIn("Chatudo", guide)
        self.assertIn("examples/collaboration.html", (ROOT / "README.md").read_text())
        self.assertIn(
            "https://syntyr-css.pages.dev/docs/collaboration.md",
            (ROOT / "llms.txt").read_text(),
            "new public guide must appear in the agent retrieval index",
        )
        example = (ROOT / "examples/collaboration.html").read_text()
        self.assertIn('href="../docs/collaboration.md"', example)
        # The ZIP is a self-contained allowlisted artifact; no HTML-only guide link.
        self.assertIn("docs/collaboration.md", FILES)
        for script in ("browser_matrix.py", "reflow_test.py", "axe_audit.py"):
            self.assertIn('"examples/collaboration.html"', (ROOT / "tests" / script).read_text())


if __name__ == "__main__":
    unittest.main()
