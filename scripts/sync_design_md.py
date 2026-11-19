#!/usr/bin/env python3
"""Sync the Google DESIGN.md-compatible Studio token snapshot from canonical CSS.

Syntyr's runtime source of truth stays src/tokens.css. This script uses only the
Python standard library and never modifies CSS or a consumer build artifact.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
DESIGN = ROOT / "DESIGN.md"
SOURCE = ROOT / "src/tokens.css"

COLOR_ROLES = (
    ("primary", "accent"),
    ("secondary", "accent-2"),
    ("background", "bg"),
    ("surface", "surface"),
    ("surface-raised", "surface-hi"),
    ("text", "text"),
    ("muted", "muted"),
    ("on-primary", "on-accent"),
    ("border", "frame"),
    ("border-strong", "frame-strong"),
    ("danger", "danger"),
    ("success", "success"),
    ("warning", "warning"),
)
SPACE_ROLES = ("xs", "sm", "md", "lg", "xl")


def _declarations(source: str, selector: str) -> dict[str, str]:
    match = re.search(selector + r"\s*\{([^{}]*)\}", source, flags=re.S)
    if not match:
        raise ValueError("Could not find the expected CSS token scope")
    return dict(re.findall(r"(--syn-[\w-]+):\s*([^;]+);", match.group(1)))


def _required(declarations: dict[str, str], name: str) -> str:
    key = "--syn-" + name
    if key not in declarations:
        raise ValueError(f"Required Syntyr token missing: {key}")
    return declarations[key].strip()


def _dimension(value: str) -> str:
    # CSS accepts '.375rem'; use canonical '0.375rem' for portable token parsers.
    return re.sub(r"^\.", "0.", value)


def _resolved_dimension(declarations: dict[str, str], name: str) -> str:
    # DESIGN.md requires a concrete size, but CSS role aliases can point at base tokens.
    seen: set[str] = set()
    while True:
        if name in seen:
            raise ValueError(f"Circular Syntyr token alias: --syn-{name}")
        seen.add(name)
        value = _required(declarations, name)
        alias = re.fullmatch(r"var\(\s*--syn-([\w-]+)\s*\)", value)
        if alias:
            name = alias.group(1)
            continue
        if "var(" in value:
            raise ValueError(f"Unsupported Syntyr token expression: {value}")
        return _dimension(value)


def build_frontmatter(css: str) -> str:
    base = _declarations(css, r":where\(\.syn-root\)")
    studio = _declarations(
        css, r":where\(\.syn-root,\s*\.syn-root\[data-syn-theme=\"studio\"\],\s*\.syn-root \[data-syn-theme=\"studio\"\]\)"
    )

    lines = [
        "---",
        "version: alpha",
        "name: Syntyr Studio",
        'description: "Framework-neutral, CSS-first Syntyr design contract; Studio reference palette."',
        "colors:",
    ]
    for role, css_name in COLOR_ROLES:
        value = _required(studio, css_name)
        if not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
            raise ValueError(f"Studio {css_name} must be a static hex color for portable DESIGN.md")
        lines.append(f"  {role}: {json.dumps(value)}")
    lines.extend((
        "typography:",
        "  body:",
        f"    fontFamily: {json.dumps(_required(base, 'font'))}",
        f"    fontSize: {json.dumps(_resolved_dimension(base, 'type-body'))}",
        "    fontWeight: 400",
        f"    lineHeight: {_required(base, 'leading-body')}",
        "spacing:",
    ))
    for index, role in enumerate(SPACE_ROLES, start=1):
        lines.append(f"  {role}: {json.dumps(_dimension(_required(base, f'space-{index}')))}")
    lines.extend((
        "rounded:",
        f"  default: {json.dumps(_dimension(_required(studio, 'radius')))}",
        "components:",
        "  application:",
        '    backgroundColor: "{colors.background}"',
        '    textColor: "{colors.text}"',
        "  panel:",
        '    backgroundColor: "{colors.surface}"',
        '    textColor: "{colors.text}"',
        "  divider:",
        '    backgroundColor: "{colors.border}"',
        "  raised-surface:",
        '    backgroundColor: "{colors.surface-raised}"',
        '    textColor: "{colors.text}"',
        "  primary-button:",
        '    backgroundColor: "{colors.primary}"',
        '    textColor: "{colors.on-primary}"',
        "  secondary-button:",
        '    backgroundColor: "{colors.surface-raised}"',
        '    textColor: "{colors.text}"',
        "  secondary-text:",
        '    textColor: "{colors.muted}"',
        "  strong-divider:",
        '    backgroundColor: "{colors.border-strong}"',
        "  secondary-accent:",
        '    textColor: "{colors.secondary}"',
        "  status-danger:",
        '    textColor: "{colors.danger}"',
        "  status-success:",
        '    textColor: "{colors.success}"',
        "  status-warning:",
        '    textColor: "{colors.warning}"',
        "---",
        "",
    ))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Fail if the DESIGN.md tokens drift from CSS")
    args = parser.parse_args()
    frontmatter = build_frontmatter(SOURCE.read_text(encoding="utf-8"))
    if not DESIGN.exists():
        raise SystemExit("DESIGN.md missing; create the authored guidance before syncing")
    current = DESIGN.read_text(encoding="utf-8")
    match = re.match(r"\A---\r?\n.*?\r?\n---\r?\n", current, flags=re.S)
    if not match:
        raise SystemExit("DESIGN.md must begin with YAML frontmatter delimited by ---")
    wanted = frontmatter + current[match.end():]
    if wanted == current:
        print("DESIGN.md tokens match src/tokens.css")
        return 0
    if args.check:
        print("DESIGN.md token snapshot has drifted. Run: python3 scripts/sync_design_md.py")
        return 1
    DESIGN.write_text(wanted, encoding="utf-8")
    print("Updated DESIGN.md token snapshot from src/tokens.css")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
