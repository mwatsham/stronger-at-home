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


if __name__ == "__main__":
    unittest.main()
