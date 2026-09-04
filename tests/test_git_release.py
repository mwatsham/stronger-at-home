import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile, ZipInfo

from scripts.build_git_release import (
    build_git_release,
    extract_approved_archive,
    validate_provenance,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE_SHA = "0123456789abcdef0123456789abcdef01234567"
BUILD_TIMESTAMP = "2026-09-03T22:00:00Z"
ACCOUNT_HOME = "/home/v0398ees6dry"


def write_regular_entry(archive: ZipFile, name: str, content: str) -> None:
    information = ZipInfo(name)
    information.create_system = 3
    information.external_attr = (stat.S_IFREG | 0o644) << 16
    archive.writestr(information, content.encode("utf-8"))


class GitReleaseTests(unittest.TestCase):
    def assert_release_tree(self, release: Path) -> None:
        self.assertEqual(
            {path.name for path in release.iterdir()},
            {".cpanel.yml", "deploy.sh", "release.json", "public", "vendor"},
        )
        self.assertFalse(any(path.is_symlink() for path in release.rglob("*")))
        self.assertEqual(
            (release / ".cpanel.yml").read_text(encoding="utf-8"),
            "---\ndeployment:\n  tasks:\n    - /bin/bash deploy.sh\n",
        )

    def test_staging_release_has_exact_boundary_metadata_and_bindings(self):
        with TemporaryDirectory() as directory:
            release = build_git_release(
                ROOT,
                Path(directory) / "release",
                "staging",
                SOURCE_SHA,
                BUILD_TIMESTAMP,
            )

            self.assert_release_tree(release)
            self.assertFalse((release / "public/robots-staging.txt").exists())
            expected_metadata = {
                "buildTimestamp": BUILD_TIMESTAMP,
                "deploymentBranch": "deploy-staging",
                "environment": "staging",
                "hostname": "staging.stronger-at-home.co.uk",
                "sourceBranch": "develop",
                "sourceSha": SOURCE_SHA,
            }
            metadata_source = (release / "release.json").read_text(encoding="utf-8")
            self.assertEqual(json.loads(metadata_source), expected_metadata)
            self.assertEqual(
                metadata_source,
                json.dumps(expected_metadata, indent=2, sort_keys=True) + "\n",
            )
            htaccess = (release / "public/.htaccess").read_text(encoding="utf-8")
            self.assertIn(
                "RewriteCond %{HTTP_HOST} !^staging\\.stronger-at-home\\.co\\.uk$ [NC]",
                htaccess,
            )
            self.assertNotIn("www\\.stronger-at-home", htaccess)
            self.assertEqual(htaccess.count("STRONGER_HOME_CONFIG"), 1)
            self.assertEqual(htaccess.count("STRONGER_HOME_AUTOLOAD"), 1)
            self.assertIn(
                'SetEnv STRONGER_HOME_CONFIG '
                '"/home/v0398ees6dry/private/stronger-at-home/staging/site.php"',
                htaccess,
            )
            self.assertIn(
                'SetEnv STRONGER_HOME_AUTOLOAD '
                '"/home/v0398ees6dry/stronger-at-home-releases/staging/'
                f'{SOURCE_SHA}/vendor/autoload.php"',
                htaccess,
            )

    def test_repeated_release_builds_have_identical_git_content_and_modes(self):
        with TemporaryDirectory() as directory:
            temporary = Path(directory)
            first = build_git_release(
                ROOT, temporary / "first", "staging", SOURCE_SHA, BUILD_TIMESTAMP
            )
            second = build_git_release(
                ROOT, temporary / "second", "staging", SOURCE_SHA, BUILD_TIMESTAMP
            )

            def git_snapshot(release: Path):
                return {
                    path.relative_to(release).as_posix(): (
                        stat.S_IMODE(path.stat().st_mode),
                        path.read_bytes(),
                    )
                    for path in release.rglob("*")
                    if path.is_file()
                }

            self.assertEqual(git_snapshot(first), git_snapshot(second))

    def test_production_release_uses_only_production_metadata_and_bindings(self):
        with TemporaryDirectory() as directory:
            temporary = Path(directory)
            archive = temporary / "approved-production.zip"
            with ZipFile(archive, "w") as package:
                write_regular_entry(
                    package,
                    "public/.htaccess",
                    (ROOT / "site/.htaccess").read_text(encoding="utf-8"),
                )
                write_regular_entry(package, "public/index.html", "production\n")
                write_regular_entry(package, "vendor/autoload.php", "<?php\n")

            with patch("scripts.build_git_release.package_site", return_value=archive):
                release = build_git_release(
                    ROOT,
                    temporary / "release",
                    "production",
                    SOURCE_SHA,
                    BUILD_TIMESTAMP,
                )

            self.assert_release_tree(release)
            self.assertEqual(
                json.loads((release / "release.json").read_text(encoding="utf-8")),
                {
                    "buildTimestamp": BUILD_TIMESTAMP,
                    "deploymentBranch": "deploy-production",
                    "environment": "production",
                    "hostname": "stronger-at-home.co.uk",
                    "sourceBranch": "main",
                    "sourceSha": SOURCE_SHA,
                },
            )
            combined = (
                (release / "public/.htaccess").read_text(encoding="utf-8")
                + (release / "deploy.sh").read_text(encoding="utf-8")
                + (release / "release.json").read_text(encoding="utf-8")
            )
            self.assertIn(
                "/home/v0398ees6dry/private/stronger-at-home/production/site.php",
                combined,
            )
            self.assertIn(
                f"/home/v0398ees6dry/stronger-at-home-releases/production/{SOURCE_SHA}",
                combined,
            )
            self.assertIn(
                "/home/v0398ees6dry/public_html/stronger-at-home.co.uk",
                combined,
            )
            self.assertIn(
                "RewriteCond %{HTTP_HOST} "
                "!^(?:stronger-at-home\\.co\\.uk|www\\.stronger-at-home\\.co\\.uk)$ [NC]",
                combined,
            )
            self.assertNotIn("staging", combined)

    def test_provenance_rejects_invalid_sha_and_timestamp_values(self):
        validate_provenance(SOURCE_SHA, BUILD_TIMESTAMP)

        for source_sha in ("main", "abc", "g" * 40, "A" * 40):
            with self.subTest(source_sha=source_sha), self.assertRaisesRegex(
                ValueError, "source SHA"
            ):
                validate_provenance(source_sha, BUILD_TIMESTAMP)

        for build_timestamp in (
            "2026-09-03 22:00:00Z",
            "2026-09-03T22:00:00+00:00",
            "2026-13-03T22:00:00Z",
        ):
            with self.subTest(build_timestamp=build_timestamp), self.assertRaisesRegex(
                ValueError, "build timestamp"
            ):
                validate_provenance(SOURCE_SHA, build_timestamp)

    def test_safe_extraction_rejects_unsafe_members_before_writing(self):
        unsafe_members = {
            "absolute path": ("/public/index.html", False),
            "parent traversal": ("public/../secret", False),
            "unexpected root": ("config/site.php", False),
            "symlink": ("public/link", True),
        }
        for label, (unsafe_name, is_symlink) in unsafe_members.items():
            with self.subTest(label=label), TemporaryDirectory() as directory:
                temporary = Path(directory)
                archive = temporary / "unsafe.zip"
                with ZipFile(archive, "w") as package:
                    write_regular_entry(package, "public/index.html", "safe first\n")
                    if is_symlink:
                        information = ZipInfo(unsafe_name)
                        information.create_system = 3
                        information.external_attr = (stat.S_IFLNK | 0o777) << 16
                        package.writestr(information, b"../private/site.php")
                    else:
                        write_regular_entry(package, unsafe_name, "unsafe\n")

                destination = temporary / "extracted"
                with self.assertRaisesRegex(ValueError, "archive"):
                    extract_approved_archive(archive, destination)
                self.assertFalse(destination.exists())

    def test_builder_rejects_existing_environment_bindings(self):
        with TemporaryDirectory() as directory:
            temporary = Path(directory)
            archive = temporary / "duplicate-binding.zip"
            with ZipFile(archive, "w") as package:
                write_regular_entry(
                    package,
                    "public/.htaccess",
                    "SetEnv STRONGER_HOME_CONFIG \"already-present\"\n",
                )
                write_regular_entry(package, "vendor/autoload.php", "<?php\n")

            with patch("scripts.build_git_release.package_site", return_value=archive):
                with self.assertRaisesRegex(ValueError, "environment binding"):
                    build_git_release(
                        ROOT,
                        temporary / "release",
                        "staging",
                        SOURCE_SHA,
                        BUILD_TIMESTAMP,
                    )
            self.assertFalse((temporary / "release").exists())

    def test_command_line_builds_release_and_rejects_invalid_input(self):
        with TemporaryDirectory() as directory:
            temporary = Path(directory)
            output = temporary / "release"
            command = [
                sys.executable,
                str(ROOT / "scripts/build_git_release.py"),
                "--environment",
                "staging",
                "--source-sha",
                SOURCE_SHA,
                "--build-timestamp",
                BUILD_TIMESTAMP,
                "--output-directory",
                str(output),
            ]
            result = subprocess.run(
                command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(str(output.resolve()), result.stdout)
            self.assertRegex(result.stdout, r"SHA-256: [0-9a-f]{64}\n")
            self.assertTrue((output / "release.json").is_file())

            invalid_command = command.copy()
            invalid_command[5] = "abc"
            invalid_command[-1] = str(temporary / "invalid")
            invalid = subprocess.run(
                invalid_command,
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("source SHA", invalid.stderr)
            self.assertNotIn("Traceback", invalid.stderr)


class DeploymentScriptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.release_directory = TemporaryDirectory()
        cls.release = build_git_release(
            ROOT,
            Path(cls.release_directory.name) / "release",
            "staging",
            SOURCE_SHA,
            BUILD_TIMESTAMP,
        )

    @classmethod
    def tearDownClass(cls):
        cls.release_directory.cleanup()

    def prepare_account(self):
        account_directory = TemporaryDirectory()
        self.addCleanup(account_directory.cleanup)
        account_home = Path(account_directory.name).resolve()
        repository_root = account_home / "repositories/stronger-at-home-staging"
        shutil.copytree(self.release, repository_root)
        deploy_path = repository_root / "deploy.sh"
        deploy_path.write_text(
            deploy_path.read_text(encoding="utf-8").replace(ACCOUNT_HOME, str(account_home)),
            encoding="utf-8",
        )
        deploy_path.chmod(0o755)

        config_path = account_home / "private/stronger-at-home/staging/site.php"
        config_path.parent.mkdir(parents=True)
        config_path.write_text("<?php return [];\n", encoding="utf-8")

        document_root = account_home / "public_html/staging.stronger-at-home.co.uk"
        document_root.mkdir(parents=True)
        (document_root / "obsolete.txt").write_text("old release\n", encoding="utf-8")

        release_root = account_home / "stronger-at-home-releases/staging"
        release_path = release_root / SOURCE_SHA
        next_path = document_root.with_name(document_root.name + f".next-{SOURCE_SHA}")
        return account_home, repository_root, document_root, release_path, next_path

    def run_deployment(self, script: Path, cwd: Path, account_home: Path, **extra_env):
        environment = os.environ.copy()
        environment.update({"HOME": str(account_home), **extra_env})
        return subprocess.run(
            ["/bin/bash", str(script)],
            cwd=cwd,
            env=environment,
            capture_output=True,
            text=True,
            check=False,
        )

    def test_successful_deployment_swaps_complete_tree_and_records_source(self):
        account_home, repository_root, document_root, release_path, next_path = (
            self.prepare_account()
        )

        result = self.run_deployment(
            repository_root / "deploy.sh", repository_root, account_home
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertFalse((document_root / "obsolete.txt").exists())
        self.assertTrue((release_path / "previous-public/obsolete.txt").is_file())
        self.assertTrue((document_root / "index.html").is_file())
        self.assertTrue((release_path / "vendor/autoload.php").is_file())
        self.assertEqual(
            (release_path / "deployed-source-sha").read_text(encoding="utf-8"),
            SOURCE_SHA + "\n",
        )
        self.assertFalse(next_path.exists())

    def test_second_move_failure_restores_previous_document_root(self):
        account_home, repository_root, document_root, release_path, next_path = (
            self.prepare_account()
        )
        fake_bin = account_home / "test-bin"
        fake_bin.mkdir()
        counter = account_home / "mv-count"
        fake_mv = fake_bin / "mv"
        fake_mv.write_text(
            "#!/bin/bash\n"
            "set -eu\n"
            "count=0\n"
            'if [[ -f "$MV_COUNT_FILE" ]]; then count=$(<"$MV_COUNT_FILE"); fi\n'
            "count=$((count + 1))\n"
            'printf "%s\\n" "$count" > "$MV_COUNT_FILE"\n'
            'if [[ "$count" -eq 2 ]]; then exit 70; fi\n'
            'exec /bin/mv "$@"\n',
            encoding="utf-8",
        )
        fake_mv.chmod(0o755)

        result = self.run_deployment(
            repository_root / "deploy.sh",
            repository_root,
            account_home,
            PATH=str(fake_bin) + os.pathsep + os.environ.get("PATH", ""),
            MV_COUNT_FILE=str(counter),
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((document_root / "obsolete.txt").is_file())
        self.assertFalse((release_path / "previous-public").exists())
        self.assertTrue((next_path / "index.html").is_file())
        self.assertTrue((release_path / "vendor/autoload.php").is_file())
        self.assertFalse((release_path / "deployed-source-sha").exists())

    def test_wrong_working_directory_fails_without_changing_either_tree(self):
        account_home, repository_root, document_root, release_path, next_path = (
            self.prepare_account()
        )
        wrong_directory = account_home / "wrong-directory"
        wrong_directory.mkdir()

        result = self.run_deployment(
            repository_root / "deploy.sh", wrong_directory, account_home
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((document_root / "obsolete.txt").is_file())
        self.assertFalse(release_path.exists())
        self.assertFalse(next_path.exists())

    def test_wrong_home_and_existing_targets_fail_before_the_swap(self):
        account_home, repository_root, document_root, release_path, next_path = (
            self.prepare_account()
        )
        wrong_home = account_home / "wrong-home"
        result = self.run_deployment(
            repository_root / "deploy.sh", repository_root, wrong_home
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((document_root / "obsolete.txt").is_file())
        self.assertFalse(release_path.exists())

        release_path.mkdir(parents=True)
        result = self.run_deployment(
            repository_root / "deploy.sh", repository_root, account_home
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((document_root / "obsolete.txt").is_file())
        self.assertFalse(next_path.exists())

        release_path.rmdir()
        next_path.mkdir()
        (next_path / "sentinel.txt").write_text("keep\n", encoding="utf-8")
        result = self.run_deployment(
            repository_root / "deploy.sh", repository_root, account_home
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertTrue((document_root / "obsolete.txt").is_file())
        self.assertTrue((next_path / "sentinel.txt").is_file())
        self.assertFalse(release_path.exists())

    def test_missing_required_inputs_fail_before_creating_release_state(self):
        for missing in ("public/.htaccess", "vendor/autoload.php", "config"):
            with self.subTest(missing=missing):
                account_home, repository_root, document_root, release_path, next_path = (
                    self.prepare_account()
                )
                if missing == "config":
                    (account_home / "private/stronger-at-home/staging/site.php").unlink()
                else:
                    (repository_root / missing).unlink()

                result = self.run_deployment(
                    repository_root / "deploy.sh", repository_root, account_home
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertTrue((document_root / "obsolete.txt").is_file())
                self.assertFalse(release_path.exists())
                self.assertFalse(next_path.exists())


if __name__ == "__main__":
    unittest.main()
