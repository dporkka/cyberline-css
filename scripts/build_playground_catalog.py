"""Generate editable examples from the existing component and free-block galleries.

Those galleries own the MIT HTML snippets. This docs-only build artifact avoids
maintaining duplicate markup or fetching HTML at runtime (also works from file://).
"""
from __future__ import annotations

import argparse
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs/playground-catalog.js"


class CatalogParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.entries: list[dict[str, str]] = []
        self.card: dict[str, str] | None = None
        self.article_depth = 0
        self.field = ""
        self.field_tag = ""
        self.in_source = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag == "article" and "catalog-card" in classes and self.card is None:
            self.card = {"id": a.get("aria-labelledby") or "", "title": "",
                         "module": "", "description": "", "html": "",
                         "keywords": a.get("data-catalog-keywords") or ""}
            self.article_depth = 1
            return
        if self.card is None:
            return
        if tag == "article":
            self.article_depth += 1
        if tag == "pre" and "catalog-source" in classes:
            self.in_source = True
        if tag == "code" and self.in_source:
            self.field, self.field_tag = "html", "code"
        elif tag == "h2" and "syn-heading" in classes and not self.card["title"]:
            self.field, self.field_tag = "title", "h2"
        elif tag == "span" and "syn-badge" in classes and not self.card["module"]:
            self.field, self.field_tag = "module", "span"
        elif tag == "p" and "syn-muted" in classes and not self.card["description"]:
            self.field, self.field_tag = "description", "p"

    def handle_data(self, data: str) -> None:
        if self.card is not None and self.field:
            self.card[self.field] += data

    def handle_endtag(self, tag: str) -> None:
        if self.card is None:
            return
        if tag == self.field_tag:
            self.field, self.field_tag = "", ""
        if tag == "pre":
            self.in_source = False
        if tag == "article":
            self.article_depth -= 1
            if self.article_depth == 0:
                entry = {key: value.strip() for key, value in self.card.items()}
                self.entries.append(entry)
                self.card = None


class BlockParser(CatalogParser):
    """Read the source from the existing free blocks gallery, never the preview."""

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = dict(attrs)
        classes = (a.get("class") or "").split()
        if tag == "article" and "blocks-card" in classes and self.card is None:
            block_id = a.get("data-block-id") or ""
            self.card = {"id": f"block-{block_id}", "title": "", "module": "",
                         "description": "", "html": "", "keywords": a.get("data-block-keywords") or "",
                         "kind": "block", "category": a.get("data-block-category") or ""}
            self.article_depth = 1
            return
        if self.card is None:
            return
        if tag == "article":
            self.article_depth += 1
        if tag == "pre" and "blocks-source" in classes:
            self.in_source = True
        if tag == "code" and self.in_source:
            self.field, self.field_tag = "html", "code"
        elif tag == "h2" and a.get("id") == self.card["id"].replace("block-", "block-title-", 1):
            self.field, self.field_tag = "title", "h2"
        elif tag == "span" and "syn-badge" in classes and not self.card["module"]:
            self.field, self.field_tag = "module", "span"
        elif tag == "p" and "syn-muted" in classes and not self.card["description"]:
            self.field, self.field_tag = "description", "p"


def generate() -> str:
    parser = CatalogParser()
    parser.feed((ROOT / "docs/catalog.html").read_text(encoding="utf-8"))
    blocks = BlockParser()
    blocks.feed((ROOT / "docs/blocks.html").read_text(encoding="utf-8"))
    manifest = json.loads((ROOT / "metadata/components.json").read_text(encoding="utf-8"))
    components = manifest["components"]
    allowed_modules = {item["module"] for item in components}
    entries = parser.entries + blocks.entries
    if len(parser.entries) < 8 or len(blocks.entries) < 20:
        raise ValueError("Expected the full canonical component and free-block galleries")
    if len({entry["id"] for entry in entries}) != len(entries):
        raise ValueError("Duplicate catalog identifiers")
    for entry in entries:
        if not all(entry.values()):
            raise ValueError(f"Incomplete catalog example: {entry['id']}")
        if not re.fullmatch(r"(catalog|block)-[a-z0-9-]+", entry["id"]):
            raise ValueError(f"Unsafe example identifier: {entry['id']}")
        modules = entry["module"].split(" + ")
        if any(module not in allowed_modules for module in modules):
            raise ValueError(f"Unrecognized CSS module: {entry['module']}")
        if len(entry["html"]) > 20000 or "<script" in entry["html"].lower():
            raise ValueError(f"Example must be inert, short HTML: {entry['id']}")
        used_classes = set(re.findall(r"\bsyn-[a-z][a-z0-9-]*", entry["html"]))
        matches = [component for component in components
                   if component["module"] in modules
                   and used_classes.intersection(component["classes"])]
        if entry.get("kind") == "block":
            entry["guidance"] = "Illustrative, MIT-licensed presentation. Use the required CSS modules; your application supplies actions, validation, real data and permissions."
        elif matches:
            matched = max(matches, key=lambda item: len(
                used_classes.intersection(item["classes"])))
            entry["guidance"] = matched["notes"]
        else:
            entry["guidance"] = "See the component API reference for compatible classes and CSS modules."
    payload = json.dumps(entries, ensure_ascii=True, indent=2).replace("<", r"\u003c")
    return f"window.SYNTYR_PLAYGROUND_CATALOG = {payload};\n"


def main() -> int:
    args = argparse.ArgumentParser(description=__doc__)
    args.add_argument("--check", action="store_true")
    options = args.parse_args()
    expected = generate()
    if options.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != expected:
            print("STALE docs/playground-catalog.js: run python3 scripts/build_playground_catalog.py",
                  file=sys.stderr)
            return 1
        print("OK playground examples synchronized with catalog")
        return 0
    OUTPUT.write_text(expected, encoding="utf-8")
    print(f"Generated {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
