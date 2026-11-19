"""All explicit and optional Syntyr selectors are bounded by an opt-in root."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCOPED = [
    *sorted((ROOT / 'src/components').glob('*.css')),
    *(ROOT / f'src/{name}.css' for name in ('recipes', 'effects', 'geometry')),
]


class RootScopeContract(unittest.TestCase):
    def test_scoped_sources_have_exactly_one_module_boundary(self):
        for path in SCOPED:
            with self.subTest(module=path.relative_to(ROOT)):
                source = path.read_text(encoding='utf-8')
                layer = re.search(r'@layer syn\.[\w-]+\s*\{', source)
                self.assertIsNotNone(layer)
                body = source[layer.end():source.rfind('}')]
                clean = re.sub(r'/\*.*?\*/', '', body, flags=re.S).strip()
                self.assertTrue(clean.startswith(':where(.syn-root, .syn-root *) {'))
                self.assertTrue(clean.endswith('}'))
                # The wrapper must be the only top-level rule in this layer.
                depth = 0
                completed = 0
                for ch in clean:
                    if ch == '{':
                        depth += 1
                    elif ch == '}':
                        depth -= 1
                        if depth == 0:
                            completed += 1
                    self.assertGreaterEqual(depth, 0)
                self.assertEqual(depth, 0)
                self.assertEqual(completed, 1, 'Unscoped top-level selector escaped the root')

    def test_source_contract_remains_javascript_free(self):
        for path in SCOPED:
            with self.subTest(module=path.relative_to(ROOT)):
                self.assertNotIn('@import', path.read_text())

    def test_docs_show_explicit_semantic_root(self):
        docs = (ROOT / 'docs/components.md').read_text()
        self.assertIn('<section class="syn-root syn-semantic"', docs)


if __name__ == '__main__':
    unittest.main()
