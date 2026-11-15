"""Build an explicit public-only SYNTYR site for Cloudflare Workers Static Assets.

Pure stdlib, no Node dependencies, no browser JavaScript, no repo-root publishing.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import posixpath
import re
from urllib.parse import urlsplit
from pathlib import Path, PurePosixPath
import shutil
import sys
import tempfile

if __package__:
    from .build import all_distributions
else:
    from build import all_distributions

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

/docs/*.md
  X-Robots-Tag: noindex
  Content-Type: text/markdown; charset=utf-8

/README.md
  X-Robots-Tag: noindex
  Content-Type: text/markdown; charset=utf-8

/ARCHITECTURE.md
  X-Robots-Tag: noindex
  Content-Type: text/markdown; charset=utf-8

/agents/syntyr/SKILL.md
  X-Robots-Tag: noindex
  Content-Type: text/markdown; charset=utf-8

/examples/*
  Cache-Control: public, max-age=0, must-revalidate

/dist/*
  Cache-Control: public, max-age=0, must-revalidate
  Access-Control-Allow-Origin: *

/v/*
  Cache-Control: public, max-age=31536000, immutable
  Access-Control-Allow-Origin: *

/_assets/css/*
  Cache-Control: public, max-age=31536000, immutable
"""


LINK_TAG = re.compile(r"<link\b[^>]*>", re.IGNORECASE)
REL_ATTR = re.compile(r"""\brel\s*=\s*(['"])(.*?)\1""", re.IGNORECASE)
HREF_ATTR = re.compile(r"""\bhref\s*=\s*(['"])(.*?)\1""", re.IGNORECASE)


def immutable_site_css(files: dict[str, bytes]) -> None:
    """Rewrite only shipped HTML stylesheet references to content-hashed copies.

    Original /dist and /v assets remain intact for consumers. The site HTML
    references an immutable hashed copy of each linked local stylesheet.
    Other source links, external URLs, JS, and Markdown examples are unchanged.
    """
    derived: dict[str, bytes] = {}
    for filename, payload in tuple(files.items()):
        if not filename.endswith(".html"):
            continue
        def replace_link(match: re.Match) -> str:
            tag = match.group(0)
            rel = REL_ATTR.search(tag)
            href = HREF_ATTR.search(tag)
            if not rel or not href or "stylesheet" not in rel.group(2).lower().split():
                return tag
            parsed = urlsplit(href.group(2))
            if parsed.scheme or parsed.netloc or parsed.query or parsed.fragment:
                return tag
            # The HTML may be at the site root or in an examples/docs folder.
            path = posixpath.normpath(
                posixpath.join(posixpath.dirname(filename), parsed.path.lstrip("/"))
                if not parsed.path.startswith("/")
                else parsed.path.lstrip("/"))
            if path not in files or not path.endswith(".css"):
                return tag
            css = files[path]
            if re.search(rb"@import\b|url\s*\(", css, re.IGNORECASE):
                raise ValueError(f"Cannot relocate CSS with imports/relative URLs: {path}")
            dest = f"_assets/css/{hashlib.sha256(css).hexdigest()}.css"
            existing = derived.get(dest)
            if existing is not None and existing != css:
                raise ValueError(f"Hash collision: {dest}")
            derived[dest] = css
            return tag[:href.start(2)] + "/" + dest + tag[href.end(2):]

        html = payload.decode("utf-8")
        rewritten = LINK_TAG.sub(replace_link, html)
        files[filename] = rewritten.encode("utf-8")
    files.update(derived)


PUBLIC_DOCS = (
    "ai-quickstart.md", "agent-integration.md",
    "accessibility.md", "accessibility-alpha5-review.md", "api-stability.md", "cloudflare-hosting.md", "component-authoring.md", "components.md",
    "console-kit.html", "component-recipes.md", "design-research-linear-resend.md", "premium-compositions.md", "visual-composition.md",
    "distribution.md", "native-patterns.md", "from-pico.md", "package-managers.md", "docs.css", "guides.html", "catalog.html", "catalog.css", "catalog.js",
    "blocks.html", "blocks.css", "blocks.js", "blocks-assets.css", "blocks-guide.md", "framework-integrations.md",
    "geometry-terminal.md", "native-browser-apis.md", "radix-integration.md", "visual-intensity.md", "performance-and-polish.md",
    "performance-validation.md", "progressive-enhancement.md", "progressive-loading.md", "live-performance-audit.md",
    "index.html", "lit-integration.md", "playground.html", "playground.css", "playground.js",
    "editor-integration.md", "recipes.md", "saas-cli-business.md",
    "site-generator-decision.md", "tailwind-research.md",
    "theme-customization.md", "design-assets.md", "theme-editor.html", "theme-editor.js", "symbols.md",
    "vertigo-integration.md", "viz.md",
)


