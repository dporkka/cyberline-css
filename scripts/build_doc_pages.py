"""Generate human-readable static HTML from approved Markdown documentation.

Authoritative docs stay in Markdown for AI tools and repository contributors.
The generated HTML is committed for dependency-free, static hosting.
Maintainer-only dependency: python3 -m pip install -r requirements-docs.txt
"""
from __future__ import annotations

import argparse
from hashlib import sha256
from html import escape
from pathlib import Path
import re
from urllib.parse import urlsplit, urlunsplit

try:
    from markdown_it import MarkdownIt
except ImportError as error:
    raise SystemExit("Install the docs authoring dependency: python3 -m pip install -r requirements-docs.txt") from error

if __package__:
    from .build_cloudflare_site import ROOT, PUBLIC_DOCS
else:
    from build_cloudflare_site import ROOT, PUBLIC_DOCS

SITE = "https://syntyr-css.pages.dev"
GUIDES = tuple(name for name in PUBLIC_DOCS if name.endswith(".md"))
SECTIONS = (
    ("Start here", ("ai-quickstart", "distribution", "package-managers", "from-pico",
                    "adoption-starters", "components", "data-tables", "data-grid",
                    "recipes", "native-patterns", "component-recipes")),
    ("Design system", ("design-principles", "theme-customization", "visual-intensity", "geometry-terminal", "symbols", "viz", "blocks-guide", "premium-compositions", "component-authoring")),
    ("Integrations", ("framework-integrations", "interaction-recipes", "headless-interactions", "lit-integration", "radix-integration", "shadcn-integration", "ecosystem-integrations", "editor-integration", "figma-component-kit", "vertigo-integration", "rust-saas-integration", "saas-cli-business")),
    ("Accessibility and performance", ("accessibility", "accessibility-alpha5-review", "progressive-enhancement", "native-browser-apis", "progressive-loading", "performance-and-polish", "performance-validation", "live-performance-audit", "visual-regression")),
    ("Maintainer and reference", ("agent-integration", "api-stability", "cloudflare-hosting", "site-generator-decision", "design-research-linear-resend", "tailwind-research", "selective-builds", "release-readiness-ecosystem")),
)


def title_of(source: str) -> str:
    for line in source.splitlines():
        if line.startswith("# "):
            return re.sub(r"[`*_]", "", line[2:]).strip()
    raise ValueError("Guide is missing a first-level heading")


def slugify(label: str) -> str:
    slug = re.sub(r"[^\w -]", "", label.lower(), flags=re.UNICODE)
    return re.sub(r"[\s_]+", "-", slug).strip("-") or "section"


def renderer() -> MarkdownIt:
    md = MarkdownIt("default", {"html": False, "linkify": False}).enable("table")
    return md


DESCRIPTION_OVERRIDES = {
    "design-principles.md": "Learn shared UI design principles, accessible component states, semantic HTML compositions, and static palette contrast checks in Syntyr CSS.",
    "ai-quickstart.md": "Install Syntyr CSS with AI coding agents using semantic HTML, real component classes, and version-aware, framework-neutral examples.",
    "components.md": "Reference Syntyr CSS components, class names, design tokens, scopes, and semantic HTML patterns for lightweight application interfaces.",
    "framework-integrations.md": "Integrate Syntyr CSS with server-rendered HTML, HTMX, LiveView, Livewire, and frontend frameworks without requiring client-side JavaScript.",
    "from-pico.md": "Migrate from Pico CSS to Syntyr with semantic HTML, explicit component styling, theme tokens, and minimal runtime dependencies.",
    "distribution.md": "Install and self-host Syntyr CSS using versioned stylesheets, optional modules, and immutable releases for production websites.",
    "theme-customization.md": "Customize Syntyr CSS themes and design tokens for SaaS dashboards, accessible business applications, and futuristic interfaces.",
    "component-authoring.md": "Define semantic HTML, styling namespaces, theme scopes, and accessibility contracts for Syntyr-compatible application and Web Components.",
    "design-research-linear-resend.md": "Explore the design principles Syntyr adapts from Linear, Resend, and other developer tools without copying proprietary interfaces or assets.",
    "recipes.md": "Build MIT-licensed interface compositions with Syntyr CSS, including forms, layout flows, responsive sections, and SaaS presentation patterns.",
    "saas-cli-business.md": "Style SaaS dashboards, business websites, and CLI-inspired interfaces with Syntyr's framework-neutral Grid, Noir, and Studio themes.",
    "tailwind-research.md": "Compare Syntyr CSS with Tailwind CSS and Tailwind Plus: tokens, cascade layers, responsive components, build tooling, and licensing tradeoffs.",
    "visual-composition.md": "Explore Syntyr's principles for layout hierarchy, typography, surfaces, visual restraint, and original product-led SaaS interface design.",
    "visual-intensity.md": "Customize Syntyr's cyberpunk frames, decorative intensity, density, and palettes independently with CSS attributes and no runtime JavaScript.",
    "viz.md": "Style server-rendered charts with Syntyr Viz, an optional CSS-only module using theme-aware visualization tokens and native HTML.",
}


