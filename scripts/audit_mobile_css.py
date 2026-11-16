"""Conservative, dependency-free declaration audit for React Native migration.

This is a *report*, not a CSS parser, transpiler, or native compatibility claim.
Selectors, cascade, inheritance, actual platform versions, and runtime
accessibility cannot be translated by this tool. Unknowns are never green.
"""
from __future__ import annotations

import argparse
from collections import Counter
import json
from pathlib import Path
import re
import sys

# Deliberately narrow React Native style-property allowlist. CSS property
# support differs by React Native version; no inferred support for unknowns.
PORTABLE = frozenset({
    "align-content", "align-items", "align-self", "background-color",
    "border-bottom-color", "border-color", "border-left-color",
    "border-right-color", "border-top-color", "color", "flex", "flex-basis",
    "flex-direction", "flex-grow", "flex-shrink", "flex-wrap", "font-family",
    "font-size", "font-style", "font-weight", "height", "justify-content",
    "letter-spacing", "line-height", "margin", "margin-bottom", "margin-left",
    "margin-right", "margin-top", "max-height", "max-width", "min-height",
    "min-width", "opacity", "padding", "padding-bottom", "padding-left",
    "padding-right", "padding-top", "position", "text-align",
    "text-decoration-line", "text-transform", "width", "z-index", "top",
    "right", "bottom", "left", "border-radius", "border-bottom-left-radius",
    "border-bottom-right-radius", "border-top-left-radius", "border-top-right-radius",
    "border-width", "border-top-width", "border-bottom-width",
    "border-left-width", "border-right-width", "overflow", "display",
    "gap", "row-gap", "column-gap", "aspect-ratio",
})
# CSS has semantics RN does not implement, or needs a native-specific structure.
WEB_ONLY = frozenset({
    "animation", "animation-delay", "animation-duration", "animation-name",
    "animation-timing-function", "appearance", "backdrop-filter",
    "background", "background-attachment", "background-image",
    "background-position", "background-repeat", "background-size", "clip-path",
    "content", "container", "container-name", "container-type", "cursor",
    "filter", "float", "grid", "grid-area", "grid-auto-columns",
    "grid-auto-flow", "grid-auto-rows", "grid-column", "grid-row",
    "grid-template", "grid-template-areas", "grid-template-columns",
    "grid-template-rows", "isolation", "mix-blend-mode", "object-fit",
    "outline", "outline-color", "outline-offset", "outline-style",
    "outline-width", "pointer-events", "scroll-behavior", "scroll-margin",
    "scroll-padding", "scroll-snap-align", "scroll-snap-type", "transition",
    "transition-duration", "transition-property", "transition-timing-function",
    "user-select", "vertical-align", "visibility",
})
# Adaptable, but CSS syntax is not directly a React Native style object.
NATIVE_RECIPE = frozenset({
    "box-shadow", "text-shadow", "transform", "transform-origin",
    "inset", "inset-block", "inset-inline", "inset-inline-start",
    "inset-inline-end", "inset-block-start", "inset-block-end",
    "padding-inline", "padding-inline-start", "padding-inline-end",
    "padding-block", "padding-block-start", "padding-block-end",
    "margin-inline", "margin-inline-start", "margin-inline-end",
    "margin-block", "margin-block-start", "margin-block-end",
    "border-inline", "border-block", "box-sizing", "text-wrap",
})
_NUMERIC = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)\Z")
_PERCENT = re.compile(r"[-+]?(?:\d+(?:\.\d*)?|\.\d+)%\Z")
_PROPERTY = re.compile(r"\s*([a-zA-Z_-][\w-]*)\s*:\s*(.*?)\s*\Z", re.DOTALL)
_CSS_EXPRESSION = re.compile(
    r"\b(?:var|env|calc|min|max|clamp|color-mix|light-dark)\s*\(|"
    r"(?:\d|\.)(?:rem|em|vh|vw|svh|dvh|lvh|ch|ex|vmin|vmax|px)\b|!important\b",
    re.IGNORECASE,
)
_COLOR = re.compile(r"(?:#[0-9a-f]{3,8}|[a-z-]+|rgba?\([^)]*\)|hsla?\([^)]*\))\Z", re.IGNORECASE)
_DIMENSIONS_PERCENT = {"width", "height", "min-width", "min-height", "max-width", "max-height", "top", "right", "bottom", "left"}
_CSS_GLOBAL_VALUES = {"inherit", "initial", "unset", "revert", "revert-layer"}
_INTRINSIC_VALUES = {"min-content", "max-content", "fit-content", "fit-content()", "stretch"}
_SIMPLE_COLORS = {"transparent", "black", "white", "red", "green", "blue"}
_WEB_AT_RULES = ("@keyframes", "@-webkit-keyframes", "@font-face", "@property", "@counter-style")
_CONTEXT_AT_RULES = ("@media", "@container", "@supports", "@layer", "@scope", "@starting-style")


