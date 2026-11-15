"""Build reproducible modular CSS distributions using only Python's standard library.

No compiler, minifier, network access, or package-manager install.
Optional ESM modules are copied byte-for-byte; no JavaScript is required by CSS consumers.
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
    'components/overlays.css', 'components/data.css', 'components/patterns.css',
)

def assemble(paths):
    return '\n'.join((SOURCE / path).read_text(encoding='utf-8').strip() for path in paths) + '\n'

def distributions():
    core = ('tokens.css', 'base.css') + COMPONENTS
    primary = {
        'syntyr.core.css': core,
        'syntyr.semantic.css': ('semantic.css',),
        'syntyr.recipes.css': ('recipes.css',),
        'syntyr.effects.css': ('effects.css',),
        'syntyr.geometry.css': ('geometry.css',),
        'syntyr.symbols.css': ('symbols.css',),
        'syntyr.viz.css': ('viz.css',),
        'syntyr.utilities.css': ('utilities.css',),
        'syntyr.print.css': ('print.css',),
        'syntyr.css': core + ('effects.css',),
        'syntyr.all.css': core + ('semantic.css', 'recipes.css', 'geometry.css', 'symbols.css', 'effects.css', 'viz.css', 'utilities.css', 'print.css'),
    }
    return primary



def js_distributions():
    """Independent, explicitly opt-in ES modules; never imported by CSS."""
    return {
        'syntyr.viz.js': 'js/viz.js',
        'syntyr.motion.js': 'js/motion.js',
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='fail if committed dist is stale')
    args = parser.parse_args()
    failed = False
    for name, inputs in distributions().items():
        output = assemble(inputs).encode('utf-8')
        path = DIST / name
        zipped = len(gzip.compress(output, mtime=0))
        if args.check:
            match = path.exists() and path.read_bytes() == output
            print(f'{"OK" if match else "STALE"} {name}: {len(output)} raw / {zipped} gzip')
            failed |= not match
        else:
            DIST.mkdir(exist_ok=True)
            path.write_bytes(output)
            print(f'WROTE {name}: {len(output)} raw / {zipped} gzip')
    for name, source in js_distributions().items():
        output = (SOURCE / source).read_bytes()
        path = DIST / name
        zipped = len(gzip.compress(output, mtime=0))
        if args.check:
            match = path.exists() and path.read_bytes() == output
            print(f'{"OK" if match else "STALE"} {name}: {len(output)} raw / {zipped} gzip')
            failed |= not match
        else:
            DIST.mkdir(exist_ok=True)
            path.write_bytes(output)
            print(f'WROTE {name}: {len(output)} raw / {zipped} gzip')
    return int(failed)

if __name__ == '__main__':
    sys.exit(main())