def description_of(name: str, tokens: list) -> str:
    if name in DESCRIPTION_OVERRIDES:
        return DESCRIPTION_OVERRIDES[name]
    for index, token in enumerate(tokens[:-1]):
        if token.type != "paragraph_open" or tokens[index + 1].type != "inline":
            continue
        inline = tokens[index + 1]
        summary = " ".join(
            child.content for child in inline.children or []
            if child.type in {"text", "code_inline"} and child.content.strip()
        )
        summary = re.sub(r"\s+", " ", summary).strip()
        if len(summary) >= 70:
            if len(summary) > 158:
                summary = summary[:155].rsplit(" ", 1)[0].rstrip(" .,;:") + "…"
            return summary
    title = title_of((ROOT / "docs" / name).read_text(encoding="utf-8"))
    return f"Explore {title} in Syntyr CSS with practical guidance, semantic HTML examples, and integration notes for developers."


def render_guide(name: str, allowed: set[str]) -> str:
    source = (ROOT / "docs" / name).read_text(encoding="utf-8")
    title = title_of(source)
    slug = name.removesuffix(".md")
    digest = sha256(source.encode("utf-8")).hexdigest()
    tokens = renderer().parse(source)
    description = description_of(name, tokens)
    used: set[str] = set()
    headings: list[tuple[int, str, str]] = []
    for index, token in enumerate(tokens):
        if token.type == "heading_open":
            inline = tokens[index + 1]
            label = "".join(child.content for child in inline.children or []
                            if child.type in {"text", "code_inline", "html_inline"}) or inline.content
            base = slugify(label)
            anchor = base
            i = 2
            while anchor in used:
                anchor = f"{base}-{i}"
                i += 1
            used.add(anchor)
            token.attrSet("id", anchor)
            if token.tag in {"h2", "h3"}:
                headings.append((int(token.tag[1]), anchor, label))
        if token.type != "inline":
            continue
        for child in token.children or []:
            if child.type != "link_open":
                continue
            link = child.attrGet("href") or ""
            parsed = urlsplit(link)
            if parsed.scheme or parsed.netloc or parsed.path.startswith("/") or not parsed.path.endswith(".md"):
                continue
            if parsed.path in allowed:
                child.attrSet("href", urlunsplit(("", "", parsed.path.removesuffix(".md") + ".html", parsed.query, parsed.fragment)))
                continue
            # Other repository Markdown is not approved for site publication.
            # Link to the public GitHub source instead of a broken site URL.
            target = (ROOT / "docs" / parsed.path).resolve()
            if target.is_relative_to(ROOT) and target.is_file() and target.suffix == ".md":
                repo_path = target.relative_to(ROOT).as_posix()
                child.attrSet("href", urlunsplit(("https", "github.com", f"/dporkka/syntyr-css/blob/main/{repo_path}", parsed.query, parsed.fragment)))

    article = renderer().renderer.render(tokens, renderer().options, {})
    toc = "\n".join(
        f'<a class="docs-article-toc-link docs-article-toc-{level}" href="#{escape(anchor)}">{escape(label)}</a>'
        for level, anchor, label in headings
    )
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="{escape(description, quote=True)}">
  <meta name="syntyr-source-sha256" content="{digest}">
  <meta name="theme-color" content="#f5f7fb">
  <title>{escape(title)} — Syntyr CSS docs</title>
  <link rel="canonical" href="{SITE}/docs/{slug}">
  <link rel="alternate" type="text/markdown" href="{name}" title="Markdown source">
  <link rel="icon" href="../assets/syntyr-mark.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../dist/syntyr.core.css">
  <link rel="stylesheet" href="docs.css">
</head>
<body class="syn-root syn-page" data-syn-theme="studio">
  <a class="syn-button docs-skip" href="#doc-main">Skip to guide</a>
  <div class="syn-shell">
    <header class="syn-header docs-header">
      <a class="syn-logo" href="../index.html">SYNTYR / CSS</a>
      <nav class="syn-nav" aria-label="Documentation navigation">
        <a href="index.html">Overview</a><a href="catalog.html">Components</a><a href="guides.html">Guides</a><a href="reference.html">All docs</a>
      </nav>
      <details class="site-mobile-menu"><summary>Menu</summary><nav aria-label="Mobile navigation">
        <a href="index.html">Overview</a><a href="catalog.html">Components</a><a href="guides.html">Guides</a><a href="reference.html">All docs</a>
      </nav></details>
    </header>
    <main id="doc-main" class="docs-article-page">
      <nav class="syn-breadcrumbs" aria-label="Breadcrumb"><ol><li><a href="../index.html">Home</a></li><li><a href="reference.html">Documentation</a></li><li aria-current="page">{escape(title)}</li></ol></nav>
      <header class="docs-article-heading">
        <p class="syn-eyebrow">SYNTYR / DOCUMENTATION</p>
        <p class="syn-muted">Current source documentation may describe unreleased alpha.5 features. <a href="distribution.html">Check released version compatibility.</a></p>
        <p class="syn-caption">Prefer a machine-readable version? <a href="{name}">Markdown source</a> · <a href="../llms.txt">LLM index</a></p>
      </header>
      <div class="docs-article-layout">
        <article class="docs-prose" aria-label="{escape(title, quote=True)}">
{article}        </article>
        <aside class="docs-article-sidebar"><nav aria-label="On this page"><p class="syn-eyebrow">ON THIS PAGE</p>
{toc}
        </nav></aside>
      </div>
      <nav class="docs-guide-links" aria-label="More documentation"><a href="reference.html">All documentation</a><a href="guides.html">Practical guides</a><a href="{name}">Markdown source</a></nav>
    </main>
    <footer class="syn-header"><span class="syn-caption">SYNTYR CSS · MIT CORE · EXPERIMENTAL</span><a href="../index.html">Home</a></footer>
  </div>