def _declarations(source: str):
    """Extract basic declarations with context, respecting comments/strings/functions.

    This is intentionally a bounded scanner, not a CSS grammar: it does not
    interpret selectors, nesting syntax, or property-specific grammars.
    """
    contexts: list[str] = []
    chars: list[str] = []
    segment_line = 1
    line = 1
    quote = ""
    comment = False
    escaped = False
    parens = 0
    brackets = 0
    i = 0
    while i < len(source):
        ch = source[i]
        next_char = source[i + 1] if i + 1 < len(source) else ""
        if ch == "\n":
            line += 1
        if comment:
            if ch == "*" and next_char == "/":
                comment = False
                i += 2
            else:
                i += 1
            continue
        if quote:
            chars.append(ch)
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == quote:
                quote = ""
            i += 1
            continue
        if ch == "/" and next_char == "*":
            comment = True
            i += 2
            continue
        if ch in ("'", '"'):
            quote = ch
            chars.append(ch)
        elif ch == "(":
            parens += 1
            chars.append(ch)
        elif ch == ")":
            parens = max(0, parens - 1)
            chars.append(ch)
        elif ch == "[":
            brackets += 1
            chars.append(ch)
        elif ch == "]":
            brackets = max(0, brackets - 1)
            chars.append(ch)
        elif parens == 0 and brackets == 0 and ch in "{};":
            fragment = "".join(chars).strip()
            if ch == "{":
                contexts.append(fragment)
            elif ch == ";" and contexts and fragment:
                yield fragment, segment_line, tuple(contexts)
            elif ch == "}":
                if contexts and fragment:
                    yield fragment, segment_line, tuple(contexts)
                if contexts:
                    contexts.pop()
            chars.clear()
            segment_line = line
        else:
            if not ch.isspace() and not "".join(chars).strip():
                segment_line = line
            chars.append(ch)
        i += 1


def _classify(prop: str, value: str, contexts: tuple[str, ...]) -> tuple[str, str]:
    if any(ctx.strip().lower().startswith(_WEB_AT_RULES) for ctx in contexts):
        return "web-only", "CSS at-rule has no direct native style equivalent"
    if prop.startswith("--"):
        return "adapt", "Export literal tokens; React Native cannot consume CSS custom properties"
    if prop in WEB_ONLY:
        return "web-only", "Browser-specific CSS feature; use native components or behavior"
    if prop in NATIVE_RECIPE:
        return "adapt", "Requires an explicit React Native style or platform-aware recipe"
    if prop not in PORTABLE:
        return "unknown", "Not in Syntyr's conservative React Native property allowlist"
    if value.lower() in _CSS_GLOBAL_VALUES:
        return "adapt", "CSS cascade-wide keywords have no native style equivalent"
    if prop in _DIMENSIONS_PERCENT and value.lower() in _INTRINSIC_VALUES:
        return "adapt", "Intrinsic CSS sizing is not a React Native dimension"
    if prop in {"font-size", "padding", "padding-top", "padding-bottom", "padding-left", "padding-right"} and value.lower() in {"auto", "larger", "smaller", "small", "medium", "large", "x-large"}:
        return "adapt", "CSS sizing keyword must be mapped to a numeric native value"
    if prop == "font-family" and "," in value:
        return "adapt", "React Native fontFamily expects a resolved font, not a CSS fallback list"
    if prop == "display" and value.lower() not in {"flex", "none"}:
        return "web-only", "Only display: flex/none are treated as native-compatible"
    if prop == "position" and value.lower() not in {"relative", "absolute"}:
        return "web-only", "CSS positioning mode is not a React Native positioning mode"
    if prop == "overflow" and value.lower() not in {"visible", "hidden"}:
        return "adapt", "Use a native scrolling container when scrolling is required"
    if prop == "flex" and not _NUMERIC.fullmatch(value):
        return "adapt", "CSS flex shorthand differs from React Native flex number"
    if prop == "line-height" and _NUMERIC.fullmatch(value):
        return "adapt", "CSS unitless line-height is a ratio; native lineHeight uses points"
    if _CSS_EXPRESSION.search(value):
        return "adapt", "CSS length/function syntax must be resolved to native values"
    if "%" in value and not (prop in _DIMENSIONS_PERCENT and _PERCENT.fullmatch(value)):
        return "adapt", "Percentage sizing requires target-specific validation"
    if prop.endswith("color") or prop == "color":
        if not _COLOR.fullmatch(value) or (re.fullmatch(r"[a-z-]+", value, re.IGNORECASE) and value.lower() not in _SIMPLE_COLORS):
            return "adapt", "Resolve color to a known native-compatible literal"
    if any(ctx.strip().lower().startswith(_CONTEXT_AT_RULES) for ctx in contexts):
        return "adapt", "CSS conditional/cascade rule needs native runtime adaptation"
    return "portable", "Property/value has a straightforward native style mapping; selectors are not portable"


def audit_css(css: str, *, source: str = "<inline>") -> list[dict]:
    """Return per-declaration findings; unknowns and ambiguous values are not safe."""
    findings = []
    for fragment, line, contexts in _declarations(css):
        match = _PROPERTY.fullmatch(fragment)
        if not match:
            continue
        prop, value = match.group(1).lower(), match.group(2).strip()
        status, reason = _classify(prop, value, contexts)
        findings.append({
            "source": source, "line": line, "property": prop,
            "value": value, "status": status, "reason": reason,
        })
    return findings


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("css", nargs="+", type=Path, help="CSS files to audit (no native build required)")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--strict", action="store_true", help="fail if any declaration needs adaptation or has unknown support")
    args = parser.parse_args(argv)
    findings = []
    for path in args.css:
        try:
            contents = path.read_text(encoding="utf-8")
        except OSError as error:
            parser.error(str(error))
        findings.extend(audit_css(contents, source=str(path)))
    counts = Counter(f["status"] for f in findings)
    summary = {name: counts[name] for name in ("portable", "adapt", "web-only", "unknown")}
    summary["total"] = len(findings)
    report = {"target": "react-native", "summary": summary, "findings": findings}
    if args.format == "json":
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("React Native declaration audit (not a CSS-to-native compiler)")
        print(" | ".join(f"{key}: {count}" for key, count in summary.items()))
        for finding in findings:
            if finding["status"] != "portable":
                print(f"{finding['source']}:{finding['line']}: {finding['status']}: "
                      f"{finding['property']}: {finding['value']} — {finding['reason']}")
    return int(args.strict and summary["total"] != summary["portable"])


if __name__ == "__main__":
    sys.exit(main())
