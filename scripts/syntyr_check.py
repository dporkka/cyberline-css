"""Optional, dependency-free static HTML checks against the Syntyr CSS contract.

This is a development tool, not a CSS preprocessor or application dependency.
It validates only literal HTML attributes. Dynamic templates need their own
language-aware integration; false claims about rendered state are avoided.
"""
from __future__ import annotations

import argparse
from difflib import get_close_matches
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "metadata" / "syntyr-contract.json"
# HTMLParser does not synthesize end tags for void elements.
_VOID_TAGS = frozenset({
    "area", "base", "br", "col", "embed", "hr", "img", "input", "link",
    "meta", "param", "source", "track", "wbr",
})


def _stylesheet_name(href: str, names: set[str]) -> str | None:
    """Match a published Syntyr entrypoint, not an unrelated stylesheet."""
    path = urlsplit(href).path.replace("\\", "/")
    for name in sorted(names, key=len, reverse=True):
        if path == name or path.endswith("/" + name):
            return name
    return None


def _is_dynamic(value: str) -> bool:
    return any(char in value for char in "{}$<>")  # conservative template escape


class _SyntyrParser(HTMLParser):
    def __init__(self, contract: dict):
        super().__init__(convert_charrefs=True)
        self.classes = {c["name"]: c for c in contract["classes"]}
        self.attribute_values = contract["attributes"]
        self.stylesheet_names = set(contract["stylesheets"])
        self.linked_stylesheets: set[str] = set()
        self.stylesheet_links: list[tuple[int, int, str]] = []
        self.used_classes: list[tuple[int, int, str]] = []
        self.unscoped_classes: list[tuple[int, int, str]] = []
        self.complete_document = False
        # (tag, known-root-ancestor, possible-dynamic-root-ancestor)
        self.scope_stack: list[tuple[str, bool, bool]] = []
        self.diagnostics: list[dict] = []

    def _error(self, code: str, message: str, line: int, column: int, **details):
        self.diagnostics.append({
            "line": line, "column": column + 1,
            "severity": "error", "code": code, "message": message,
            **details,
        })

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        data = dict(attrs)
        line, col = self.getpos()
        if tag == "html":
            self.complete_document = True
        class_values = [data.get(key) or "" for key in ("class", "classname")]
        local_root = any("syn-root" in value.split()
                         for value in class_values if not _is_dynamic(value))
        dynamic_scope = any(_is_dynamic(value) for value in class_values)
        parent_root = self.scope_stack[-1][1] if self.scope_stack else False
        parent_possible = self.scope_stack[-1][2] if self.scope_stack else False
        has_root = parent_root or local_root
        possibly_scoped = has_root or parent_possible or dynamic_scope
        if tag not in _VOID_TAGS:
            self.scope_stack.append((tag, has_root, possibly_scoped))
        # Inert <template> content may be cloned into an existing Syntyr root.
        within_template = any(frame[0] == "template" for frame in self.scope_stack)
        if tag == "link" and "stylesheet" in (data.get("rel") or "").split():
            name = _stylesheet_name(data.get("href") or "", self.stylesheet_names)
            if name:
                self.linked_stylesheets.add(name)
                self.stylesheet_links.append((line, col, name))
        for class_attr in ("class", "classname"):
            class_value = data.get(class_attr) or ""
            if _is_dynamic(class_value):
                continue  # template output cannot be resolved safely without its renderer
            for name in class_value.split():
                if not name.startswith("syn-"):
                    continue
                if name not in self.classes:
                    matches = get_close_matches(name, self.classes, n=3, cutoff=0.75)
                    suggestions = [
                        {"name": match, "stylesheets": sorted(self.classes[match]["stylesheets"])}
                        for match in matches
                    ]
                    self._error("unknown-class", f"Unknown Syntyr class '{name}'.",
                                line, col, suggestions=suggestions)
                else:
                    self.used_classes.append((line, col, name))
                    if name != "syn-root" and not possibly_scoped and not within_template:
                        self.unscoped_classes.append((line, col, name))
        for name, allowed in self.attribute_values.items():
            value = data.get(name)
            if value is not None and not _is_dynamic(value) and allowed and value not in allowed:
                self._error("invalid-attribute-value",
                            f"Invalid {name}='{value}'; expected one of: {', '.join(allowed)}.",
                            line, col, attribute=name, allowed_values=list(allowed))

    def handle_endtag(self, tag):
        # Drop any inner implicitly-unclosed tags alongside the closing tag.
        # Unmatched closing tags must not disturb the known scope.
        for index in range(len(self.scope_stack) - 1, -1, -1):
            if self.scope_stack[index][0] == tag.lower():
                del self.scope_stack[index:]
                break

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)


