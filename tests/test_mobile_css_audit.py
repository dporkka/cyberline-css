"""Contract tests for the conservative CSS-to-native portability report."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.audit_mobile_css import audit_css

ROOT = Path(__file__).resolve().parents[1]


class MobileCSSAuditTests(unittest.TestCase):
    def test_distinguishes_portable_styles_from_adaptable_and_web_only(self):
        css = '''
.card {
  flex: 1;
  opacity: .75;
  background-color: #123456;
  padding: .75rem;
  color: var(--syn-text);
  display: grid;
  position: sticky;
  border-radius: 6px;
  unknown-mobile-property: 1;
}
'''
        findings = {finding['property']: finding for finding in audit_css(css)}
        for prop in ('flex', 'opacity', 'background-color'):
            self.assertEqual(findings[prop]['status'], 'portable', prop)
        for prop in ('padding', 'color', 'border-radius'):
            self.assertEqual(findings[prop]['status'], 'adapt', prop)
        for prop in ('display', 'position'):
            self.assertEqual(findings[prop]['status'], 'web-only', prop)
        self.assertEqual(findings['unknown-mobile-property']['status'], 'unknown')
        self.assertEqual(findings['flex']['line'], 3)

    def test_skips_comments_and_nested_semicolons_and_detects_media_context(self):
        css = '''/* color: red; */
@media (min-width: 40rem) {
  .item {
    color: #fff;
    background-image: url("data:image/svg+xml;utf8,<svg></svg>");
    content: "; color: blue";
  }
}
.outside { opacity: 0.5; }
'''
        findings = audit_css(css)
        self.assertEqual([x['property'] for x in findings],
                         ['color', 'background-image', 'content', 'opacity'])
        self.assertEqual(findings[0]['status'], 'adapt')
        self.assertEqual(findings[1]['status'], 'web-only')
        self.assertEqual(findings[2]['status'], 'web-only')
        self.assertEqual(findings[3]['status'], 'portable')

    def test_custom_property_and_animation_cannot_be_reported_portable(self):
        css = '''.a { --syn-space-1: .375rem; transform: translateX(4px); }
@keyframes blink { 50% { opacity: .4; } }
'''
        findings = audit_css(css)
        self.assertEqual([x['status'] for x in findings],
                         ['adapt', 'adapt', 'web-only'])

    def test_intrinsic_css_values_and_font_fallbacks_are_not_declared_portable(self):
        css = '''.item {
  width: max-content;
  height: min-content;
  font-size: larger;
  font-family: "Inter", sans-serif;
  color: currentColor;
  background-color: #ffffff;
  padding: auto;
}'''
        findings = {f['property']: f['status'] for f in audit_css(css)}
        for prop in ('width', 'height', 'font-size', 'font-family', 'color', 'padding'):
            self.assertEqual(findings[prop], 'adapt', prop)
        self.assertEqual(findings['background-color'], 'portable')

    def test_cli_provides_machine_readable_report_and_strict_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / 'mobile.css'
            source.write_text('.foo { opacity: 1; display: grid; }', encoding='utf-8')
            cmd = [sys.executable, 'scripts/audit_mobile_css.py',
                   str(source), '--format', 'json', '--strict']
            result = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report['target'], 'react-native')
            self.assertEqual(report['summary']['portable'], 1)
            self.assertEqual(report['summary']['web-only'], 1)
            self.assertEqual(report['summary']['total'], 2)
            self.assertEqual(report['findings'][1]['property'], 'display')
            source.write_text('.foo { flex: 1; opacity: .5; }', encoding='utf-8')
            success = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(success.returncode, 0, success.stdout + success.stderr)

    def test_docs_describe_limits_and_checker_entry_point(self):
        docs = (ROOT / 'docs/mobile-frameworks.md').read_text(encoding='utf-8')
        self.assertIn('scripts/audit_mobile_css.py', docs)
        self.assertIn('not a CSS-to-native compiler', docs)


if __name__ == '__main__':
    unittest.main()