</body>
</html>
'''


def render_directory(guides: dict[str, str]) -> str:
    listed: set[str] = set()
    sections = []
    for section, stems in SECTIONS:
        items = []
        for stem in stems:
            filename = stem + ".md"
            if filename in guides:
                items.append(f'<li><a href="{stem}.html">{escape(guides[filename])}</a></li>')
                listed.add(filename)
        if items:
            sections.append(f'<section class="docs-reference-group"><h2>{escape(section)}</h2><ul>{"".join(items)}</ul></section>')
    remaining = sorted(set(guides) - listed)
    if remaining:
        sections.append('<section class="docs-reference-group"><h2>More guides</h2><ul>' + ''.join(
            f'<li><a href="{name.removesuffix(".md")}.html">{escape(guides[name])}</a></li>' for name in remaining
        ) + '</ul></section>')
    content = '\n'.join(sections)
    return f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Browse all Syntyr CSS guides in readable HTML, from installation and components to integrations, design tokens, accessibility, and performance.">
  <meta name="theme-color" content="#f5f7fb"><title>All documentation — Syntyr CSS</title>
  <link rel="canonical" href="{SITE}/docs/reference">
  <link rel="icon" href="../assets/syntyr-mark.svg" type="image/svg+xml">
  <link rel="stylesheet" href="../dist/syntyr.core.css"><link rel="stylesheet" href="docs.css">
</head>
<body class="syn-root syn-page" data-syn-theme="studio">
  <a class="syn-button docs-skip" href="#doc-main">Skip to documentation index</a>
  <div class="syn-shell">
    <header class="syn-header docs-header"><a class="syn-logo" href="../index.html">SYNTYR / CSS</a>
      <nav class="syn-nav" aria-label="Documentation navigation"><a href="index.html">Overview</a><a href="catalog.html">Components</a><a href="guides.html">Guides</a><a aria-current="page" href="reference.html">All docs</a></nav>
      <details class="site-mobile-menu"><summary>Menu</summary><nav aria-label="Mobile navigation"><a href="index.html">Overview</a><a href="catalog.html">Components</a><a href="guides.html">Guides</a><a aria-current="page" href="reference.html">All docs</a></nav></details>
    </header>
    <main id="doc-main"><section class="docs-guide-hero">
      <p class="syn-eyebrow">DOCUMENTATION / HUMAN-READABLE</p><h1 class="docs-guide-title">All Syntyr guides.</h1>
      <p class="syn-lede">Browse complete HTML guides with headings, code samples and tables. Markdown is still available for AI agents and source editing.</p>
      <p><a href="guides.html">Start with practical walkthroughs</a> · <a href="../llms.txt">Machine-readable documentation index</a></p>
    </section>
    <div class="docs-reference-grid">{content}</div></main>
    <footer class="syn-header"><span class="syn-caption">SYNTYR CSS · MIT CORE · EXPERIMENTAL</span><a href="../index.html">Home</a></footer>
  </div>
</body>
</html>
'''


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify generated pages were committed")
    args = parser.parse_args()
    titles = {name: title_of((ROOT / "docs" / name).read_text(encoding="utf-8")) for name in GUIDES}
    targets = {ROOT / "docs" / (name.removesuffix(".md") + ".html"): render_guide(name, set(GUIDES)) for name in GUIDES}
    targets[ROOT / "docs/reference.html"] = render_directory(titles)
    stale = [p for p, html in targets.items() if not p.is_file() or p.read_text(encoding="utf-8") != html]
    if args.check:
        if stale:
            print("Stale generated documentation: " + ", ".join(p.name for p in stale))
            return 1
        print(f"OK {len(targets)} generated HTML documentation pages")
        return 0
    for path, html in targets.items():
        path.write_text(html, encoding="utf-8")
    print(f"Generated {len(targets)} human-readable HTML documentation pages")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
