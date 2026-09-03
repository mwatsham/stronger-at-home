from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = (ROOT / "docs/website-staging-runbook.md").read_text(encoding="utf-8")


class StagingRunbookTests(unittest.TestCase):
    def test_preflight_uses_account_compatible_read_only_commands(self):
        expected_commands = (
            "cpanel-admin profiles show test-123reg",
            "cpanel-admin --profile test-123reg domains inspect "
            "--domain staging.stronger-at-home.co.uk",
            "cpanel-admin --profile test-123reg diagnostics has-feature "
            "--name lvephpsel",
            "cpanel-admin --profile test-123reg diagnostics has-feature "
            "--name ea-php84",
            "cpanel-admin --profile test-123reg diagnostics has-feature "
            "--name multiphp",
            "cpanel-admin --profile test-123reg diagnostics has-feature "
            "--name multiphp_ini_editor",
            "cpanel-admin --profile test-123reg diagnostics has-feature "
            "--name filemanager",
            "cpanel-admin --profile test-123reg diagnostics has-feature "
            "--name backup",
            "cpanel-admin --profile test-123reg diagnostics quota",
        )

        for command in expected_commands:
            with self.subTest(command=command):
                self.assertIn(command, RUNBOOK)

    def test_preflight_excludes_known_unsupported_commands_and_routes(self):
        normalized_runbook = " ".join(RUNBOOK.split())
        unsupported_commands = (
            "cpanel-admin --profile test-123reg runtime php-installed",
            "cpanel-admin --profile test-123reg runtime php-default",
            "cpanel-admin --profile test-123reg runtime php-vhosts",
            "cpanel-admin --profile test-123reg runtime php-directives",
            "cpanel-admin --profile test-123reg files inspect",
            "cpanel-admin --profile test-123reg files list",
        )

        for command in unsupported_commands:
            with self.subTest(command=command):
                self.assertNotIn(command, RUNBOOK)
        self.assertIn("Software > Select PHP Version", normalized_runbook)
        self.assertIn("Do not use MultiPHP Manager.", normalized_runbook)
        self.assertIn("Browser automation is not permitted", normalized_runbook)

    def test_preflight_and_smoke_checks_require_error_suppression_and_true_noindex(self):
        self.assertIn("`display_errors` is **Off**", RUNBOOK)
        self.assertIn("`display_errors` On", RUNBOOK)
        self.assertIn("`X-Robots-Tag: noindex, nofollow`", RUNBOOK)
        self.assertIn("staging deployment artifact", RUNBOOK)

    def test_deployment_uses_the_reviewed_git_lifecycle(self):
        normalized_runbook = " ".join(RUNBOOK.split())
        required_values = (
            "deploy-staging",
            "/home/v0398ees6dry/repositories/stronger-at-home-staging",
            "/home/v0398ees6dry/public_html/staging.stronger-at-home.co.uk",
            "release.json",
            "runtime version-control",
            "runtime deployments",
            "runtime git-update",
            "--name stronger-at-home-staging",
            "--branch deploy-staging",
            "--source-repository /exact/operator/path/stronger-at-home-staging-update.json",
            "runtime deployment-create",
            "deployed-source-sha",
        )

        for value in required_values:
            with self.subTest(value=value):
                self.assertIn(value, normalized_runbook)

        self.assertIn(
            '"url": "git@github.com:mwatsham/stronger-at-home.git",\n'
            '  "branch": "deploy-staging"',
            RUNBOOK,
        )
        self.assertIn('{"remote_name": "origin"}', RUNBOOK)

    def test_deployment_omits_manual_archive_and_document_root_mutations(self):
        forbidden_instructions = (
            "files upload",
            "File Manager to extract",
            "extract the uploaded ZIP",
            "Rename the existing staging document root",
            "Move the extracted `vendor/`",
        )

        for instruction in forbidden_instructions:
            with self.subTest(instruction=instruction):
                self.assertNotIn(instruction, RUNBOOK)

    def test_smoke_checks_cover_public_security_accessibility_and_safe_delivery(self):
        required_checks = (
            "HTTPS homepage",
            "deny-all",
            "X-Robots-Tag: noindex, nofollow",
            "X-Content-Type-Options: nosniff",
            "all routes and assets",
            "200% browser zoom",
            "keyboard only",
            "safe staging recipient",
        )

        for check in required_checks:
            with self.subTest(check=check):
                self.assertIn(check, RUNBOOK)

    def test_rollback_is_a_new_git_deployment_not_deletion(self):
        normalized_runbook = " ".join(RUNBOOK.split())
        required_rollback = (
            "new source commit",
            "regenerated `deploy-staging`",
            "reviewed `runtime git-update`",
            "reviewed `runtime deployment-create`",
            "complete staging smoke checks",
            "`runtime git-delete`",
            "`runtime deployment-delete`",
            "deleting document-root files",
            "not rollback mechanisms",
        )

        for requirement in required_rollback:
            with self.subTest(requirement=requirement):
                self.assertIn(requirement, normalized_runbook)


if __name__ == "__main__":
    unittest.main()
