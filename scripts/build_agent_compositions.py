"""Build copy-owned, AI-friendly multi-block examples from the existing registry.

No new CSS, runtime, generator dependency or framework is required by consumers.
Generated pages are illustrative: applications must wire routes, state and data.
"""
from __future__ import annotations

import argparse
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / 'examples'
SRC = ROOT / 'blocks' / 'snippets'
THEMES = {'studio', 'grid', 'noir', 'industrial', 'terminal', 'corporate', 'minimal'}
SOURCE_ROOT = re.compile(r'^<section class="syn-root syn-region" data-syn-theme="studio"')


class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.duplicates = set()
        self.references = set()
        self.script_count = 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get('id'):
            ident = attributes['id']
            if ident in self.ids:
                self.duplicates.add(ident)
            self.ids.add(ident)
        for key in ('aria-labelledby', 'aria-describedby'):
            self.references.update((attributes.get(key) or '').split())
        if attributes.get('for'):
            self.references.add(attributes['for'])
        if tag == 'script':
            self.script_count += 1


def render(recipe: dict, blocks: dict) -> str:
    ident = recipe['id']
    if not re.fullmatch('[a-z][a-z0-9-]*', ident):
        raise ValueError(f'Unsafe composition id: {ident!r}')
    theme = recipe['theme']
    if theme not in THEMES:
        raise ValueError(f'Unsupported theme: {theme!r}')
    names = recipe['blocks']
    if len(names) < 3 or len(names) != len(set(names)):
        raise ValueError(f'{ident}: expected at least three unique blocks')
    modules = {'core'}
    fragments = []
    for block_id in names:
        if block_id not in blocks:
            raise ValueError(f'{ident}: unknown block {block_id!r}')
        if not re.fullmatch('[a-z][a-z0-9-]*', block_id):
            raise ValueError(f'{ident}: invalid block path {block_id!r}')
        modules.update(blocks[block_id]['modules'])
        source = (SRC / f'{block_id}.html').read_text(encoding='utf-8').strip()
        # Each gallery block has its own Syntyr root for independent copying.
        # In a page composition, the outer page root owns the theme so the
        # same markup can be recomposed under any single selected palette.
        fragment, replacements = SOURCE_ROOT.subn('<section class="syn-region"', source, count=1)
        if replacements != 1:
            raise ValueError(f'{ident}: unexpected source root in {block_id}')
        fragments.append(f'    <!-- Existing MIT block: {block_id} -->\n' +
                         '\n'.join('    ' + line for line in fragment.splitlines()))
    if not modules <= {'core', 'recipes', 'effects', 'geometry', 'semantic', 'utilities', 'viz', 'symbols', 'print'}:
        raise ValueError(f'{ident}: unexpected CSS modules: {modules}')
    styles = '\n'.join(f'  <link rel="stylesheet" href="../dist/syntyr.{module}.css">'
                       for module in sorted(modules, key=lambda m: (m != 'core', m)))
    title = escape(recipe['title'])
    description = escape(recipe['description'])
    html = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <meta name="description" content="{description} Copy-owned Syntyr page composition.">
  <title>{title} — Syntyr CSS</title>
{styles}
</head>
<body class="syn-root syn-page" data-syn-theme="{theme}">
  <a href="#main" class="syn-button">Skip to content</a>
  <header class="syn-header syn-shell">
    <a class="syn-logo" href="../docs/blocks.html">SYNTYR / COMPOSITIONS</a>
    <nav class="syn-nav" aria-label="Composition navigation">
      <a href="../docs/playground.html">Design Lab</a>
      <a href="../docs/agent-integration.html">Agent guide</a>
    </nav>
  </header>
  <main id="main" class="syn-shell syn-stack">
    <header class="syn-region">
      <span class="syn-eyebrow">ILLUSTRATIVE / COPY-OWNED HTML</span>
      <h1 class="syn-title">{title}</h1>
      <p class="syn-lede">{description}</p>
    </header>
{chr(10).join(fragments)}
    <p class="syn-caption">Static example data, pricing and routes. Supply real data and server handlers in your application; Syntyr does not implement business logic.</p>
  </main>
</body>
</html>
'''
    structure = Structure(); structure.feed(html)
    if structure.script_count or structure.duplicates or structure.references - structure.ids:
        raise ValueError(f'{ident}: invalid composed markup: duplicate ids={structure.duplicates}, missing references={structure.references - structure.ids}')
    return html


def generate(*, check: bool) -> int:
    data = json.loads((ROOT / 'metadata/agent-compositions.json').read_text(encoding='utf-8'))
    if data.get('version') != 1:
        raise ValueError('Unsupported compositions manifest version')
    blocks = {item['id']: item for item in json.loads((ROOT / 'blocks/manifest.json').read_text(encoding='utf-8'))['blocks']}
    names = set()
    stale = []
    for recipe in data['recipes']:
        if recipe['id'] in names:
            raise ValueError(f"Duplicate composition: {recipe['id']}")
        names.add(recipe['id'])
        page = TARGET / f"composition-{recipe['id']}.html"
        content = render(recipe, blocks)
        if check:
            if not page.is_file() or page.read_text(encoding='utf-8') != content:
                stale.append(str(page.relative_to(ROOT)))
        else:
            page.write_text(content, encoding='utf-8')
            print(f'Generated {page.relative_to(ROOT)}')
    if stale:
        print('Stale compositions: ' + ', '.join(stale), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    try:
        sys.exit(generate(check=args.check))
    except (OSError, ValueError, KeyError) as error:
        print(f'Composition build: {error}', file=sys.stderr)
        sys.exit(2)
