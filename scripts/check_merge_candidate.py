"""Validate a PR merged with the current base without touching its checkout.

CI fetches the target branch first and passes FETCH_HEAD. This checks the
resulting combined tree, not only the independent PR head; it cannot substitute
for required current-base CI or a merge queue when other PRs land concurrently.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parents[1]


def run(args, cwd: Path, *, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(args, cwd=cwd, check=check, text=True)


def verify_commands(release_zip: Path) -> list[tuple[str, ...]]:
    return [
        (sys.executable, 'scripts/build.py', '--check'),
        (sys.executable, 'scripts/export_api_metadata.py', '--check'),
        (sys.executable, 'scripts/build_agent_docs.py', '--check'),
        (sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-q'),
        (sys.executable, 'scripts/build_cloudflare_site.py'),
        (sys.executable, 'scripts/build_cloudflare_site.py', '--check'),
        (sys.executable, 'scripts/package_release.py', str(release_zip)),
    ]


def validate_candidate(repo: Path, base: str,
                       commands: list[tuple[str, ...]] | None = None) -> int:
    """Return nonzero on conflicts/stale artifacts; leave source HEAD untouched."""
    repo = Path(repo).resolve()
    resolved = subprocess.run(['git', 'rev-parse', '--verify', f'{base}^{{commit}}'],
                              cwd=repo, capture_output=True, text=True)
    if resolved.returncode:
        print(f'Cannot resolve merge-base ref {base!r}: {resolved.stderr.strip()}', file=sys.stderr)
        return 2
    base_sha = resolved.stdout.strip()
    with TemporaryDirectory(prefix='syntyr-merge-candidate-') as directory:
        scratch = Path(directory)
        checkout = scratch / 'checkout'
        added = False
        try:
            run(['git', 'worktree', 'add', '--detach', str(checkout), 'HEAD'], repo)
            added = True
            run(['git', '-c', 'user.name=Syntyr CI',
                 '-c', 'user.email=syntyr-ci@invalid.example',
                 'merge', '--no-commit', '--no-ff', base_sha], checkout)
            for command in commands if commands is not None else verify_commands(scratch / 'release.zip'):
                run(list(command), checkout)
            print(f'PASS isolated merge candidate against {base_sha[:12]}')
            return 0
        except subprocess.CalledProcessError as err:
            print(f'FAIL merge candidate at {err.cmd}: exit {err.returncode}', file=sys.stderr)
            return err.returncode or 1
        finally:
            if added:
                subprocess.run(['git', 'merge', '--abort'], cwd=checkout,
                               check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                run(['git', 'worktree', 'remove', '--force', str(checkout)], repo)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True, help='Fetched target SHA or FETCH_HEAD')
    args = parser.parse_args()
    return validate_candidate(ROOT, args.base)


if __name__ == '__main__':
    sys.exit(main())
