"""PR validation must check the composed merge without mutating the checkout."""
from pathlib import Path
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


class MergeCandidateTests(unittest.TestCase):
    def create_repo(self, directory):
        repo = Path(directory) / 'repo'
        repo.mkdir()
        git(repo, 'init', '-b', 'main')
        git(repo, 'config', 'user.name', 'Syntyr Contract')
        git(repo, 'config', 'user.email', 'syntyr-test@invalid.example')
        (repo / 'baseline.txt').write_text('base')
        git(repo, 'add', '.')
        git(repo, 'commit', '-qm', 'base')
        git(repo, 'checkout', '-b', 'feature')
        (repo / 'metadata.txt').write_text('old')
        git(repo, 'add', '.')
        git(repo, 'commit', '-qm', 'feature metadata')
        feature_sha = git(repo, 'rev-parse', 'HEAD')
        git(repo, 'checkout', 'main')
        (repo / 'expected.txt').write_text('new')
        git(repo, 'add', '.')
        git(repo, 'commit', '-qm', 'base changes')
        base_sha = git(repo, 'rev-parse', 'HEAD')
        git(repo, 'checkout', 'feature')
        return repo, feature_sha, base_sha

    def test_detects_stale_artifact_only_after_merging_base(self):
        from check_merge_candidate import validate_candidate
        with TemporaryDirectory() as temp:
            repo, feature_sha, base_sha = self.create_repo(temp)
            test = (sys.executable, '-c',
                    'from pathlib import Path; assert Path("expected.txt").read_text() == Path("metadata.txt").read_text()')
            self.assertNotEqual(validate_candidate(repo, base_sha, [test]), 0)
            self.assertEqual(git(repo, 'rev-parse', 'HEAD'), feature_sha)
            self.assertEqual(git(repo, 'status', '--porcelain'), '')
            self.assertEqual(len(git(repo, 'worktree', 'list').splitlines()), 1)

    def test_succeeds_for_compatible_candidate_and_cleans_up(self):
        from check_merge_candidate import validate_candidate
        with TemporaryDirectory() as temp:
            repo, feature_sha, base_sha = self.create_repo(temp)
            test = (sys.executable, '-c',
                    'from pathlib import Path; assert Path("expected.txt").exists() and Path("metadata.txt").exists()')
            self.assertEqual(validate_candidate(repo, base_sha, [test]), 0)
            self.assertEqual(git(repo, 'rev-parse', 'HEAD'), feature_sha)
            self.assertEqual(len(git(repo, 'worktree', 'list').splitlines()), 1)

    def test_merge_conflict_fails_closed_and_cleans_up(self):
        from check_merge_candidate import validate_candidate
        with TemporaryDirectory() as temp:
            repo, feature_sha, _ = self.create_repo(temp)
            git(repo, 'checkout', 'main')
            (repo / 'metadata.txt').write_text('main')
            git(repo, 'add', '.')
            git(repo, 'commit', '-qm', 'conflicting base edit')
            base_sha = git(repo, 'rev-parse', 'HEAD')
            git(repo, 'checkout', 'feature')
            self.assertNotEqual(validate_candidate(repo, base_sha, []), 0)
            self.assertEqual(git(repo, 'rev-parse', 'HEAD'), feature_sha)
            self.assertEqual(len(git(repo, 'worktree', 'list').splitlines()), 1)

    def test_pr_workflow_fetches_current_base_and_runs_isolated_gate(self):
        workflow = (ROOT / '.woodpecker' / 'pr-merge.yaml').read_text()
        self.assertIn('event: pull_request', workflow)
        self.assertIn('git fetch', workflow)
        self.assertIn('python3 scripts/check_merge_candidate.py --base FETCH_HEAD', workflow)
        quality = (ROOT / '.woodpecker' / 'quality.yaml').read_text()
        self.assertIn('python3 scripts/build_agent_docs.py --check', quality)


if __name__ == '__main__':
    unittest.main()
