"""Agent onboarding integrated with the shipped CLI and conservative framework checks."""
import json
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / 'scripts/syntyr_cli.py'


def run(*args, cli=CLI):
    return subprocess.run([sys.executable, str(cli), *map(str, args)],
                          cwd=ROOT, text=True, capture_output=True)


class CliAgentIntegrationTests(unittest.TestCase):
    def test_cli_init_then_project_check_and_existing_check(self):
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            result = run('init', '--project', project, '--agent', 'cursor', '--format', 'json')
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['release'], '0.3.0-alpha.4')
            self.assertTrue((project / '.cursor/skills/syntyr/SKILL.md').is_file())
            html = project / 'index.html'
            html.write_text('<main class="syn-root syn-panel"></main>')
            report = run('check', '--project', project, '--format', 'json', html)
            self.assertEqual(report.returncode, 0, report.stderr + report.stdout)
            self.assertEqual(json.loads(report.stdout)['status'], 'passed')
            # Existing unpinned checker must remain backwards compatible.
            legacy = run('check', '--format', 'json', html)
            self.assertEqual(legacy.returncode, 0, legacy.stderr)

    def test_bundled_cli_initializes_an_unrelated_app(self):
        with TemporaryDirectory() as tmp:
            archive = Path(tmp) / 'bundle.zip'
            built = subprocess.run([sys.executable, str(ROOT / 'scripts/package_cli.py'), str(archive)],
                                   cwd=ROOT, capture_output=True, text=True)
            self.assertEqual(built.returncode, 0, built.stderr)
            with ZipFile(archive) as zip_file:
                zip_file.extractall(tmp)
            bundled = Path(tmp) / f'syntyr-cli-{(ROOT / "VERSION").read_text().strip()}/scripts/syntyr_cli.py'
            project = Path(tmp) / 'app'
            project.mkdir()
            installed = run('init', '--project', project, '--format', 'json', cli=bundled)
            self.assertEqual(installed.returncode, 0, installed.stderr)
            checked = run('check', '--project', project, '--format', 'json', cli=bundled)
            self.assertEqual(checked.returncode, 2)  # No HTML: incomplete, not success.
            page = project / 'check.tsx'
            page.write_text('const View = () => <main className="syn-root syn-buttn"/>;')
            detected = run('check', '--project', project, '--format', 'json', page, cli=bundled)
            self.assertEqual(detected.returncode, 1, detected.stderr + detected.stdout)
            self.assertIn('unknown-class', [d['code'] for d in json.loads(detected.stdout)['diagnostics']])

    def test_jsx_literal_bad_class_is_flagged_but_valid_jsx_is_incomplete(self):
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.assertEqual(run('init', '--project', project).returncode, 0)
            page = project / 'view.tsx'
            page.write_text('''export function Page() {
              const decoy = '<button className="syn-made-up-decoy">oops</button>';
              return <main className="syn-root syn-panel"><button className="syn-buttn">Save</button></main>;
            }''')
            bad = run('check', '--project', project, '--format', 'json', page)
            self.assertEqual(bad.returncode, 1, bad.stderr + bad.stdout)
            findings = json.loads(bad.stdout)['diagnostics']
            self.assertEqual(len([d for d in findings if d['code'] == 'unknown-class']), 1, findings)
            self.assertIn('syn-buttn', findings[0]['message'])
            self.assertEqual(findings[0]['line'], 3)
            page.write_text('export function Page() { return <main className="syn-root syn-panel"/>; }')
            good = run('check', '--project', project, '--format', 'json', page)
            self.assertEqual(good.returncode, 2, good.stdout)
            self.assertEqual(json.loads(good.stdout)['unchecked_files'], [str(page)])

    def test_vue_and_svelte_check_literal_classes_and_mark_dynamic_incomplete(self):
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.assertEqual(run('init', '--project', project).returncode, 0)
            vue = project / 'view.vue'
            vue.write_text('''<script setup>const decoy = '<p class="syn-not-real">';</script>
            <template><main class="syn-root"><p class="syn-buttn" :class="dynamic">Hello</p></main></template>''')
            svelte = project / 'view.svelte'
            svelte.write_text('''<script>const decoy = '<div class="syn-bad-decoy">';</script>
            <main class="syn-root"><button class="syn-button syn-buttn" class:active={enabled}>OK</button></main>''')
            for file in (vue, svelte):
                with self.subTest(file=file):
                    report = run('check', '--project', project, '--format', 'json', file)
                    self.assertEqual(report.returncode, 1, report.stderr + report.stdout)
                    messages = [d['message'] for d in json.loads(report.stdout)['diagnostics']]
                    self.assertEqual(sum('syn-buttn' in m for m in messages), 1)
                    self.assertFalse(any('decoy' in m for m in messages))
                    file.write_text(file.read_text().replace('syn-buttn', 'syn-button'))
                    fixed = run('check', '--project', project, '--format', 'json', file)
                    self.assertEqual(fixed.returncode, 2, fixed.stdout)
                    self.assertIn(str(file), json.loads(fixed.stdout)['unchecked_files'])

    def test_markup_in_dynamic_jsx_expression_is_not_misreported_as_verified(self):
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            self.assertEqual(run('init', '--project', project).returncode, 0)
            jsx = project / 'view.jsx'
            jsx.write_text('const Page = () => <div className={dynamicClass}><span className="syn-panel" /></div>;')
            report = run('check', '--project', project, '--format', 'json', jsx)
            self.assertEqual(report.returncode, 2, report.stdout)
            self.assertIn(str(jsx), json.loads(report.stdout)['unchecked_files'])


if __name__ == '__main__':
    unittest.main()
