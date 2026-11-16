"""Optional Syntyr CSS developer CLI. Standard library only.

The distributed CSS is still the complete, permanent runtime interface.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

if __package__:
    from . import syntyr_check, syntyr_agent
    from .registry_install import RegistryError, plan_install, apply_install, verify_install, ROOT, OUTPUT
else:
    import syntyr_check
    import syntyr_agent
    from registry_install import RegistryError, plan_install, apply_install, verify_install, ROOT, OUTPUT


def _print(value, output_format="text"):
    if output_format == "json":
        print(json.dumps(value, indent=2, sort_keys=True))
    elif isinstance(value, str):
        print(value)
    else:
        print(json.dumps(value, indent=2, sort_keys=True))


def _list_items(category: str) -> list[dict]:
    manifest = json.loads((OUTPUT / "registry.json").read_text(encoding="utf-8"))
    items = []
    for item in manifest["items"]:
        files = item.get("files", [])
        item_category = "blocks" if any("/blocks/" in file.get("target", "") for file in files) else "css"
        if category != "all" and item_category != category:
            continue
        items.append({
            "name": item["name"],
            "title": item["title"],
            "description": item["description"],
            "category": item_category,
            "dependencies": [
                dep.rsplit("/", 1)[-1].removesuffix(".json")
                for dep in item.get("registryDependencies", [])
            ],
        })
    return sorted(items, key=lambda item: item["name"])


def main(argv=None) -> int:
    args_list = list(sys.argv[1:] if argv is None else argv)
    if args_list and (args_list[0] == 'init' or
                      args_list[0] == 'check' and '--project' in args_list):
        # Consumer project commands use a pinned, locally installed contract.
        # Preserve --format json spelling from the existing CLI.
        delegated = args_list.copy()
        if '--format' in delegated:
            index = delegated.index('--format')
            fmt = delegated[index + 1] if index + 1 < len(delegated) else ''
            if fmt not in ('text', 'json'):
                print('syntyr: --format requires text or json', file=sys.stderr)
                return 2
            delegated[index:index + 2] = ['--json'] if fmt == 'json' else []
        return syntyr_agent.main(delegated)
    if args_list and args_list[0] in ("check", "doctor"):
        # One canonical validator implementation; doctor only opts into CSS
        # dependency checks and preserves its established JSON/exit contract.
        flags = ["--doctor"] if args_list[0] == "doctor" else []
        return syntyr_check.main([*flags, *args_list[1:]])

    parser = argparse.ArgumentParser(prog="syntyr", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    # Help entries are advertised here; actual parsing is delegated above so
    # all validator arguments work without maintaining a second schema.
    sub.add_parser("check", help="Validate Syntyr markup; --project uses pinned consumer CSS")
    sub.add_parser("init", help="Install a portable Agent Skill and version-pinned CSS in a project")
    sub.add_parser("doctor", help="Diagnose CSS duplicates, overlaps, and mixed version pins")

    ver = sub.add_parser("version", help="Print the bundled Syntyr version")
    ver.add_argument("--format", choices=("text", "json"), default="text")

    listed = sub.add_parser("list", help="Discover available copy-owned items")
    listed.add_argument("--category", choices=("all", "css", "blocks"), default="all")
    listed.add_argument("--format", choices=("text", "json"), default="text")

    add = sub.add_parser("add", help="Preview an offline installation; --apply writes new files")
    add.add_argument("item")
    add.add_argument("--project", type=Path, default=Path("."))
    add.add_argument("--apply", action="store_true")
    add.add_argument("--format", choices=("text", "json"), default="text")

    verify = sub.add_parser("verify", help="Check installed files against syntyr.lock.json")
    verify.add_argument("--project", type=Path, default=Path("."))
    verify.add_argument("--format", choices=("text", "json"), default="text")

    args = parser.parse_args(args_list)
    try:
        if args.command == "version":
            version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
            _print({"version": version} if args.format == "json" else version, args.format)
            return 0
        if args.command == "list":
            items = _list_items(args.category)
            if args.format == "json":
                _print(items, args.format)
            else:
                for item in items:
                    deps = ",".join(item["dependencies"]) or "none"
                    print(f"{item['name']:28} {item['category']:7} CSS: {deps}  {item['description']}")
            return 0
        if args.command == "add":
            plan = plan_install(args.item, args.project)
            if args.apply:
                apply_install(plan, args.project)
            published = {key: value for key, value in plan.items() if key != "files"}
            published["files"] = [{key: value for key, value in entry.items() if key != "_content"}
                                  for entry in plan["files"]]
            published["applied"] = args.apply
            if args.format == "json":
                _print(published, args.format)
            else:
                for entry in published["files"]:
                    print(f"{entry['status']:9} {entry['path']}")
                if args.apply:
                    print("Installed with integrity lockfile; existing content was not overwritten.")
                else:
                    print("Dry run only; pass --apply to create missing files.")
            return 0
        if args.command == "verify":
            diagnostics = verify_install(args.project)
            report = {"status": "error" if diagnostics else "ok", "diagnostics": diagnostics}
            if args.format == "json":
                _print(report, args.format)
            else:
                for item in diagnostics:
                    print(f"{item['path']}: {item['code']}: {item['message']}")
                if not diagnostics:
                    print("OK: installed Syntyr files match syntyr.lock.json")
            return 1 if diagnostics else 0
    except (RegistryError, OSError, ValueError, KeyError) as exc:
        print(f"syntyr {args.command}: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
