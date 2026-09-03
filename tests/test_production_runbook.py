from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
RUNBOOK = (ROOT / "docs/website-production-runbook.md").read_text(encoding="utf-8")


class ProductionRunbookTests(unittest.TestCase):
    def test_production_prerequisites_remain_explicit_approval_gates(self):
        normalized_runbook = " ".join(RUNBOOK.split())
        required_gates = (
            "accepted staging",
            "green `main`",
            "GitHub production approval",
            "final portrait",
            "privacy approval",
            "explicit first-publication approval",
            "live-recipient confirmation",
            "melanie@stronger-at-home.co.uk",
        )

        for gate in required_gates:
            with self.subTest(gate=gate):
                self.assertIn(gate, normalized_runbook)

    def test_production_uses_exact_git_targets_and_external_configuration(self):
        normalized_runbook = " ".join(RUNBOOK.split())
        required_values = (
            "deploy-production",
            "/home/v0398ees6dry/repositories/stronger-at-home-production",
            "/home/v0398ees6dry/public_html/stronger-at-home.co.uk",
            "/home/v0398ees6dry/private/stronger-at-home/production/site.php",
            "runtime version-control",
            "runtime deployments",
            "runtime git-update",
            "--name stronger-at-home-production",
            "--branch deploy-production",
            "--source-repository /exact/operator/path/stronger-at-home-production-update.json",
            "runtime deployment-create",
            "deployment status",
            "deployed-source-sha",
        )

        for value in required_values:
            with self.subTest(value=value):
                self.assertIn(value, normalized_runbook)

        self.assertIn(
            '"url": "git@github.com:mwatsham/stronger-at-home.git",\n'
            '  "branch": "deploy-production"',
            RUNBOOK,
        )
        self.assertIn('{"remote_name": "origin"}', RUNBOOK)

    def test_production_artifact_and_smoke_requirements_are_fail_closed(self):
        normalized_runbook = " ".join(RUNBOOK.split())
        required_checks = (
            "no staging directives in the artifact",
            "https://stronger-at-home.co.uk",
            "https://www.stronger-at-home.co.uk",
            "absence of `noindex`",
            "all routes and assets",
            "external configuration",
            "vendor paths",
            "generic failure behaviour",
            "one explicitly authorised message to Melanie",
        )

        for check in required_checks:
            with self.subTest(check=check):
                self.assertIn(check, normalized_runbook)

    def test_rollback_is_verified_as_a_new_git_deployment(self):
        normalized_runbook = " ".join(RUNBOOK.split())
        required_rollback = (
            "rollback verification",
            "new source commit",
            "regenerated `deploy-production`",
            "reviewed `runtime git-update`",
            "reviewed `runtime deployment-create`",
            "complete production smoke checks",
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