def source_files() -> dict[str, bytes]:
    files: dict[str, bytes] = {}
    paths = [
        ROOT / "index.html",
        ROOT / "assets/syntyr-mark.svg",
        ROOT / "assets/og-syntyr.png",
        ROOT / "404.html",
        ROOT / "LICENSE",
        ROOT / "README.md",
        ROOT / "ARCHITECTURE.md",
        ROOT / "THIRD_PARTY_NOTICES.md",
        ROOT / "metadata/design-assets.json",
        ROOT / "llms.txt",
        ROOT / "llms-full.txt",
        ROOT / "metadata/components.json",
        ROOT / "agents/syntyr/SKILL.md",
        ROOT / "terminal/palettes.json",
        *(
            ROOT / "metadata" / name
            for name in (
                "syntyr-api.json", "syntyr.html-custom-data.json",
                "syntyr.css-custom-data.json", "syntyr.code-snippets",
            )
        ),
        ROOT / "integrations/vertigo/admin.css",
        ROOT / "integrations/radix/states.css",
        ROOT / "examples/ansi_cli.py",
    ]
    # Explicit per-file allowlist: new repo files are private until reviewed.

    public_examples = (
        "business.html", "console.html", "form-composition.html", "geometry-terminal.html", "intensity-geometry.html", "landing.html", "semantic-starter.html",
        "minimalist-patterns.html", "design-states.html", "native-elements.html", "native-recipes.html", "native-apis.html", "performance-first.html",
        "operations-console.css", "operations-console.html", "pricing.html",
        "flagship.css", "flagship-studio.html", "flagship-noir.html", "flagship-grid.html",
        "resources.html", "design-assets.html", "saas.html", "saas-workflows.html", "crm.html", "saas-workflows.css", "premium-compositions.html",
        "terminal.html", "themes.html", "vertigo-admin.html", "symbols.html",
        "viz.html",
    )
    # Import the canonical distribution registry rather than maintaining
    # a second list that can silently omit new CSS entrypoints.
    public_css = tuple(all_distributions())
    paths.extend(ROOT / "docs" / name for name in PUBLIC_DOCS)
    paths.extend(ROOT / "docs" / (name.removesuffix(".md") + ".html")
                 for name in PUBLIC_DOCS if name.endswith(".md"))
    paths.append(ROOT / "docs/reference.html")
    # Only approved raster captures from the privately authored Console Kit.
    # Never publish premium HTML, CSS, build output, or other private assets.
    public_preview_images = (
        "studio-overview.webp",
        "grid-resources.webp",
        "noir-billing.webp",
    )
    paths.extend(ROOT / "docs/previews" / name for name in public_preview_images)
    paths.extend(ROOT / "examples" / name for name in public_examples)
    paths.extend(ROOT / "dist" / name for name in public_css)
    # Curated originals only; each SVG is from the audited gallery source.
    if __package__:
        from .export_icons import icon_paths
    else:
        from export_icons import icon_paths
    paths.extend(ROOT / name for name in icon_paths())
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

    # Index HTML for people. Keep public Markdown fetchable by agents but
    # exclude it from human-facing search results and the HTML sitemap.
    from xml.sax.saxutils import escape as escape_xml
    pages = sorted(name for name in files if name.endswith(".html"))
    addresses = ["/"] + ["/" + name for name in pages if name != "index.html"]
    files["sitemap.xml"] = ("<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
                            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
                            + "".join(f"  <url><loc>{escape_xml('https://syntyr-css.pages.dev' + url)}</loc></url>\n"
                                      for url in addresses)
                            + "</urlset>\n").encode("utf-8")
    files["robots.txt"] = b"User-agent: *\nAllow: /\n\nSitemap: https://syntyr-css.pages.dev/sitemap.xml\n"
    immutable_site_css(files)
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
