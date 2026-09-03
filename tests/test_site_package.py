import json
from pathlib import Path
import shutil
import subprocess
import sys
from tempfile import TemporaryDirectory
import unittest
from zipfile import ZipFile

from scripts.package_site import package_site


ROOT = Path(__file__).resolve().parents[1]
STAGING_ROBOTS = b"User-agent: *\nDisallow: /\n"


class SitePackageTests(unittest.TestCase):
    def test_staging_package_excludes_secrets_and_uses_noindex_robots(self):
        with TemporaryDirectory() as directory:
            archive = package_site(ROOT, Path(directory), "staging")

            with ZipFile(archive) as package:
                names = set(package.namelist())
                self.assertIn("public/robots.txt", names)
                self.assertIn("public/api/enquiry.php", names)
                self.assertNotIn("config/site.php", names)
                self.assertFalse(any(name.startswith("tests/") for name in names))
                self.assertEqual(package.read("public/robots.txt"), STAGING_ROBOTS)

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

    def test_repeated_builds_are_byte_for_byte_deterministic(self):
        with TemporaryDirectory() as first, TemporaryDirectory() as second:
            first_archive = package_site(ROOT, Path(first), "staging")
            second_archive = package_site(ROOT, Path(second), "staging")

            self.assertEqual(first_archive.read_bytes(), second_archive.read_bytes())

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
