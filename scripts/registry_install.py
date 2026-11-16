"""Opt-in, stdlib-only planner for the local Syntyr copy-owned registry.

Offline and preview-first. Explicit installs never overwrite existing consumer
files; lock metadata records exact installed bytes for later verification.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import tempfile

if __package__:
    from .build_shadcn_registry import ROOT, OUTPUT, DEFAULT_REGISTRY_URL
else:
    from build_shadcn_registry import ROOT, OUTPUT, DEFAULT_REGISTRY_URL

LOCKFILE = "syntyr.lock.json"
ITEM_NAME = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")


class RegistryError(ValueError):
    """Invalid registry data, unsafe target, or existing-file conflict."""


def _digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _safe_destination(project: Path, target: str) -> Path:
    if not isinstance(target, str) or not target.startswith("~/syntyr/"):
        raise RegistryError("Registry target outside ~/syntyr/")
    relative = target[2:]
    parts = Path(relative).parts
    if not parts or any(part in {".", ".."} for part in parts):
        raise RegistryError("Invalid registry target")
    if not re.fullmatch(r"syntyr/(css|blocks)/[a-z0-9_.-]+|syntyr/LICENSE", relative):
        raise RegistryError("Unknown registry destination: " + relative)
    if project.is_symlink():
        raise RegistryError("Project directory must not be a symlink")
    destination = project / relative
    for parent in (project, *destination.parents):
        if parent == project.parent:
            break
        if parent.is_symlink():
            raise RegistryError("Symlinked installation path: " + str(parent))
    if destination.is_symlink():
        raise RegistryError("Symlinked installation target: " + relative)
    return destination


def plan_install(name: str, project: Path, registry_root: Path = OUTPUT) -> dict:
    """Resolve explicit CSS dependencies, validate hashes and preview all writes."""
    if not isinstance(name, str) or not ITEM_NAME.fullmatch(name):
        raise RegistryError("Invalid item name")
    project = Path(project).absolute()
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    registry_root = Path(registry_root)
    collected: dict[str, str] = {}
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(item_name: str) -> None:
        if item_name in visited:
            return
        if item_name in visiting:
            raise RegistryError("Cyclic registry dependency")
        visiting.add(item_name)
        file = registry_root / "r" / (item_name + ".json")
        try:
            obj = json.loads(file.read_text(encoding="utf-8"))
        except (OSError, ValueError) as error:
            raise RegistryError("Missing or unreadable registry item: " + item_name) from error
        if obj.get("name") != item_name or obj.get("type") != "registry:item":
            raise RegistryError("Unexpected registry item identity")
        meta = obj.get("meta", {})
        if meta.get("syntyrVersion") != version or meta.get("runtimeJavaScript") is not False:
            raise RegistryError("Incompatible item version or runtime")
        if obj.get("dependencies") != []:
            raise RegistryError("Runtime dependencies are not supported")
        for dep in obj.get("registryDependencies", []):
            prefix = DEFAULT_REGISTRY_URL + "/"
            if not isinstance(dep, str) or not dep.startswith(prefix) or not dep.endswith(".json"):
                raise RegistryError("Untrusted registry dependency URL")
            child = dep[len(prefix):-5]
            if not ITEM_NAME.fullmatch(child):
                raise RegistryError("Invalid dependency item name")
            visit(child)
        hashes = meta.get("fileDigests")
        if not isinstance(hashes, dict):
            raise RegistryError("Missing content digests")
        files = obj.get("files")
        if not isinstance(files, list) or not files:
            raise RegistryError("Missing item files")
        for entry in files:
            if not isinstance(entry, dict) or entry.get("type") != "registry:file":
                raise RegistryError("Unexpected file entry")
            target, content = entry.get("target"), entry.get("content")
            if not isinstance(content, str):
                raise RegistryError("Missing file content")
            dest = _safe_destination(project, target)
            relative = dest.relative_to(project).as_posix()
            expected_hash = _digest(content.encode("utf-8"))
            if hashes.get(target) != expected_hash:
                raise RegistryError("File digest mismatch: " + relative)
            old = collected.get(relative)
            if old is not None and old != content:
                raise RegistryError("Conflicting registry assets: " + relative)
            collected[relative] = content
        visiting.remove(item_name)
        visited.add(item_name)

    visit(name)
    files = []
    for relative, content in collected.items():
        target = _safe_destination(project, "~/" + relative)
        status = "create"
        if target.exists():
            if not target.is_file():
                raise RegistryError("Non-file registry destination: " + relative)
            status = "identical" if target.read_bytes() == content.encode("utf-8") else "conflict"
        files.append({"path": relative, "status": status,
                      "sha256": _digest(content.encode("utf-8")),
                      "bytes": len(content.encode("utf-8")), "_content": content})
    return {"item": name, "version": version, "project": str(project), "files": files}


def _read_lock(project: Path) -> tuple[dict | None, bytes | None]:
    path = project / LOCKFILE
    if path.is_symlink():
        raise RegistryError("Symlinked Syntyr lockfile")
    if not path.exists():
        return None, None
    if not path.is_file():
        raise RegistryError("Non-file Syntyr lockfile")
    original = path.read_bytes()
    try:
        data = json.loads(original)
    except (ValueError, UnicodeError) as exc:
        raise RegistryError("Invalid Syntyr lockfile; refusing to overwrite") from exc
    if not isinstance(data, dict) or data.get("schema") != 1:
        raise RegistryError("Unsupported Syntyr lockfile schema")
    if not isinstance(data.get("version"), str):
        raise RegistryError("Invalid Syntyr lockfile version")
    if not isinstance(data.get("files"), dict) or not isinstance(data.get("items"), list):
        raise RegistryError("Invalid Syntyr lockfile contents")
    for relative, digest in data["files"].items():
        if not isinstance(relative, str) or not isinstance(digest, str) or not SHA256.fullmatch(digest):
            raise RegistryError("Invalid Syntyr lockfile digest")
        _safe_destination(project, "~/" + relative)
    if any(not isinstance(item, str) or not ITEM_NAME.fullmatch(item) for item in data["items"]):
        raise RegistryError("Invalid Syntyr lockfile item")
    return data, original


def verify_install(project: Path) -> list[dict]:
    """Diagnose installed-file drift without mutating the consumer project."""
    project = Path(project).absolute()
    lock, _ = _read_lock(project)
    if lock is None:
        raise RegistryError("No syntyr.lock.json found; install a registry item first")
    results = []
    current_version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    if lock["version"] != current_version:
        results.append({"code": "version-mismatch", "path": LOCKFILE,
                        "severity": "error", "message": "Lockfile was created by a different Syntyr version"})
    for relative, expected in sorted(lock["files"].items()):
        target = _safe_destination(project, "~/" + relative)
        if not target.exists() or not target.is_file():
            code, message = "missing-file", "Installed Syntyr file is missing"
        elif _digest(target.read_bytes()) != expected:
            code, message = "modified-file", "Installed Syntyr file differs from lockfile"
        else:
            continue
        results.append({"code": code, "path": relative, "severity": "error", "message": message})
    return results


def _write_new_file(target: Path, data: bytes) -> None:
    """Exclusive create; never follow an already-existing file."""
    flags = os.O_CREAT | os.O_EXCL | os.O_WRONLY | getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(target, flags, 0o644)
    owned = os.fstat(fd)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(data)
    except BaseException:
        # Remove a partial write only if the target still refers to our inode.
        try:
            current = target.stat(follow_symlinks=False)
            if (current.st_dev, current.st_ino) == (owned.st_dev, owned.st_ino):
                target.unlink()
        except FileNotFoundError:
            pass
        raise


def _write_lock(project: Path, content: bytes, previous: bytes | None) -> None:
    """Stage lock bytes then atomically publish if no external change is observed."""
    lockfile = project / LOCKFILE
    candidate = None
    try:
        with tempfile.NamedTemporaryFile(mode="wb", prefix=".syntyr-lock-",
                                         suffix=".tmp", dir=project, delete=False) as stream:
            candidate = Path(stream.name)
            stream.write(content)
        if lockfile.is_symlink():
            raise RegistryError("Symlinked Syntyr lockfile")
        if previous is None:
            try:
                _write_new_file(lockfile, content)
            except FileExistsError as exc:
                raise RegistryError("Lockfile concurrently created") from exc
        else:
            if not lockfile.is_file() or lockfile.read_bytes() != previous:
                raise RegistryError("Lockfile changed since preflight")
            os.replace(candidate, lockfile)
            candidate = None
    finally:
        if candidate is not None:
            candidate.unlink(missing_ok=True)


def apply_install(plan: dict, project: Path) -> None:
    """Copy missing files and write integrity metadata; roll back new files on failure."""
    project = Path(project).absolute()
    if plan.get("project") != str(project):
        raise RegistryError("Installation target does not match the reviewed plan")
    if not project.is_dir() or project.is_symlink():
        raise RegistryError("Installation project must be an existing real directory")
    existing, prior_bytes = _read_lock(project)
    if existing is not None and existing["version"] != plan["version"]:
        raise RegistryError("Existing lockfile tracks another Syntyr version")
    if existing is not None and verify_install(project):
        raise RegistryError("Existing Syntyr installation has drift; resolve before adding items")
    planned_bytes = {}
    for entry in plan["files"]:
        relative = entry["path"]
        target = _safe_destination(project, "~/" + relative)
        content = entry["_content"].encode("utf-8")
        if entry["status"] == "conflict" or (target.exists() and target.read_bytes() != content):
            raise RegistryError("Would overwrite existing file: " + relative)
        if entry["sha256"] != _digest(content):
            raise RegistryError("Install plan content digest mismatch")
        planned_bytes[relative] = content
    files = dict(existing["files"]) if existing else {}
    files.update({path: _digest(data) for path, data in planned_bytes.items()})
    items = sorted(set((existing["items"] if existing else []) + [plan["item"]]))
    lock_data = {"schema": 1, "version": plan["version"],
                 "items": items, "files": dict(sorted(files.items()))}
    serialized = (json.dumps(lock_data, sort_keys=True, indent=2) + "\n").encode("utf-8")
    created: list[tuple[Path, bytes]] = []
    try:
        for relative, content in planned_bytes.items():
            target = _safe_destination(project, "~/" + relative)
            target.parent.mkdir(parents=True, exist_ok=True)
            target = _safe_destination(project, "~/" + relative)
            if target.exists():
                if target.read_bytes() != content:
                    raise RegistryError("Existing target changed during installation: " + relative)
                continue
            _write_new_file(target, content)
            created.append((target, content))
        _write_lock(project, serialized, prior_bytes)
    except Exception:
        for target, content in reversed(created):
            # Never delete a file whose bytes were modified after creation.
            if target.is_file() and not target.is_symlink() and target.read_bytes() == content:
                target.unlink()
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description="Plan or explicitly install a local Syntyr registry item")
    parser.add_argument("item", help="Name from registry/registry.json")
    parser.add_argument("--project", type=Path, required=True)
    parser.add_argument("--apply", action="store_true", help="Opt in to creating missing assets; never overwrites")
    args = parser.parse_args()
    try:
        plan = plan_install(args.item, args.project)
        for entry in plan["files"]:
            print(f"{entry['status']:9} {entry['path']} ({entry['bytes']} bytes, sha256:{entry['sha256'][:12]})")
        print(f"Syntyr {plan['version']} / {len(plan['files'])} files")
        if args.apply:
            apply_install(plan, args.project)
            print("Installed; existing identical files untouched; syntyr.lock.json updated")
        else:
            print("Dry run only. Pass --apply to copy missing files.")
        return 0
    except (RegistryError, OSError) as error:
        parser.exit(2, f"Registry installation rejected: {error}\n")


if __name__ == "__main__":
    raise SystemExit(main())
