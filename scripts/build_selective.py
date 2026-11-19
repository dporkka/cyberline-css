"""Optional, explicit, deterministic CSS composition (Python standard library only).

No source scanning, class purging, stylesheet parser, installed compiler, or
mandatory application build step. Dynamic classes must be accounted for by the
developer when choosing components and modules.
"""
import argparse
import gzip
import json
from pathlib import Path

from build import ROOT, SOURCE, DIST, COMPONENTS, assemble, distributions


def comma_names(value, allowed, flag):
    if value is None:
        return None
    if value == "none":
        return set()
    supplied = value.split(",")
    if not supplied or any(not item or item != item.strip() for item in supplied):
        raise ValueError(f"{flag}: enter nonempty comma-separated names")
    unknown = sorted(set(supplied) - set(allowed))
    if unknown:
        raise ValueError(f"{flag}: unknown value(s): {', '.join(unknown)}")
    return set(supplied)


def choose_sources(components=None, modules=None):
    """Return sources in canonical cascade order, with necessary form dependency."""
    named_components = {Path(item).stem: item for item in COMPONENTS}
    core = distributions()["syntyr.core.css"]
    optional = tuple(path for path in distributions()["syntyr.all.css"] if path not in core)
    named_modules = {Path(path).stem: path for path in optional}
    selected_components = comma_names(components, named_components, "--components")
    selected_modules = comma_names(modules, named_modules, "--modules")
    if selected_components is None:
        selected_components = set(named_components)
    if selected_modules is None:
        selected_modules = set()
    if "form-composition" in selected_components:
        selected_components.add("forms")
    paths = ("tokens.css", "base.css")
    paths += tuple(path for path in COMPONENTS
                   if Path(path).stem in selected_components)
    paths += tuple(path for path in optional
                   if Path(path).stem in selected_modules)
    return paths


def validate_output(output, report):
    dist = DIST.resolve()
    src = SOURCE.resolve()
    candidates = [output] + ([report] if report is not None else [])
    resolved = [path.expanduser().resolve() for path in candidates]
    if len(set(resolved)) != len(resolved):
        raise ValueError("--report and --output must be different files")
    for path in resolved:
        if path == dist or dist in path.parents or path == src or src in path.parents:
            raise ValueError("Custom files cannot overwrite src/ or dist/ artifacts")
    return resolved[0], resolved[1] if report is not None else None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True,
                        help="destination CSS file (never src/ or dist/)")
    parser.add_argument("--components",
                        help="comma-separated core components; defaults to all, or 'none'")
    parser.add_argument("--modules",
                        help="comma-separated optional CSS modules; defaults to none")
    parser.add_argument("--report", type=Path,
                        help="optional deterministic JSON manifest and size report")
    args = parser.parse_args()
    try:
        paths = choose_sources(args.components, args.modules)
        css = assemble(paths).encode("utf-8")
        output, report = validate_output(args.output, args.report)
        manifest = {
            "included_sources": list(paths),
            "raw_bytes": len(css),
            "gzip_bytes": len(gzip.compress(css, mtime=0)),
        }
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_bytes(css)
        if report is not None:
            report.parent.mkdir(parents=True, exist_ok=True)
            report.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n",
                              encoding="utf-8")
        print(f"WROTE {output}: {manifest['raw_bytes']} raw / "
              f"{manifest['gzip_bytes']} gzip")
        return 0
    except (ValueError, OSError) as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    raise SystemExit(main())
