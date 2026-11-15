"""Export Syntyr editor metadata from CSS sources with no external dependencies.

Generated files are committed and supported by any editor able to consume
HTML/CSS custom-data JSON or VS Code workspace snippets.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys

if __package__:
    from .build import all_distributions, distributions
else:
    from build import all_distributions, distributions

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "src"
OUTPUT = ROOT / "metadata"
CSS_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
CLASS = re.compile(r"(?<!-)\.(syn-[a-zA-Z0-9_-]+)\b")
TOKEN = re.compile(r"(?<![\w-])(--syn-[a-zA-Z0-9_-]+)\s*:")
THEME = re.compile(r'data-syn-theme="([^"]+)"')

CLASS_DOCS = {
    "syn-root": "Required style scope for Syntyr components and themes.",
    "syn-panel": "General-purpose surface; customize via --syn-panel-* properties.",
    "syn-frame--accent": "Optional 2px accent outline for a selected frame shape.",
    "syn-frame--step": "Optional square-stepped top-right and bottom-left frame.",
    "syn-frame--facet": "Optional diagonal top-left and bottom-right facets.",
    "syn-glow": "Opt-in themed shadow; decoration controlled by data-syn-intensity.",
    "syn-button": "Native button or link styling; use semantic HTML.",
    "syn-button--primary": "Primary action appearance.",
    "syn-region": "Container query boundary for responsive compositions.",
    "syn-filter-bar": "Optional wrapping CRM GET filter form; host applies query parameters.",
    "syn-work-queue": "CSS-only prioritized work list; host owns ordering and actions.",
    "syn-work-item": "Work item with host-controlled data-syn-priority and overdue state.",
    "syn-data-grid-scroll": "Keyboard-focusable horizontal scroll region for dense tables.",
    "syn-data-grid-table": "Native table styling with optional visual data-grid states.",
    "syn-data-grid-cell": "Presentational cell states; host owns grid interactions.",
    "syn-filter-field": "Label and control group in an optional CRM filter bar.",
    "syn-filter-actions": "Wrapping submit and reset action group for CRM filters.",
    "syn-pipeline": "Keyboard-focusable scrollable CRM stage layout; host manages state.",
    "syn-pipeline-lane": "Named stage column with semantic list of records.",
    "syn-pipeline-card": "Opt-in CRM record presentation, not a drag-drop widget.",
    "syn-record-fields": "Responsive definition-list layout for key/value record details.",
    "syn-grid": "Responsive grid composition.",
    "syn-stats": "Container-responsive metric composition.",
    "syn-semantic": "Opt-in styling of native HTML elements.",
    "syn-u-flex": "Opt-in flexbox layout utility.",
    "syn-u-w-full": "Opt-in full-width utility.",
}
TOKEN_DOCS = {
    "--syn-accent": "Theme accent color; also check --syn-on-accent contrast.",
    "--syn-on-accent": "Foreground color for the primary accent.",
    "--syn-bg": "Theme background.",
    "--syn-text": "Default text color.",
    "--syn-grid-alpha": "Grid-line accent share; varies by scoped data-syn-intensity.",
    "--syn-glow-alpha": "Glow accent share; varies by scoped data-syn-intensity.",
    "--syn-wash-alpha": "Primary atmospheric wash share.",
    "--syn-wash-secondary-alpha": "Secondary atmospheric wash share.",
    "--syn-horizon-alpha": "Horizon line accent share.",
    "--syn-scanline-alpha": "Scanline overlay opacity percentage.",
    "--syn-panel-padding": "Per-panel padding; defaults to the existing fluid panel padding.",
    "--syn-panel-radius": "Per-panel border radius; defaults to square corners.",
    "--syn-panel-border-width": "Per-panel border width; defaults to 1px.",
    "--syn-button-padding-inline": "Per-button inline padding; defaults to 1rem.",
    "--syn-button-border-width": "Per-button border width; defaults to 1px.",
    "--syn-frame-cut": "Shared fallback corner size for optional geometry shapes.",
    "--syn-frame-cut-tl": "Optional top-left frame cut size.",
    "--syn-frame-cut-tr": "Optional top-right frame cut size.",
    "--syn-frame-cut-br": "Optional bottom-right frame cut size.",
    "--syn-frame-cut-bl": "Optional bottom-left frame cut size.",
    "--syn-frame-stroke": "Width of the optional shape-following border.",
    "--syn-frame-fill": "Interior fill paint for optional shaped frames.",
    "--syn-frame-outline": "Solid border paint fallback for optional frames.",
    "--syn-frame-border-paint": "Solid or gradient border paint for optional frames.",
    "--syn-frame-inlay-paint": "Optional translucent overlay on the inner shaped surface.",
}
# These overrides have CSS var() fallbacks, and are still valid documented API.
EXPLICIT_TOKENS = {
    "--syn-panel-padding": "components/layout.css",
    "--syn-panel-radius": "components/layout.css",
    "--syn-panel-border-width": "components/layout.css",
    "--syn-button-padding-inline": "components/buttons.css",
    "--syn-button-border-width": "components/buttons.css",
    "--syn-frame-cut": "geometry.css",
    "--syn-frame-cut-tl": "geometry.css",
    "--syn-frame-cut-tr": "geometry.css",
    "--syn-frame-cut-br": "geometry.css",
    "--syn-frame-cut-bl": "geometry.css",
    "--syn-frame-stroke": "geometry.css",
    "--syn-frame-fill": "geometry.css",
    "--syn-frame-outline": "geometry.css",
    "--syn-frame-border-paint": "geometry.css",
    "--syn-frame-inlay-paint": "geometry.css",
}
# Only permit literal, CSS-implemented presentation states. Curated choices
# must not omit states used by optional server or visualization stylesheets.
CSS_STATE = re.compile(r'\[\s*data-syn-state\s*=\s*["\']([^"\']+)["\']\s*\]')


def source_state_values() -> list[str]:
    values = set()
    for path in SOURCE.rglob("*.css"):
        values.update(CSS_STATE.findall(CSS_COMMENT.sub("", path.read_text(encoding="utf-8"))))
    return sorted(values)


SNIPPET_CLASSES = (
    "syn-root", "syn-panel", "syn-button", "syn-button--primary",
    "syn-region", "syn-grid", "syn-stats", "syn-form",
    "syn-input", "syn-semantic", "syn-u-flex", "syn-u-w-full",
)


def collect():
    classes = {}
    tokens = {}
    # Honor the public build manifest. Source ownership differs by API kind:
    # class definitions live in base/components/recipes, while primary theme
    # token declarations live in tokens.css (not their print-mode overrides).
    sources = list(dict.fromkeys(path for modules in distributions().values() for path in modules))
    css_by_module = {
        path: CSS_COMMENT.sub("", (SOURCE / path).read_text(encoding="utf-8"))
        for path in sources
    }
    class_sources = sorted(sources, key=lambda path: (path == "tokens.css", path == "print.css"))
    for path in class_sources:
        for name in CLASS.findall(css_by_module[path]):
            classes.setdefault(name, path)
    token_sources = sorted(sources, key=lambda path: (path != "tokens.css", path == "print.css"))
    for path in token_sources:
        for name in TOKEN.findall(css_by_module[path]):
            tokens.setdefault(name, path)
    for name, path in EXPLICIT_TOKENS.items():
        content = (SOURCE / path).read_text(encoding="utf-8")
        if "var(" + name not in content:
            raise ValueError(f"Declared public token is not referenced: {name}")
        tokens.setdefault(name, path)
    if not set(SNIPPET_CLASSES).issubset(classes):
        raise ValueError(f"Missing class from snippets: {set(SNIPPET_CLASSES) - set(classes)}")
    themes = sorted(set(THEME.findall((SOURCE / "tokens.css").read_text(encoding="utf-8"))))
    return {
        "version": 1,
        "classes": [{"name": name, "module": classes[name],
                     "description": CLASS_DOCS.get(name, f"Syntyr CSS class ({classes[name]}).")}
                    for name in sorted(classes)],
        "tokens": [{"name": name, "module": tokens[name],
                    "description": TOKEN_DOCS.get(name, f"Syntyr CSS property ({tokens[name]}).")}
                   for name in sorted(tokens)],
        "themes": themes,
    }


def component_contract(api, html_data):
    """Full source-discovered inventory plus curated semantic component recipes.

    This is tooling metadata, not a second, separately maintained CSS API.
    The curated component list describes compositions, not class-by-class
    allowed elements; those must not be treated as strict static rules.
    """
    distributions_by_name = all_distributions()
    curated = json.loads((OUTPUT / "components.json").read_text(encoding="utf-8"))
    known_classes = {item["name"] for item in api["classes"]}
    for component in curated["components"]:
        unknown = sorted(set(component["classes"]) - known_classes)
        if unknown:
            raise ValueError(f"Curated {component['name']} uses unknown classes: {unknown}")
        if component["module"] not in distributions_by_name:
            raise ValueError(f"Unknown component distribution: {component['module']}")

    def with_stylesheets(items):
        return [
            {**item, "stylesheets": sorted(
                name for name, modules in distributions_by_name.items()
                if item["module"] in modules
            )}
            for item in items
        ]

    return {
        "schema_version": 1,
        "source_version": (ROOT / "VERSION").read_text(encoding="utf-8").strip(),
        "completeness": "all-source-discovered-classes-and-tokens; curated-components",
        "note": "Curated component elements are guidance, not per-class tag restrictions.",
        "stylesheets": sorted(distributions_by_name),
        "classes": with_stylesheets(api["classes"]),
        "tokens": with_stylesheets(api["tokens"]),
        "themes": api["themes"],
        "attributes": {
            attribute["name"]: [value["name"] for value in attribute["values"]]
            for attribute in html_data["globalAttributes"]
            if attribute["name"].startswith("data-syn-") and "values" in attribute
        },
        "components": curated["components"],
    }


def outputs():
    api = collect()
    classes = api["classes"]
    themes = api["themes"]
    html = {
        "version": 1.1,
        "globalAttributes": [
            {"name": "class", "description": "Syntyr class names in the optional syn-* styling API.",
             "values": [{"name": c["name"], "description": c["description"]} for c in classes]},
            {"name": "data-syn-theme", "description": "Syntyr theme selector (on syn-root or a nested region).",
             "values": [{"name": theme} for theme in themes]},
            {"name": "data-syn-intensity", "description": "Opt-in decorative intensity independent of theme and density.",
             "values": [{"name": name} for name in ("quiet", "standard", "cinematic")]},
            {"name": "data-syn-density", "description": "Opt-in presentation density.",
             "values": [{"name": name} for name in ("compact", "comfortable", "spacious")]},
            {"name": "data-syn-state", "description": "Host-managed decorative state, not an ARIA substitute.",
             "values": [{"name": name} for name in source_state_values()]},
            {"name": "data-syn-featured", "description": "Decorative featured pricing card state."},
        ],
    }
    css = {
        "version": 1.1,
        "properties": [{"name": token["name"], "description": token["description"]} for token in api["tokens"]],
    }
    snippets = {
        f"Syntyr: {name}": {
            "prefix": name,
            "scope": "html,javascriptreact,typescriptreact",
            "body": name,
            "description": CLASS_DOCS.get(name, "Syntyr class."),
        }
        for name in SNIPPET_CLASSES
    }
    payloads = {
        "syntyr-contract.json": component_contract(api, html),
        "syntyr-api.json": api,
        "syntyr.html-custom-data.json": html,
        "syntyr.css-custom-data.json": css,
        "syntyr.code-snippets": snippets,
    }
    return {OUTPUT / file: json.dumps(data, ensure_ascii=False, indent=2) + "\n"
            for file, data in payloads.items()}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Check committed exports against CSS")
    args = parser.parse_args(argv)
    failures = 0
    for path, result in outputs().items():
        if args.check:
            current = path.read_text(encoding="utf-8") if path.exists() else ""
            if current != result:
                print(f"STALE {path.relative_to(ROOT)}")
                failures += 1
            else:
                print(f"OK {path.relative_to(ROOT)}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(result, encoding="utf-8")
            print(f"WROTE {path.relative_to(ROOT)}")
    return int(failures > 0)


if __name__ == "__main__":
    sys.exit(main())