def validate_html(html: str, contract: dict, *, stylesheets: set[str] | None = None) -> list[dict]:
    """Return deterministic diagnostics for literal HTML.

    When no Syntyr stylesheet is linked and none is explicitly provided,
    treat input as a partial HTML fragment and skip module presence checks.
    """
    parser = _SyntyrParser(contract)
    parser.feed(html)
    parser.close()
    # All known bundles are assembled from the canonical source module registry.
    # Report repeated/overlapping Syntyr CSS imports before they silently
    # increase transfer size or override component styles. Distinct opt-in
    # modules can still be combined normally.
    sources_by_sheet = {
        name: set(sources) for name, sources in contract.get("stylesheet_sources", {}).items()
    }
    seen: set[str] = set()
    for line, col, name in parser.stylesheet_links:
        if name in seen:
            parser._error("duplicate-stylesheet",
                          f"Duplicate Syntyr stylesheet '{name}' loaded more than once.",
                          line, col, stylesheet=name)
        else:
            sources = sources_by_sheet.get(name, set())
            overlapping = sorted(sources.intersection(
                source for prior in seen for source in sources_by_sheet.get(prior, ())
            ))
            if overlapping:
                with_sheets = sorted(
                    prior for prior in seen if sources.intersection(sources_by_sheet.get(prior, ()))
                )
                parser._error("overlapping-stylesheet",
                              f"'{name}' repeats CSS already loaded by {', '.join(with_sheets)}.",
                              line, col, stylesheet=name, overlaps_with=with_sheets,
                              overlapping_sources=overlapping)
            seen.add(name)
    # A fragment may inherit .syn-root from its host, so only diagnose root
    # scope when the input explicitly contains a full HTML document.
    if parser.complete_document:
        for line, col, name in parser.unscoped_classes:
            parser._error("unscoped-class",
                          f"'{name}' is outside .syn-root; wrap it in a Syntyr root.",
                          line, col, class_name=name, required_root="syn-root")
    loaded = parser.linked_stylesheets if stylesheets is None else stylesheets
    # An explicit empty set means the caller knows no Syntyr CSS is loaded;
    # None with no recognized <link> means an unverifiable HTML fragment.
    if loaded or stylesheets is not None:
        for line, col, name in parser.used_classes:
            expected = set(parser.classes[name]["stylesheets"])
            if not expected.intersection(loaded):
                hint = ", ".join(sorted(expected, key=lambda n: (n.count("/"), len(n)))[:3])
                parser._error("missing-stylesheet",
                              f"'{name}' is not in the loaded Syntyr CSS; add {hint}.",
                              line, col, required_stylesheets=sorted(expected),
                              loaded_stylesheets=sorted(loaded))
    return sorted(parser.diagnostics, key=lambda d: (d["line"], d["column"],
                                                    d["code"] == "missing-stylesheet"))


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description="Validate literal Syntyr classes and states in HTML.")
    p.add_argument("files", nargs="+", type=Path,
                   help="Static HTML files to check; use - to read HTML from stdin.")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.add_argument("--stylesheets", action="append", default=None,
                   help="Known loaded Syntyr stylesheets, comma-separated; overrides HTML links.")
    p.add_argument("--contract", type=Path, default=CONTRACT)
    args = p.parse_args(argv)
    try:
        contract = json.loads(args.contract.read_text(encoding="utf-8"))
        configured = None
        if args.stylesheets is not None:
            configured = set()
            for value in args.stylesheets:
                for item in value.split(","):
                    found = _stylesheet_name(item.strip(), set(contract["stylesheets"]))
                    if found is None:
                        p.error(f"Unrecognized Syntyr stylesheet: {item}")
                    configured.add(found)
        results = []
        for file in args.files:
            source = sys.stdin.read() if str(file) == "-" else file.read_text(encoding="utf-8")
            diagnostics = validate_html(source, contract, stylesheets=configured)
            label = "<stdin>" if str(file) == "-" else str(file)
            results += [{"file": label, **diag} for diag in diagnostics]
    except (OSError, UnicodeError, ValueError, KeyError) as exc:
        print(f"syntyr check: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        for diag in results:
            print(f"{diag['file']}:{diag['line']}:{diag['column']}: "
                  f"{diag['severity']} [{diag['code']}]: {diag['message']}")
        if not results:
            print(f"OK: {len(args.files)} file(s) checked")
    return 1 if results else 0


if __name__ == "__main__":
    sys.exit(main())
