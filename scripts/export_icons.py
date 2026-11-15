"""Deterministically export Syntyr's original inline icons to optional SVG assets.

No external icon code is copied or fetched; the blocks gallery remains the
single authoritative source. Exported SVG is decorative by default.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "blocks/icons.json"
DEST = ROOT / "assets/icons"
MANIFEST = ROOT / "metadata/design-assets.json"
PATTERNS = ("dots", "blueprint", "diagonal", "hatch", "scanlines")
# These references are research only; none of their implementation is bundled.
REFERENCES = (
    {"name": "Lucide", "license": "ISC", "url": "https://github.com/lucide-icons/lucide", "bundled": False},
    {"name": "Tabler Icons", "license": "MIT", "url": "https://github.com/tabler/tabler-icons", "bundled": False},
    {"name": "Radix Colors", "license": "MIT", "url": "https://github.com/radix-ui/colors", "bundled": False},
    {"name": "Open Props", "license": "MIT", "url": "https://github.com/argyleink/open-props", "bundled": False},
    {"name": "pattern.css", "license": "MIT", "url": "https://github.com/bansal-io/pattern.css", "bundled": False},
)


def icons() -> list[dict[str, str]]:
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    result = data["icons"]
    ids = [icon["id"] for icon in result]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate icon ID")
    for icon in result:
        if not re.fullmatch(r"[a-z][a-z0-9-]*", icon["id"]):
            raise ValueError("Unsafe icon ID")
        body = ET.fromstring("<root>" + icon["body"] + "</root>")
        for element in body.iter():
            if element is body:
                continue
            if element.tag not in {"path", "circle", "rect", "ellipse"}:
                raise ValueError("Unexpected SVG element")
            if any(key.startswith("on") or key in {"href", "style"} for key in element.attrib):
                raise ValueError("Unexpected SVG attribute")
        if len(body) == 0:
            raise ValueError("Empty icon body")
    return result


def icon_paths() -> tuple[str, ...]:
    return tuple("assets/icons/" + icon["id"] + ".svg" for icon in icons())


def exports() -> dict[Path, bytes]:
    records = icons()
    output = {}
    for icon in records:
        svg = (
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" '
            'fill="none" stroke="currentColor" stroke-width="1.7" '
            'stroke-linecap="round" stroke-linejoin="round" '
            'aria-hidden="true" focusable="false">\n  '
            + icon["body"] + '\n</svg>\n'
        )
        output[DEST / (icon["id"] + ".svg")] = svg.encode("utf-8")
    manifest = {
        "version": 1,
        "license": "MIT",
        "origin": "original Syntyr artwork",
        "icons": [icon["id"] for icon in records],
        "patterns": ["syn-pattern--" + name for name in PATTERNS],
        "external_references": list(REFERENCES),
    }
    output[MANIFEST] = (json.dumps(manifest, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    return output


def run(check: bool) -> int:
    expected = exports()
    stale = []
    for path, contents in expected.items():
        if check:
            if not path.is_file() or path.read_bytes() != contents:
                stale.append(path)
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(contents)
    if DEST.exists():
        unexpected = sorted(p for p in DEST.iterdir() if p.is_file() and p not in expected)
        if unexpected:
            stale.extend(unexpected)
    if stale:
        print("STALE design assets: " + ", ".join(str(x.relative_to(ROOT)) for x in stale), file=sys.stderr)
        return 1
    print(("OK" if check else "EXPORTED") + f" {len(expected) - 1} original SVG icons and attribution manifest")
    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    sys.exit(run(parser.parse_args().check))
