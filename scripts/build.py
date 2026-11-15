"""Build reproducible modular CSS distributions using only Python's standard library.

No compiler, minifier, runtime JS, network access, or package-manager install.
"""
from pathlib import Path
import argparse
import gzip
import sys

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'src'
DIST = ROOT / 'dist'
COMPONENTS = (
    'components/layout.css', 'components/typography.css',
    'components/buttons.css', 'components/forms.css',
    'components/form-composition.css', 'components/overlays.css', 'components/data.css', 'components/patterns.css',
)

def assemble(paths):
    return '\n'.join((SOURCE / path).read_text(encoding='utf-8').strip() for path in paths) + '\n'

def distributions():
    core = ('tokens.css', 'base.css') + COMPONENTS
    primary = {
        'syntyr.core.css': core,
        'syntyr.semantic.css': ('semantic.css',),
        'syntyr.server.css': ('server.css',),
        'syntyr.semantic-bundle.css': core + ('semantic.css',),
        'syntyr.recipes.css': ('recipes.css',),
        'syntyr.operations.css': ('operations.css',),
        'syntyr.data-grid.css': ('data-grid.css',),
        'syntyr.native-recipes.css': ('native-recipes.css',),
        'syntyr.effects.css': ('effects.css',),
        'syntyr.motion.css': ('motion.css',),
        'syntyr.geometry.css': ('geometry.css',),
        'syntyr.symbols.css': ('symbols.css',),
        'syntyr.viz.css': ('viz.css',),
        'syntyr.utilities.css': ('utilities.css',),
        'syntyr.print.css': ('print.css',),
        'syntyr.css': core + ('effects.css',),
        'syntyr.all.css': core + ('semantic.css', 'recipes.css', 'operations.css', 'data-grid.css', 'native-recipes.css', 'geometry.css', 'symbols.css', 'effects.css', 'motion.css', 'viz.css', 'utilities.css', 'print.css', 'server.css'),
    }
    return primary


def component_distributions():
    """Standalone CSS files for explicit per-component imports, never runtime imports.

    A consumer must load components/tokens.css, components/base.css, then
    selected components/*.css. Component order follows COMPONENTS.
    """
    files = ("tokens.css", "base.css") + COMPONENTS
    return {"components/" + Path(name).name: (name,) for name in files}


def all_distributions():
    """Complete, publicly shipped CSS registry (bundles + atomic files)."""
    return {**distributions(), **component_distributions()}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='fail if committed dist is stale')
    args = parser.parse_args()
    failed = False
    for name, inputs in all_distributions().items():
        output = assemble(inputs).encode('utf-8')
        path = DIST / name
        zipped = len(gzip.compress(output, mtime=0))
        if args.check:
            match = path.exists() and path.read_bytes() == output
            print(f'{"OK" if match else "STALE"} {name}: {len(output)} raw / {zipped} gzip')
            failed |= not match
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(output)
            print(f'WROTE {name}: {len(output)} raw / {zipped} gzip')
    return int(failed)

if __name__ == '__main__':
    sys.exit(main())
