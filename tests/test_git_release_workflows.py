from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_DIRECTORY = ROOT / ".github/workflows"
FULL_GATE_COMMANDS = (
    "composer install --no-dev --no-interaction --prefer-dist",
    'for test_file in tests/php/*Test.php; do php "$test_file" || exit 1; done',
    "for php_file in $(find site tests/php config -type f -name '*.php' | sort); do php -l \"$php_file\" || exit 1; done",
    "python -m unittest discover -s tests -q",
    "python scripts/validate_site.py --mode development",
    "python scripts/validate_site.py --mode staging",
    "python scripts/validate_brand.py",
    "node --check site/assets/js/site.js",
    "python scripts/package_site.py --environment staging --destination output/site-package",
    "git diff --exit-code",
)


def top_level_section(source: str, heading: str) -> str:
    lines = source.splitlines()
    start = lines.index(f"{heading}:") + 1
    end = start
    while end < len(lines) and (not lines[end] or lines[end].startswith(" ")):
        end += 1
    return "\n".join(lines[start:end])


class GitReleaseWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ci = (WORKFLOW_DIRECTORY / "ci.yml").read_text(encoding="utf-8")
        cls.staging = (WORKFLOW_DIRECTORY / "release-staging.yml").read_text(
            encoding="utf-8"
        )
        cls.production = (WORKFLOW_DIRECTORY / "release-production.yml").read_text(
            encoding="utf-8"
        )

    def assert_common_gate(self, source: str) -> None:
        for fragment in (
            "uses: actions/checkout@v4",
            "uses: shivammathur/setup-php@v2",
            "php-version: '8.4'",
            "uses: actions/setup-python@v5",
            "python-version: '3.14'",
            "uses: actions/cache@v4",
            "composer config cache-files-dir",
            "python -m pip install --disable-pip-version-check -r requirements.txt",
            *FULL_GATE_COMMANDS,
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, source)

    def test_ci_runs_the_complete_gate_with_read_only_permissions(self):
        trigger = top_level_section(self.ci, "on")
        self.assertIn("  push:\n    branches: [main, develop]", trigger)
        self.assertIn("  pull_request:", trigger)
        self.assertIn("  workflow_dispatch:", trigger)
        self.assertEqual(top_level_section(self.ci, "permissions").strip(), "contents: read")
        self.assertNotIn("--mode production", self.ci)
        self.assertNotIn("--environment production", self.ci)
        self.assert_common_gate(self.ci)

    def test_staging_runs_only_for_develop_and_promotes_deploy_staging(self):
        trigger = top_level_section(self.staging, "on")
        self.assertIn("  push:\n    branches: [develop]", trigger)
        self.assertIn("  workflow_dispatch:", trigger)
        self.assertNotIn("main", trigger)
        self.assertEqual(
            top_level_section(self.staging, "permissions").strip(), "contents: write"
        )
        concurrency = top_level_section(self.staging, "concurrency")
        self.assertIn("group: release-staging", concurrency)
        self.assertIn("cancel-in-progress: false", concurrency)
        for fragment in (
            "if: github.ref == 'refs/heads/develop'",
            "DEPLOYMENT_BRANCH: deploy-staging",
            "git fetch --no-tags origin develop",
            'test "${{ github.sha }}" = "$(git rev-parse origin/develop)"',
            "python scripts/build_git_release.py --environment staging",
            '--source-sha "${{ github.sha }}"',
            "git worktree add --detach",
            'checkout --orphan "$DEPLOYMENT_BRANCH"',
            'commit -m "deploy: stage ${{ github.sha }}"',
            "git push origin HEAD:refs/heads/deploy-staging",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.staging)
        self.assert_common_gate(self.staging)

    def test_production_is_manual_main_only_and_environment_protected(self):
        trigger = top_level_section(self.production, "on")
        self.assertEqual(trigger.strip(), "workflow_dispatch:")
        self.assertEqual(
            top_level_section(self.production, "permissions").strip(),
            "contents: write",
        )
        concurrency = top_level_section(self.production, "concurrency")
        self.assertIn("group: release-production", concurrency)
        self.assertIn("cancel-in-progress: false", concurrency)
        for fragment in (
            "environment: production",
            "DEPLOYMENT_BRANCH: deploy-production",
            "ref: main",
            "fetch-depth: 0",
            "python scripts/validate_site.py --mode production",
            "python scripts/package_site.py --environment production --destination output/site-package",
            "git fetch --no-tags origin main",
            'test "$(git rev-parse HEAD)" = "$(git rev-parse origin/main)"',
            "python scripts/build_git_release.py --environment production",
            'commit -m "deploy: production $SOURCE_SHA"',
            "git push origin HEAD:refs/heads/deploy-production",
        ):
            with self.subTest(fragment=fragment):
                self.assertIn(fragment, self.production)
        self.assert_common_gate(self.production)

    def test_release_promotions_replace_tracked_content_and_always_clean_up(self):
        for label, source in (
            ("staging", self.staging),
            ("production", self.production),
        ):
            with self.subTest(workflow=label):
                for fragment in (
                    "github-actions[bot]",
                    'git -C "$release_worktree" rm -r --ignore-unmatch .',
                    'cp -a release/. "$release_worktree/"',
                    'git -C "$release_worktree" add --all',
                    "trap cleanup EXIT",
                    'git worktree remove --force "$release_worktree"',
                    "git worktree prune",
                ):
                    self.assertIn(fragment, source)
                self.assertNotIn("git push --force", source)
                self.assertNotIn("git push --force-with-lease", source)

    def test_workflows_contain_no_private_deployment_credentials_or_actions(self):
        forbidden = (
            "cpanel_token",
            "cpanel_password",
            "fernet",
            "smtp_password",
            "ssh_private_key",
            "appleboy/ssh",
            "scp-action",
            "secrets.",
        )
        for path in sorted(WORKFLOW_DIRECTORY.glob("*.yml")):
            source = path.read_text(encoding="utf-8").lower()
            for fragment in forbidden:
                with self.subTest(workflow=path.name, fragment=fragment):
                    self.assertNotIn(fragment, source)


if __name__ == "__main__":
    unittest.main()
