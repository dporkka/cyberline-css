"""Contract for opt-in, scoped shadcn/ui semantic-token interoperability."""
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = ROOT / "integrations/shadcn/syntyr.tokens.css"


class ShadcnBridgeContract(unittest.TestCase):
    def test_bridge_is_opt_in_and_does_not_restyle_host_root(self):
        css = BRIDGE.read_text(encoding="utf-8")
        self.assertIn(".syn-root.syn-shadcn", css)
        self.assertIn(".syn-root .syn-shadcn", css)
        self.assertIn("[data-syn-theme]", css)
        self.assertNotIn(":root {", css)
        self.assertNotIn(".dark {", css)
        self.assertNotIn("@apply", css)
        self.assertNotIn("@import", css)
        self.assertNotIn("!important", css)
        for token, target in {
            "background": "bg", "foreground": "text",
            "card": "surface", "card-foreground": "text",
            "primary": "accent", "primary-foreground": "on-accent",
            "muted-foreground": "muted", "destructive": "danger",
            "border": "border-default", "ring": "focus-ring"
        }.items():
            with self.subTest(token=token):
                self.assertIn(f"--{token}: var(--syn-{target});", css)

    def test_bridge_is_separately_exported_from_core(self):
        pkg = json.loads((ROOT / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pkg["exports"]["./shadcn.css"], "./integrations/shadcn/syntyr.tokens.css")
        self.assertIn("integrations/shadcn/", pkg["files"])
        self.assertNotIn("syn-shadcn", (ROOT / "dist/syntyr.core.css").read_text(encoding="utf-8"))

    def test_example_is_real_tailwind_consumer_with_scoped_tokens(self):
        demo = ROOT / "examples/shadcn-bridge"
        pkg = json.loads((demo / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pkg["dependencies"]["@syntyr/css"], "file:../..")
        css = (demo / "src/app.css").read_text(encoding="utf-8")
        self.assertIn('@import "@syntyr/css/shadcn.css";', css)
        self.assertIn("@theme inline", css)
        html = (demo / "index.html").read_text(encoding="utf-8")
        self.assertIn('class="syn-root syn-shadcn"', html)
        self.assertIn('class="bg-primary text-primary-foreground', html)
        self.assertIn('data-syn-theme="noir"', html)
        self.assertTrue((demo / "README.md").exists())


if __name__ == "__main__":
    unittest.main()
