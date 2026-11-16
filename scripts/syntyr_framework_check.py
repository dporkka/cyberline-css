"""Advisory checks of literal JSX/Vue/Svelte opening tags.

Not a framework parser: source and dynamic expressions are never certified as
validated. Return useful selector diagnostics while the caller reports the file
as unchecked (exit 2 when no errors). No JS execution or network dependencies.
"""
from __future__ import annotations

import re
from scripts.syntyr_check import validate_html

_OPEN_TAG = re.compile(r'<([A-Za-z][\w:.-]*)(?=[\s/>])')


def _skip_quoted(source: str, pos: int) -> int:
    quote = source[pos]
    pos += 1
    while pos < len(source):
        if source[pos] == '\\':
            pos += 2
        elif source[pos] == quote:
            return pos + 1
        else:
            pos += 1
    return len(source)


def _skip_expression(source: str, pos: int) -> int:
    depth = 1
    pos += 1
    while pos < len(source) and depth:
        if source[pos] in "'\"`":
            pos = _skip_quoted(source, pos)
        elif source.startswith('/*', pos):
            end = source.find('*/', pos + 2)
            pos = len(source) if end == -1 else end + 2
        elif source.startswith('//', pos):
            end = source.find('\n', pos + 2)
            pos = len(source) if end == -1 else end
        elif source[pos] == '{':
            depth += 1
            pos += 1
        elif source[pos] == '}':
            depth -= 1
            pos += 1
        else:
            pos += 1
    return pos


def literal_opening_tags(source: str):
    """Yield possible markup start positions and tags, never executing code."""
    pos = 0
    length = len(source)
    while pos < length:
        if source.startswith('<!--', pos):
            end = source.find('-->', pos + 4)
            pos = length if end < 0 else end + 3
            continue
        if source.startswith('//', pos):
            end = source.find('\n', pos + 2)
            pos = length if end < 0 else end
            continue
        if source.startswith('/*', pos):
            end = source.find('*/', pos + 2)
            pos = length if end < 0 else end + 2
            continue
        if source[pos] in "'\"`":
            pos = _skip_quoted(source, pos)
            continue
        match = _OPEN_TAG.match(source, pos) if source[pos] == '<' else None
        if match is None:
            pos += 1
            continue
        tagname = match.group(1).lower()
        start = pos
        pos = match.end()
        while pos < length:
            if source[pos] in "'\"`":
                pos = _skip_quoted(source, pos)
            elif source[pos] == '{':
                pos = _skip_expression(source, pos)
            elif source[pos] == '>':
                pos += 1
                break
            else:
                pos += 1
        tag = source[start:pos]
        if not tag.endswith('>'):
            break
        if tagname in ('script', 'style'):
            closing = re.search(r'</\s*' + tagname + r'\s*>', source[pos:], re.I)
            pos = length if not closing else pos + closing.end()
            continue
        yield start, tag


def check_literal_framework_markup(source: str, contract: dict, stylesheets: set[str]) -> list[dict]:
    """Conservative literal class/attribute checks with source-mapped diagnostics.

    Every framework file remains incomplete regardless of the result: dynamic
    bindings, JSX expression trees and actual framework semantics aren't parsed.
    """
    findings = []
    for offset, opening in literal_opening_tags(source):
        line = source.count('\n', 0, offset) + 1
        column = offset - source.rfind('\n', 0, offset)
        for item in validate_html(opening, contract, stylesheets=stylesheets):
            original = item['line']
            findings.append({**item, 'line': line + original - 1,
                             'column': column + item['column'] - 1 if original == 1 else item['column']})
    return sorted(findings, key=lambda item: (item['line'], item['column'], item['code']))
