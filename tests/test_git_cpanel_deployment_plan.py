import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PLAN = (
    ROOT
    / "docs/superpowers/plans/2026-09-03-stronger-at-home-git-cpanel-deployment.md"
).read_text(encoding="utf-8")


def section(start: str, end: str) -> str:
    return PLAN[PLAN.index(start) : PLAN.index(end)]


def descriptor_after_path(source: str, path: str) -> dict[str, str]:
    following = source[source.index(path) + len(path) :]
    match = re.search(r"~~~json\s+(.*?)\s+~~~", following, re.DOTALL)
    if match is None:
        raise AssertionError(f"No JSON descriptor follows {path}")
    return json.loads(match.group(1))


class GitCpanelDeploymentPlanTests(unittest.TestCase):
    def assert_descriptor_lifecycle(
        self,
        source: str,
        environment: str,
        branch: str,
        repository_root: str,
    ) -> None:
        normalized = " ".join(source.split())
        prefix = f"/exact/operator/path/stronger-at-home-{environment}"
        approval_path = f"{prefix}-approval.json"
        create_path = f"{prefix}-create.json"
        update_path = f"{prefix}-update.json"

        self.assertEqual(
            descriptor_after_path(source, approval_path),
            {
                "url": "git@github.com:mwatsham/stronger-at-home.git",
                "branch": branch,
            },
        )
        self.assertEqual(
            descriptor_after_path(source, create_path),
            {
                "url": "git@github.com:mwatsham/stronger-at-home.git",
                "remote_name": "origin",
            },
        )
        self.assertEqual(
            descriptor_after_path(source, update_path),
            {"remote_name": "origin"},
        )

        for expected in (
            approval_path,
            create_path,
            update_path,
            '"url": "git@github.com:mwatsham/stronger-at-home.git"',
            f'"branch": "{branch}"',
            '"remote_name": "origin"',
            "approval evidence is not passed to `cpanel-admin`",
            f"runtime git-create --name stronger-at-home-{environment} "
            f"--repository-root {repository_root} --source-repository {create_path} "
            "--type git --dry-run",
            f"runtime git-update --name stronger-at-home-{environment} "
            f"--repository-root {repository_root} --branch {branch} "
            f"--source-repository {update_path} --dry-run",
        ):
            with self.subTest(environment=environment, expected=expected):
                self.assertIn(expected, normalized)

        self.assertLess(
            normalized.index("runtime git-create"),
            normalized.index("runtime git-update"),
        )

    def test_staging_mapping_uses_distinct_approval_create_and_update_descriptors(self):
        task = section("### Task 5:", "### Task 6:")
        self.assert_descriptor_lifecycle(
            task,
            "staging",
            "deploy-staging",
            "/home/v0398ees6dry/repositories/stronger-at-home-staging",
        )

    def test_staging_activation_names_the_remote_name_only_update_descriptor(self):
        task = section("### Task 6:", "### Task 7:")
        self.assertIn("stronger-at-home-staging-update.json", task)
        self.assertNotIn("protected source-definition file", task)

    def test_production_mapping_uses_distinct_approval_create_and_update_descriptors(self):
        task = section("### Task 7:", "## Plan Self-Review")
        self.assert_descriptor_lifecycle(
            task,
            "production",
            "deploy-production",
            "/home/v0398ees6dry/repositories/stronger-at-home-production",
        )


if __name__ == "__main__":
    unittest.main()
