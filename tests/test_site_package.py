import json
from pathlib import Path
import re
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from zipfile import ZipFile

import scripts.package_site as package_module
from scripts.package_site import package_site


ROOT = Path(__file__).resolve().parents[1]
STAGING_ROBOTS = b"User-agent: *\nDisallow: /\n"


class SitePackageTests(unittest.TestCase):
    def test_staging_package_excludes_secrets_and_uses_noindex_robots(self):
        with TemporaryDirectory() as directory:
            archive = package_site(ROOT, Path(directory), "staging")

            with ZipFile(archive) as package:
                names = set(package.namelist())
                self.assertEqual(len(names), 115)
                self.assertEqual(sum(name.startswith("public/") for name in names), 31)
                self.assertEqual(sum(name.startswith("vendor/") for name in names), 84)
                self.assertIn("public/robots.txt", names)
                self.assertNotIn("public/robots-staging.txt", names)
                self.assertIn("public/api/enquiry.php", names)
                self.assertIn("public/assets/fonts/OFL-source-serif.txt", names)
                self.assertIn("public/assets/fonts/OFL-atkinson.txt", names)
                self.assertNotIn("config/site.php", names)
                self.assertFalse(any(name.startswith("tests/") for name in names))
                self.assertEqual(package.read("public/robots.txt"), STAGING_ROBOTS)
                packaged_htaccess = package.read("public/.htaccess")
                self.assertEqual(
                    packaged_htaccess.count(b'Header always set X-Robots-Tag "noindex, nofollow"'),
                    1,
                )
                self.assertNotIn(
                    b'X-Robots-Tag',
                    (ROOT / "site/.htaccess").read_bytes(),
                )

    def test_package_contains_only_the_public_root_and_locked_production_vendor(self):
        with TemporaryDirectory() as directory:
            archive = package_site(ROOT, Path(directory), "staging")

            with ZipFile(archive) as package:
                names = package.namelist()
                self.assertTrue(names)
                self.assertTrue(
                    all(name.startswith(("public/", "vendor/")) for name in names),
                    names,
                )
                self.assertIn("vendor/autoload.php", names)
                installed = json.loads(package.read("vendor/composer/installed.json"))
                self.assertEqual(
                    [(item["name"], item["version"]) for item in installed["packages"]],
                    [("phpmailer/phpmailer", "v7.1.1")],
                )
                lowered = [name.lower() for name in names]
                for forbidden in (
                    "/.git/",
                    "/.env",
                    "/site.php",
                    "/tests/",
                    "/cache/",
                    "/__pycache__/",
                    "/secrets/",
                    "/.ds_store",
                ):
                    self.assertFalse(any(forbidden in f"/{name}" for name in lowered))

    def test_package_supplies_cpanel_404_shtml_with_the_approved_error_page(self):
        with TemporaryDirectory() as directory:
            archive = package_site(ROOT, Path(directory), "staging")

            with ZipFile(archive) as package:
                self.assertEqual(
                    package.read("public/404.shtml"),
                    package.read("public/404.html"),
                )

    def test_repeated_builds_are_byte_for_byte_deterministic(self):
        with TemporaryDirectory() as first, TemporaryDirectory() as second:
            first_archive = package_site(ROOT, Path(first), "staging")
            second_archive = package_site(ROOT, Path(second), "staging")

            self.assertEqual(first_archive.read_bytes(), second_archive.read_bytes())

    def test_generated_composer_root_branch_metadata_does_not_change_archive(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy, symlinks=True)
            first_archive = package_site(copy, Path(directory) / "first", "staging")

            installed_path = copy / "vendor/composer/installed.php"
            installed = installed_path.read_text(encoding="utf-8")
            root_versions = re.findall(
                r"'(?:pretty_version|version)' => '(dev-[^']+)'", installed
            )
            self.assertEqual(len(root_versions), 4)
            self.assertEqual(len(set(root_versions)), 1)
            installed_path.write_text(
                installed.replace(root_versions[0], "dev-another-branch"),
                encoding="utf-8",
            )

            second_archive = package_site(copy, Path(directory) / "second", "staging")

            self.assertEqual(first_archive.read_bytes(), second_archive.read_bytes())

    def test_packager_archives_the_validated_byte_snapshot_if_source_changes_during_write(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy, symlinks=True)
            original_home = (copy / "site/index.html").read_bytes()
            original_write_entry = package_module._write_entry
            mutated = False

            def mutate_after_snapshot(package, archive_name, content):
                nonlocal mutated
                if not mutated:
                    mutated = True
                    (copy / "site/index.html").write_bytes(b"changed after validation\n")
                original_write_entry(package, archive_name, content)

            with patch.object(package_module, "_write_entry", side_effect=mutate_after_snapshot):
                archive = package_module.package_site(copy, Path(directory) / "output", "staging")

            with ZipFile(archive) as package:
                self.assertEqual(package.read("public/index.html"), original_home)

    def test_packager_rejects_symlinks_in_an_included_tree(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy, symlinks=True)
            (copy / "site/linked-secret").symlink_to(copy / "config/site.example.php")

            with self.assertRaisesRegex(ValueError, "symlink.*site/linked-secret"):
                package_site(copy, Path(directory) / "output", "staging")

    def test_packager_rejects_forbidden_entries_in_an_included_tree(self):
        forbidden_paths = (
            "site/.env",
            "site/config/site.php",
            "site/tests/probe.txt",
            "site/cache/probe.txt",
            "site/__pycache__/probe.pyc",
            "site/secrets/probe.txt",
            "vendor/.git/config",
            "vendor/.DS_Store",
        )
        for relative_path in forbidden_paths:
            with self.subTest(relative_path=relative_path), TemporaryDirectory() as directory:
                copy = Path(directory) / "project"
                shutil.copytree(ROOT, copy, symlinks=True)
                forbidden = copy / relative_path
                forbidden.parent.mkdir(parents=True, exist_ok=True)
                forbidden.write_text("must not ship\n", encoding="utf-8")

                with self.assertRaisesRegex(ValueError, "forbidden package entry"):
                    package_site(copy, Path(directory) / "output", "staging")

    def test_packager_rejects_missing_or_unexpected_composer_dependencies(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy, symlinks=True)
            installed_path = copy / "vendor/composer/installed.json"
            installed = json.loads(installed_path.read_text(encoding="utf-8"))
            installed["packages"][0]["version"] = "v7.1.0"
            installed_path.write_text(json.dumps(installed), encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "PHPMailer 7.1.1"):
                package_site(copy, Path(directory) / "output", "staging")

    def test_packager_rejects_an_arbitrary_extra_vendor_file(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy, symlinks=True)
            (copy / "vendor/credential.txt").write_text(
                "must never ship\n", encoding="utf-8"
            )

            with self.assertRaisesRegex(
                ValueError, "vendor boundary or fingerprint mismatch"
            ):
                package_site(copy, Path(directory) / "output", "staging")

    def test_packager_rejects_a_modified_locked_dependency_file(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy, symlinks=True)
            dependency = copy / "vendor/phpmailer/phpmailer/src/PHPMailer.php"
            dependency.write_bytes(dependency.read_bytes() + b"\n")

            with self.assertRaisesRegex(
                ValueError, "vendor boundary or fingerprint mismatch"
            ):
                package_site(copy, Path(directory) / "output", "staging")

    def test_packager_rejects_unvalidated_public_source(self):
        with TemporaryDirectory() as directory:
            copy = Path(directory) / "project"
            shutil.copytree(ROOT, copy, symlinks=True)
            home = copy / "site/index.html"
            home.write_text(home.read_text(encoding="utf-8") + "\n", encoding="utf-8")

            with self.assertRaisesRegex(ValueError, "Site validation failed.*approval drift"):
                package_site(copy, Path(directory) / "output", "staging")

    def test_production_package_is_blocked_by_unresolved_publication_gates(self):
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "Production blocker remains: portrait"):
                package_site(ROOT, Path(directory), "production")

    def test_real_production_package_excludes_the_staging_robots_template(self):
        expected_blockers = [
            "Production blocker remains: portrait",
        ]
        real_validate_site = package_module.validate_site

        def allow_only_known_publication_blockers(project_root, environment):
            errors = real_validate_site(project_root, environment)
            self.assertEqual(errors, expected_blockers)
            return []

        with TemporaryDirectory() as directory, patch.object(
            package_module,
            "validate_site",
            side_effect=allow_only_known_publication_blockers,
        ):
            archive = package_site(ROOT, Path(directory), "production")

            with ZipFile(archive) as package:
                names = set(package.namelist())
                self.assertEqual(len(names), 115)
                self.assertEqual(sum(name.startswith("public/") for name in names), 31)
                self.assertEqual(sum(name.startswith("vendor/") for name in names), 84)
                self.assertNotIn("public/robots-staging.txt", names)
                self.assertEqual(
                    package.read("public/robots.txt"),
                    (ROOT / "site/robots.txt").read_bytes(),
                )
                self.assertNotIn(b"X-Robots-Tag", package.read("public/.htaccess"))

    def test_documented_command_line_entry_point_builds_the_staging_archive(self):
        with TemporaryDirectory() as directory:
            result = subprocess.run(
                [
                    sys.executable,
                    str(ROOT / "scripts/package_site.py"),
                    "--environment",
                    "staging",
                    "--destination",
                    directory,
                ],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((Path(directory) / "stronger-at-home-staging.zip").is_file())
            self.assertIn("SHA-256:", result.stdout)

    def test_packager_rejects_an_unknown_environment(self):
        with TemporaryDirectory() as directory:
            with self.assertRaisesRegex(ValueError, "staging or production"):
                package_site(ROOT, Path(directory), "preview")


if __name__ == "__main__":
    unittest.main()
