"""RTL layout behavior is inherited from the nearest direction context."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class RTLContracts(unittest.TestCase):
    def test_semantic_tables_respect_direction_and_logical_block_borders(self):
        css=(ROOT/"src/semantic.css").read_text()
        self.assertIn("border-block-end: 1px solid var(--syn-frame);",css)
        self.assertIn("text-align: start;",css)
        self.assertNotIn("text-align: left;",css)

    def test_cut_panel_mirrors_at_the_inline_end(self):
        css=(ROOT/"src/components/layout.css").read_text()
        self.assertIn("inset-inline-end: -1px;", css)
        self.assertIn("&.syn-panel--cut:dir(rtl)::after", css)
        self.assertIn("clip-path: polygon(0 0, 100% 100%, 0 100%);", css)

    def test_breadcrumb_separator_uses_local_direction_not_root_global(self):
        css=(ROOT/"src/components/patterns.css").read_text()
        self.assertIn("&.syn-breadcrumbs li + li:dir(rtl)::before",css)
        self.assertIn("transform: skew(22deg)",css)

    def test_active_app_rail_marker_uses_logical_inset(self):
        css=(ROOT/"src/recipes.css").read_text()
        self.assertIn("inset-inline-start: 0;",css)
        self.assertIn("&.syn-app-nav a[aria-current=\"page\"]::before",css)
        self.assertNotIn("box-shadow: inset 3px 0",css)

    def test_asymmetric_geometry_mirrors_for_nested_rtl(self):
        css=(ROOT/"src/geometry.css").read_text()
        self.assertIn("&.syn-frame--notch:dir(rtl)",css)
        self.assertIn("&.syn-frame--circuit:dir(rtl)::after",css)
        self.assertIn("transform: scaleX(-1)",css)

    def test_static_rtl_fixture_is_in_browser_audit_and_site(self):
        page=(ROOT/"examples/mature-patterns.html").read_text()
        for token in ("syn-panel--cut", "syn-app-nav", "syn-frame--notch", "syn-frame--circuit", "syn-breadcrumbs", 'dir="ltr"'):
            self.assertIn(token,page)
        for link in ('../dist/syntyr.recipes.css','../dist/syntyr.geometry.css'):
            self.assertIn(link,page)
        for filename in ('tests/browser_matrix.py','tests/axe_audit.py','tests/reflow_test.py'):
            self.assertIn('"examples/mature-patterns.html"',(ROOT/filename).read_text())
