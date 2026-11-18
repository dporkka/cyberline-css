"""Compose four static MIT website examples from the canonical free block snippets."""
from __future__ import annotations

import argparse
from html import escape
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
PAGES = {
    "business": ("A professional website", (
        "site-header", "services-grid", "process-steps", "portfolio-grid",
        "contact-quote", "site-footer")),
    "journal": ("An editorial website", (
        "site-header", "article-featured", "article-grid",
        "newsletter-signup", "site-footer")),
    "article": ("A long-form article", (
        "site-header", "article-detail", "author-profile",
        "article-grid", "site-footer")),
    "services": ("A service business page", (
        "site-header", "services-grid", "service-areas",
        "case-study-preview", "contact-quote", "site-footer")),
}

def render(name: str) -> str:
    title, section_ids = PAGES[name]
    sections = [(ROOT / "blocks/snippets" / (ident + ".html")).read_text(encoding="utf-8").strip()
                for ident in section_ids]
    header, footer = sections[0], sections[-1]
    body = "\n".join(sections[1:-1])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Free, scriptless Syntyr website starter composed of native HTML blocks.">
  <meta name="robots" content="noindex,follow">
  <title>{escape(title)} — Syntyr example</title>
  <link rel="stylesheet" href="../dist/syntyr.all.css">
</head>
<body class="syn-root syn-page" data-syn-theme="studio">
  <a class="syn-button" href="#content">Skip to content</a>
  {header}
  <main id="content" class="syn-shell">
    <h1 class="syn-title">{escape(title)}</h1>
    <p class="syn-caption">Illustrative site starter. Replace every route, form action, product and brand detail before publishing.</p>
{body}
  </main>
  {footer}
</body>
</html>
"""

def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    changed = []
    for name in PAGES:
        output = ROOT / "examples" / ("site-starter-" + name + ".html")
        content = render(name)
        if args.check:
            if not output.is_file() or output.read_text(encoding="utf-8") != content:
                changed.append(output.name)
        else:
            output.write_text(content, encoding="utf-8")
            changed.append(output.name)
    if args.check:
        if changed:
            print("STALE site starter pages: " + ", ".join(changed), file=sys.stderr)
            return 1
        print("OK four deterministic site starters")
        return 0
    print("WROTE " + ", ".join(changed))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
