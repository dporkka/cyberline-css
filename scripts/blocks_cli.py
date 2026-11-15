"""Dependency-free source installer for Syntyr's MIT-licensed HTML blocks.

This is an optional development-time tool, not a Syntyr runtime requirement.
No network requests, package manager, JS runtime, or license server.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ALLOWED_MODULES = frozenset(
    {"core", "recipes", "geometry", "symbols", "viz", "motion", "effects", "utilities"}
)
IDENTIFIER = re.compile(r"[a-z][a-z0-9-]*\Z")


class BlockInstallError(ValueError):
    """A user-facing validation or file safety failure."""


def load_catalog() -> dict:
    """Validate the public registry before using paths from metadata."""
    document = json.loads((ROOT / "blocks/manifest.json").read_text(encoding="utf-8"))
    if document.get("version") != 1 or not isinstance(document.get("blocks"), list):
        raise BlockInstallError("Unsupported Syntyr block manifest format")
    seen = set()
    for block in document["blocks"]:
        ident = block.get("id")
        modules = block.get("modules")
        if not isinstance(ident, str) or not IDENTIFIER.fullmatch(ident) or ident in seen:
            raise BlockInstallError("Invalid or duplicated block ID in the registry")
        seen.add(ident)
        if not isinstance(modules, list) or not modules or modules[0] != "core":
            raise BlockInstallError(f"Invalid module declaration for {ident}")
        if not all(isinstance(module, str) and module in ALLOWED_MODULES for module in modules):
            raise BlockInstallError(f"Unknown CSS module for {ident}")
        if len(set(modules)) != len(modules):
            raise BlockInstallError(f"Duplicated CSS module for {ident}")
        if not all(isinstance(block.get(field), str) for field in ("title", "category", "description")):
            raise BlockInstallError(f"Incomplete block metadata for {ident}")
    return document


def list_blocks(document: dict, category: str | None, as_json: bool) -> None:
    blocks = document["blocks"]
    if category:
        blocks = [block for block in blocks if block["category"].casefold() == category.casefold()]
    if as_json:
        print(json.dumps({"version": document["version"], "blocks": blocks}, indent=2))
    else:
        for block in blocks:
            print(f"{block['id']:<24} {block['category']:<15} {block['title']}")


def installation_files(document: dict, identifiers: list[str]) -> tuple[dict[str, bytes], list[str]]:
    registry = {block["id"]: block for block in document["blocks"]}
    unique_ids = list(dict.fromkeys(identifiers))
    for ident in unique_ids:
        if ident not in registry:
            raise BlockInstallError(f"Unknown block: {ident}")
    modules = list(dict.fromkeys(
        module for ident in unique_ids for module in registry[ident]["modules"]
    ))
    # Modules are only loaded when explicitly selected by block metadata.
    assets: dict[str, bytes] = {}
    for ident in unique_ids:
        path = ROOT / "blocks/snippets" / f"{ident}.html"
        assets[f"blocks/{ident}.html"] = path.read_bytes()
    for module in modules:
        path = ROOT / "dist" / f"syntyr.{module}.css"
        assets[f"css/syntyr.{module}.css"] = path.read_bytes()

    links = "\n".join(
        f'<link rel="stylesheet" href="/syntyr/css/syntyr.{module}.css">'
        for module in modules
    )
    readme = (
        "# Syntyr free block installation (MIT)\n\n"
        "These are static examples, not working authentication, payment, filter, or "
        "data persistence features. Bind routes, forms, authorization, CSRF and "
        "server data in your host application.\n\n"
        "## CSS for the selected blocks\n\n"
        "Put these stylesheets in the application's HTML head, in this order "
        "(adjust URLs to your hosting root):\n\n"
        "```html\n" + links + "\n```\n\n"
        "Copy markup from `syntyr/blocks/*.html` into your own HTML, Go templ, "
        "HTMX, Astro, Rails, Django, React or other templates. JSX needs attribute "
        "syntax conversion. Keep its semantic labels and accessible states. "
        "Do not load `syntyr.all.css` alongside these modular stylesheets.\n\n"
        "## Provenance and licensing\n\n"
        "The contents of this folder come from the public Syntyr MIT repository. "
        "The free core and blocks remain MIT-licensed. Retain the MIT copyright "
        "notice from the originating Syntyr LICENSE when redistributing. "
        "The `installed.json` registry records the source version and SHA-256 "
        "hashes of the installed files. It does not convey premium license rights.\n"
    )
    assets["README.md"] = readme.encode("utf-8")
    assets["LICENSE-MIT"] = (ROOT / "LICENSE").read_bytes()
    provenance = {
        "schema_version": 1,
        "syntyr_version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "license": "MIT",
        "blocks": unique_ids,
        "modules": modules,
        "sha256": {
            name: hashlib.sha256(content).hexdigest()
            for name, content in sorted(assets.items())
        },
    }
    assets["installed.json"] = (json.dumps(provenance, indent=2, sort_keys=True) + "\n").encode("utf-8")
    return assets, modules


def install(document: dict, identifiers: list[str], output: Path, dry_run: bool) -> None:
    assets, modules = installation_files(document, identifiers)
    # Preserve the path spelling so a symlink is not silently followed.
    root = output.expanduser().absolute() / "syntyr"
    files = {root / name: contents for name, contents in assets.items()}
    # Validate all outputs before creating any files. Don't follow a pre-existing
    # symlink within the destination tree, even if no file exists at the end.
    for path in (*reversed(root.parents), root, root / "blocks", root / "css"):
        if path.is_symlink():
            raise BlockInstallError(f"Refusing to write through symlink: {path}")
        if path.exists() and not path.is_dir():
            raise BlockInstallError(f"Expected a directory, found a file: {path}")
    for path in files:
        if path.is_symlink():
            raise BlockInstallError(f"Refusing to overwrite symlink: {path}")
        if path.exists():
            raise BlockInstallError(f"Refusing to overwrite existing file: {path}")

    print("Syntyr MIT blocks: " + ", ".join(dict.fromkeys(identifiers)))
    print("Required CSS modules: " + ", ".join(modules))
    for path in files:
        print(("[dry-run] " if dry_run else "Write ") + str(path.relative_to(root.parent)))
    if dry_run:
        return
    for path, content in files.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Discover and install free Syntyr HTML/CSS blocks")
    commands = parser.add_subparsers(dest="command", required=True)
    listing = commands.add_parser("list", help="List blocks and metadata")
    listing.add_argument("--category", help="Exact category, case-insensitive")
    listing.add_argument("--json", action="store_true", help="Machine-readable manifest")
    addition = commands.add_parser("install", help="Copy block HTML and minimal CSS")
    addition.add_argument("blocks", nargs="+", help="Block IDs from 'list'")
    addition.add_argument("--output", required=True, type=Path, help="Target project root")
    addition.add_argument("--dry-run", action="store_true", help="Show changes without writing")
    args = parser.parse_args(argv)
    try:
        document = load_catalog()
        if args.command == "list":
            list_blocks(document, args.category, args.json)
        else:
            install(document, args.blocks, args.output, args.dry_run)
        return 0
    except (BlockInstallError, OSError, json.JSONDecodeError) as error:
        print(f"Syntyr blocks: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
