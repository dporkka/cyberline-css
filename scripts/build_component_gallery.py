"""Build one portable component/gallery manifest from canonical Syntyr sources.

All output is static JSON: no runtime dependency, API calls or framework.
The existing curated metadata and copyable docs snippets remain authoritative.
"""
from __future__ import annotations

import argparse
from html import unescape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "metadata/component-gallery.v1.json"
OPEN_CARD = re.compile(r'<article class="catalog-card syn-panel"(?P<attrs>[^>]*)>', re.I)
EXAMPLE = re.compile(
    r'<div class="catalog-preview">\n(?P<preview>.*?)\n          </div>\n'
    r'          <details class="catalog-code-details">.*?'
    r'<pre class="catalog-source"><code>(?P<source>.*?)</code></pre>',
    re.S,
)
TITLE = re.compile(r'<h2 class="syn-heading" id="([^"]+)">([^<]+)</h2>')
MODULE = re.compile(r'<span class="syn-badge">([^<]+)</span>')
DESCRIPTION = re.compile(r'<p class="syn-muted">(.*?)</p>', re.S)
IDENTIFIER = re.compile(r'^[a-z][a-z0-9-]+$')


class ExampleHTML(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.elements: set[str] = set()
        self.classes: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "iframe", "object", "embed"}:
            raise ValueError(f"Unsafe tag in catalog example: {tag}")
        for key, value in attrs:
            if key.lower().startswith("on"):
                raise ValueError(f"Event handler forbidden in catalog example: {key}")
            if key.lower() in {"href", "src", "action"} and value and value.strip().lower().startswith("javascript:"):
                raise ValueError("JavaScript URL forbidden in catalog example")
        self.elements.add(tag)
        for key, value in attrs:
            if key == "class" and value:
                self.classes.update(c for c in value.split() if c.startswith("syn-"))


def build_manifest() -> dict:
    curated = json.loads((ROOT / "metadata/components.json").read_text(encoding="utf-8"))
    if curated["schema_version"] != 1:
        raise ValueError("Unsupported component manifest version")
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if curated["source_version"] != version:
        raise ValueError("Curated component manifest is stale")
    api = json.loads((ROOT / "metadata/syntyr-api.json").read_text(encoding="utf-8"))
    if api["version"] != 1:
        raise ValueError("Unsupported generated CSS API metadata version")
    catalog = (ROOT / "docs/catalog.html").read_text(encoding="utf-8")
    sheet = (ROOT / "dist/syntyr.all.css").read_text(encoding="utf-8")
    matches = list(OPEN_CARD.finditer(catalog))
    if not matches:
        raise ValueError("No component examples found in catalog")
    seen: set[str] = set()
    examples: list[dict] = []
    for index, card in enumerate(matches):
        block = catalog[card.end():matches[index + 1].start() if index + 1 < len(matches) else len(catalog)]
        attrs = card.group("attrs")
        label = re.search(r'aria-labelledby="([^"]+)"', attrs)
        keywords = re.search(r'data-catalog-keywords="([^"]+)"', attrs)
        category = re.search(r'data-catalog-category="([^"]+)"', attrs)
        title = TITLE.search(block)
        module = MODULE.search(block)
        description = DESCRIPTION.search(block)
        snippet = EXAMPLE.search(block)
        if not all((label, keywords, title, module, description, snippet)):
            raise ValueError(f"Incomplete catalog card #{index + 1}")
        identifier, heading_id, raw_title = label[1], title[1], title[2]
        if identifier != heading_id or not IDENTIFIER.fullmatch(identifier) or identifier in seen:
            raise ValueError(f"Invalid or duplicate catalog example id: {identifier}")
        seen.add(identifier)
        css_module = module[1]
        if css_module not in {"syntyr.core.css", "syntyr.recipes.css", "syntyr.geometry.css", "syntyr.viz.css"}:
            raise ValueError(f"Unexpected CSS module: {css_module}")
        raw_html = unescape(snippet["source"]).strip()
        if raw_html != snippet["preview"].strip():
            raise ValueError(f"Catalog preview and copyable HTML differ: {identifier}")
        parser = ExampleHTML()
        parser.feed(raw_html)
        if not parser.elements:
            raise ValueError(f"Empty catalog example: {identifier}")
        css = (ROOT / "dist" / css_module).read_text(encoding="utf-8")
        core_css = (ROOT / "dist/syntyr.core.css").read_text(encoding="utf-8")
        semantic_css = (ROOT / "dist/syntyr.semantic.css").read_text(encoding="utf-8")
        # Optional modules supplement core tokens and controls, not replace them.
        # Preserve the loading order in agent-facing metadata.
        required_modules = (["syntyr.core.css", css_module]
                            if css_module != "syntyr.core.css" else [css_module])
        for cls in parser.classes:
            selector = r'\.' + re.escape(cls) + r'(?![\w-])'
            if not (re.search(selector, css) or re.search(selector, core_css)):
                if re.search(selector, semantic_css):
                    if "syntyr.semantic.css" not in required_modules:
                        required_modules.append("syntyr.semantic.css")
                else:
                    raise ValueError(f"Unknown class {cls} in {css_module}: {identifier}")
            if not re.search(r'\.' + re.escape(cls) + r'(?![\w-])', sheet):
                raise ValueError(f"Class missing from all.css: {cls}")
        examples.append({
            "id": identifier,
            "title": unescape(raw_title),
            "module": css_module,
            "required_stylesheets": required_modules,
            "description": unescape(re.sub(r"<[^>]+>", "", description[1])).strip(),
            "keywords": keywords[1].lower().split(),
            "category": category[1] if category else "uncategorized",
            "elements": sorted(parser.elements),
            "classes": sorted(parser.classes),
            "html": raw_html,
        })
    return {
        "schema_version": 1,
        "source_version": version,
        "completeness": "curated-examples",
        "source_of_truth": {
            "components": "metadata/components.json",
            "examples": "docs/catalog.html",
            "themes": "metadata/syntyr-api.json",
        },
        "scope": "syn-root",
        "runtime_requirement": "none",
        "note": "Unreleased source-tree candidate, not a guarantee of published alpha.4 availability. Host applications own behavior, data and validation.",
        "components": curated["components"],
        "recipes": curated["recipes"],
        "themes": api["themes"],
        "examples": examples,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="fail if checked-in JSON is stale")
    args = parser.parse_args()
    try:
        rendered = json.dumps(build_manifest(), ensure_ascii=False, indent=2) + "\n"
    except (ValueError, KeyError, OSError) as error:
        print(f"INVALID component gallery: {error}", file=sys.stderr)
        return 1
    if args.check:
        if not OUTPUT.is_file() or OUTPUT.read_text(encoding="utf-8") != rendered:
            print("STALE component gallery; run python3 scripts/build_component_gallery.py", file=sys.stderr)
            return 1
        print(f"OK {OUTPUT.relative_to(ROOT)}")
        return 0
    OUTPUT.write_text(rendered, encoding="utf-8")
    print(f"WROTE {OUTPUT.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
