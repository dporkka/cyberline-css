"""Audit exact public-class collisions with another CSS stylesheet.

Requires only the Python standard library. This reports class names found in
explicit selectors; it is not proof of compatibility (resets, element selectors,
specificity, and styles from dynamic CSS generators can still conflict).

Example: python3 scripts/audit_class_collisions.py --css host.css --json
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
CLASS_SELECTOR = re.compile(r"\.((?:\\.|[A-Za-z_-][A-Za-z0-9_-]*)+)")
TOKEN_DECLARATION = re.compile(r"(?<![A-Za-z0-9_-])(--syn-[A-Za-z0-9_-]+)\s*:")


def _mask_comments_and_strings(source: str) -> str:
    """Keep punctuation structure without treating CSS strings as selectors."""
    out = []
    i = 0
    while i < len(source):
        if source.startswith("/*", i):
            end = source.find("*/", i + 2)
            i = len(source) if end == -1 else end + 2
            out.append(" ")
        elif source[i] in ("'", '"'):
            quote = source[i]
            i += 1
            while i < len(source):
                if source[i] == "\\":
                    i += 2
                elif source[i] == quote:
                    i += 1
                    break
                else:
                    i += 1
            out.append(" ")
        else:
            out.append(source[i])
            i += 1
    return "".join(out)


def extract_css_classes(css: str) -> set[str]:
    """Discover explicit class selectors, including escaped punctuation.

    Handles nested @media/@layer blocks and native CSS nesting. It does not
    expand compiler-generated utilities or concatenated CSS nesting suffixes.
    """
    classes: set[str] = set()
    prelude: list[str] = []
    for char in _mask_comments_and_strings(css):
        if char == "{":
            selector = "".join(prelude).strip()
            if selector and not selector.startswith("@"):
                for match in CLASS_SELECTOR.finditer(selector):
                    classes.add(re.sub(r"\\(.)", r"\1", match.group(1)))
            prelude.clear()
        elif char in ("}", ";"):
            prelude.clear()
        else:
            prelude.append(char)
    return classes


def audit_stylesheet(
    css: str,
    public_classes: set[str],
    *,
    public_tokens: set[str] | frozenset[str] = frozenset(),
) -> dict:
    """Compare declared names, not runtime styling or cascade compatibility."""
    external = extract_css_classes(css)
    external_tokens = set(TOKEN_DECLARATION.findall(_mask_comments_and_strings(css)))
    return {
        "other_class_count": len(external),
        "exact_overlap": sorted(external & public_classes),
        "other_syn_classes": sorted(c for c in external if c.startswith("syn-")),
        "exact_token_overlap": sorted(external_tokens & public_tokens),
        "other_syn_tokens": sorted(external_tokens),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--css", action="append", required=True, type=Path,
                        help="Other framework/app CSS file; repeat for multiple files")
    parser.add_argument("--json", action="store_true", help="Write machine-readable report")
    parser.add_argument("--fail-on-overlap", action="store_true",
                        help="Exit 1 if any external selector matches a Syntyr class")
    args = parser.parse_args(argv)
    api = json.loads((ROOT / "metadata/syntyr-api.json").read_text(encoding="utf-8"))
    public_classes = {c["name"] for c in api["classes"]}
    public_tokens = {t["name"] for t in api["tokens"]}
    if not public_classes or any(not name.startswith("syn-") for name in public_classes):
        parser.error("Syntyr class inventory is empty or not entirely syn-prefixed")
    if not public_tokens or any(not name.startswith("--syn-") for name in public_tokens):
        parser.error("Syntyr token inventory is empty or not entirely --syn-prefixed")
    comparisons = []
    for path in args.css:
        data = audit_stylesheet(path.read_text(encoding="utf-8"), public_classes,
                                public_tokens=public_tokens)
        comparisons.append({"source": str(path), **data})
    result = {"syntyr_class_count": len(public_classes),
              "syntyr_token_count": len(public_tokens), "comparisons": comparisons,
              "limitations": "Exact selectors and custom property declarations only; "
                             "no compiler expansion, CSS resets, or specificity analysis."}
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for item in comparisons:
            print(f"{item['source']}: {item['other_class_count']} classes, "
                  f"{len(item['exact_overlap'])} exact overlaps: "
                  f"{', '.join(item['exact_overlap']) or 'none'}; "
                  f"{len(item['exact_token_overlap'])} token overlaps: "
                  f"{', '.join(item['exact_token_overlap']) or 'none'}")
        print("Scope: literal selectors; inspect global styles and cascade separately.")
    return int(args.fail_on_overlap and any(
        x["exact_overlap"] or x["exact_token_overlap"] for x in comparisons
    ))


if __name__ == "__main__":
    sys.exit(main())
