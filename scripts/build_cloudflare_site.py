"""Build an explicit public-only SYNTYR site for Cloudflare Workers Static Assets.

Pure stdlib, no Node dependencies, no browser JavaScript, no repo-root publishing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile

if __package__:
    from .build import distributions
else:
    from build import distributions

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / ".cloudflare-public"
MARKER = ".syntyr-site-manifest.json"

HEADERS = """/*
  X-Content-Type-Options: nosniff
  Referrer-Policy: strict-origin-when-cross-origin

/
  Cache-Control: public, max-age=0, must-revalidate

/*.html
  Cache-Control: public, max-age=0, must-revalidate

/docs/*
  Cache-Control: public, max-age=0, must-revalidate

/examples/*
  Cache-Control: public, max-age=0, must-revalidate

/dist/*
  Cache-Control: public, max-age=0, must-revalidate
  Access-Control-Allow-Origin: *

/v/*
  Cache-Control: public, max-age=31536000, immutable
  Access-Control-Allow-Origin: *
"""


def source_files() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    paths = [
        ROOT / "index.html",
        ROOT / "404.html",
        ROOT / "LICENSE",
        ROOT / "README.md",
        ROOT / "ARCHITECTURE.md",
        ROOT / "terminal/palettes.json",
        ROOT / "integrations/vertigo/admin.css",
        ROOT / "examples/ansi_cli.py",
    ]
    # Explicit per-file allowlist: new repo files are private until reviewed.
    public_docs = (
        "accessibility.md", "accessibility-alpha5-review.md", "api-stability.md", "cloudflare-hosting.md", "components.md",
        "console-kit.html", "design-research-linear-resend.md",
        "distribution.md", "docs.css", "framework-integrations.md",
        "geometry-terminal.md", "motion.md", "performance-and-polish.md",
        "performance-validation.md", "progressive-enhancement.md",
        "index.html", "recipes.md", "saas-cli-business.md",
        "site-generator-decision.md", "tailwind-research.md",
        "theme-customization.md", "theme-editor.html", "theme-editor.js", "symbols.md",
        "vertigo-integration.md",
    )
    public_examples = (
        "business.html", "console.html", "geometry-terminal.html", "landing.html",
        "minimalist-patterns.html", "design-states.html", "motion.html",
        "operations-console.css", "operations-console.html", "pricing.html",
        "resources.html", "saas.html", "saas-workflows.html", "saas-workflows.css",
        "terminal.html", "themes.html", "vertigo-admin.html", "symbols.html",
    )
    # Import the canonical distribution registry rather than maintaining
    # a second list that can silently omit new CSS entrypoints.
    public_css = tuple(distributions())
    paths.extend(ROOT / "docs" / name for name in public_docs)
    paths.extend(ROOT / "examples" / name for name in public_examples)
    paths.extend(ROOT / "dist" / name for name in public_css)
    for path in paths:
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(ROOT):
            raise ValueError(f"Not a regular repo file: {path}")
        files[path.relative_to(ROOT).as_posix()] = path.read_bytes()

    releases = ROOT / "site-releases"
    manifest = json.loads((releases / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Invalid release manifest")
    for version, assets in manifest.items():
        if not version or "/" in version or version in {".", ".."} or not isinstance(assets, dict):
            raise ValueError(f"Invalid release version: {version!r}")
        for filename, expected_hash in assets.items():
            relative = PurePosixPath(filename)
            if (relative.is_absolute() or ".." in relative.parts
                    or not filename.startswith("syntyr") or relative.suffix != ".css"
                    or len(relative.parts) != 1):
                raise ValueError(f"Invalid release filename: {filename!r}")
            path = releases / version / filename
            if path.is_symlink() or not path.is_file():
                raise ValueError(f"Missing immutable release asset: {path}")
            data = path.read_bytes()
            if hashlib.sha256(data).hexdigest() != expected_hash:
                raise ValueError(f"Modified immutable release asset: {path}")
            files[f"v/{version}/{filename}"] = data

    files["_headers"] = HEADERS.encode("utf-8")
    return files


def build(out: Path, check: bool) -> int:
    out = out.resolve()
    if out == ROOT or out in ROOT.parents:
        raise ValueError("Refusing to publish into the source root or its parents")
    files = source_files()
    index = {path: hashlib.sha256(data).hexdigest() for path, data in sorted(files.items())}
    files[MARKER] = (json.dumps(index, indent=2, sort_keys=True) + "\n").encode("utf-8")
    if check:
        existing = {p.relative_to(out).as_posix(): p.read_bytes()
                    for p in out.rglob("*") if p.is_file()} if out.is_dir() else {}
        if existing != files:
            print("STALE Cloudflare publish directory", file=sys.stderr)
            return 1
        print(f"OK Cloudflare publish directory: {len(files)} allowlisted files")
        return 0
    if out.exists():
        if out.is_symlink() or not (out / MARKER).is_file():
            raise ValueError(f"Refusing to overwrite a non-SYNTYR output directory: {out}")
        shutil.rmtree(out)
    out.mkdir(parents=True)
    for relative, data in files.items():
        destination = out / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(data)
    print(f"BUILT Cloudflare static site: {len(files)} files at {out}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    return build(args.output, args.check)


if __name__ == "__main__":
    sys.exit(main())
