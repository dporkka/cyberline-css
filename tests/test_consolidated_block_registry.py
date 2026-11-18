"""Regression contract for reconciled free website, app and editorial blocks."""
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
ADDED = {
    "auth-sign-in", "auth-recovery", "docs-layout", "error-recovery",
    "empty-state", "content-collection", "mega-navigation",
}


class ConsolidatedBlockRegistryTests(unittest.TestCase):
    def test_distinct_patterns_are_available_once_in_manifest_and_registry(self):
        blocks = json.loads((ROOT / "blocks/manifest.json").read_text())["blocks"]
        ids = [block["id"] for block in blocks]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(ADDED.issubset(ids), ADDED.difference(ids))
        items = json.loads((ROOT / "registry/registry.json").read_text())["items"]
        names = [item["name"] for item in items]
        self.assertEqual(len(names), len(set(names)))
        for ident in ADDED:
            with self.subTest(block=ident):
                self.assertEqual(ids.count(ident), 1)
                self.assertEqual(names.count(ident), 1)
                snippet = (ROOT / "blocks/snippets" / f"{ident}.html").read_text()
                item = json.loads((ROOT / "registry/r" / f"{ident}.json").read_text())
                self.assertEqual(item["name"], ident)
                self.assertEqual(item["files"][0]["content"], snippet)

    def test_public_block_count_is_consistent_with_manifest(self):
        total = len(json.loads((ROOT / "blocks/manifest.json").read_text())["blocks"])
        readme = (ROOT / "README.md").read_text()
        guide = (ROOT / "docs/blocks-guide.md").read_text()
        llms = (ROOT / "llms.txt").read_text()
        self.assertIn(f"{total} free copy-owned HTML blocks", readme)
        self.assertIn(f"[{total} copy-owned blocks", readme)
        self.assertIn(f"[Browse {total} blocks]", guide)
        self.assertIn(f"The {total} copy-owned HTML compositions", guide)
        self.assertIn(f"{total} copy-owned MIT sections", llms)

    def test_site_header_footer_remain_single_canonical_ids(self):
        blocks = json.loads((ROOT / "blocks/manifest.json").read_text())["blocks"]
        ids = [block["id"] for block in blocks]
        self.assertEqual(ids.count("site-header"), 1)
        self.assertEqual(ids.count("site-footer"), 1)
        self.assertNotIn("site-header-footer", ids)


if __name__ == "__main__":
    unittest.main()
