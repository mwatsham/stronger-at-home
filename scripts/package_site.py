#!/usr/bin/env python3
"""Build a deterministic, secret-free website deployment archive."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import sys
from tempfile import TemporaryDirectory
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

if __package__:
    from .validate_site import APPROVED_PUBLIC_SOURCE_SHA256, validate_site
else:
    from validate_site import APPROVED_PUBLIC_SOURCE_SHA256, validate_site


ARCHIVE_TIMESTAMP = (2026, 1, 1, 0, 0, 0)
EXPECTED_PHPMAILER = ("phpmailer/phpmailer", "v7.1.1")
EXPECTED_VENDOR_FILES = 84
EXPECTED_VENDOR_FINGERPRINT = (
    "f8bcd1092477c5ad8ab4edff307a15fff0bae1c2ba67dd796bb53aaffea9d935"
)
FORBIDDEN_COMPONENTS = {".git", "tests", "cache", "__pycache__", "secrets"}
FORBIDDEN_FILENAMES = {"site.php", ".ds_store"}
STAGING_X_ROBOTS_TAG = b'Header always set X-Robots-Tag "noindex, nofollow"\n'


def _forbidden_reason(relative_path: Path) -> str | None:
    components = [component.lower() for component in relative_path.parts]
    if any(component in FORBIDDEN_COMPONENTS for component in components):
        return "forbidden path component"
    filename = relative_path.name.lower()
    if filename in FORBIDDEN_FILENAMES or filename == ".env" or filename.startswith(".env."):
        return "forbidden filename"
    return None


def _collect_files(project_root: Path, source: Path, archive_root: str) -> list[tuple[str, bytes]]:
    if not source.is_dir():
        raise ValueError(f"missing package source directory: {source.relative_to(project_root)}")
    if source.is_symlink():
        raise ValueError(f"package source is a symlink: {source.relative_to(project_root)}")

    collected: list[tuple[str, bytes]] = []
    for directory, directory_names, filenames in os.walk(source, followlinks=False):
        current = Path(directory)
        for name in sorted(directory_names):
            path = current / name
            relative = path.relative_to(project_root)
            if path.is_symlink():
                raise ValueError(f"symlink rejected: {relative.as_posix()}")
            if reason := _forbidden_reason(relative):
                raise ValueError(f"forbidden package entry ({reason}): {relative.as_posix()}")
        for name in sorted(filenames):
            path = current / name
            relative = path.relative_to(project_root)
            if path.is_symlink():
                raise ValueError(f"symlink rejected: {relative.as_posix()}")
            if reason := _forbidden_reason(relative):
                raise ValueError(f"forbidden package entry ({reason}): {relative.as_posix()}")
            if not path.is_file():
                raise ValueError(f"non-regular package entry rejected: {relative.as_posix()}")
            archive_name = PurePosixPath(archive_root, *path.relative_to(source).parts).as_posix()
            collected.append((archive_name, path.read_bytes()))
    return collected


def _validate_production_dependencies(project_root: Path) -> None:
    composer_path = project_root / "composer.json"
    lock_path = project_root / "composer.lock"
    installed_path = project_root / "vendor/composer/installed.json"
    autoload_path = project_root / "vendor/autoload.php"
    try:
        composer = json.loads(composer_path.read_text(encoding="utf-8"))
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
        installed = json.loads(installed_path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError) as error:
        raise ValueError(f"Composer production dependencies are unavailable: {error}") from error

    if composer.get("require", {}).get(EXPECTED_PHPMAILER[0]) != "7.1.1":
        raise ValueError("composer.json must require exact PHPMailer 7.1.1")
    locked = [(item.get("name"), item.get("version")) for item in lock.get("packages", [])]
    installed_packages = [
        (item.get("name"), item.get("version")) for item in installed.get("packages", [])
    ]
    if EXPECTED_PHPMAILER not in locked or EXPECTED_PHPMAILER not in installed_packages:
        raise ValueError("Composer dependencies must contain exact PHPMailer 7.1.1")
    if lock.get("packages-dev"):
        raise ValueError("composer.lock must not define development dependencies for this package")
    if installed_packages != locked or installed.get("dev-package-names"):
        raise ValueError("vendor must contain only the locked production Composer dependencies")
    if not autoload_path.is_file() or autoload_path.is_symlink():
        raise ValueError("vendor/autoload.php must be a regular production dependency file")


def _normalise_vendor_fingerprint_content(archive_name: str, content: bytes) -> bytes:
    if archive_name != "vendor/composer/installed.php":
        return content

    references = re.findall(rb"'reference' => '([0-9a-f]{40})'", content)
    repeated_references = {
        reference for reference in references if references.count(reference) == 2
    }
    if len(repeated_references) != 1:
        raise ValueError(
            "vendor boundary or fingerprint mismatch: invalid Composer root metadata"
        )
    return content.replace(repeated_references.pop(), b"0" * 40)


def _validate_vendor_fingerprint(entries: list[tuple[str, bytes]]) -> None:
    if len(entries) != EXPECTED_VENDOR_FILES:
        raise ValueError(
            "vendor boundary or fingerprint mismatch: "
            f"expected {EXPECTED_VENDOR_FILES} files, found {len(entries)}"
        )

    fingerprint = hashlib.sha256()
    for archive_name, content in sorted(entries, key=lambda item: item[0]):
        name = archive_name.encode("utf-8")
        content = _normalise_vendor_fingerprint_content(archive_name, content)
        fingerprint.update(len(name).to_bytes(4, "big"))
        fingerprint.update(name)
        fingerprint.update(len(content).to_bytes(8, "big"))
        fingerprint.update(content)

    if fingerprint.hexdigest() != EXPECTED_VENDOR_FINGERPRINT:
        raise ValueError(
            "vendor boundary or fingerprint mismatch: production tree is not approved"
        )


def _validate_public_snapshot(entries: list[tuple[str, bytes]]) -> None:
    expected = {
        f"public/{Path(path).relative_to('site').as_posix()}": digest
        for path, digest in APPROVED_PUBLIC_SOURCE_SHA256.items()
    }
    actual = {archive_name: content for archive_name, content in entries}
    if set(actual) != set(expected):
        raise ValueError("public snapshot approval drift: file boundary changed during packaging")
    for archive_name, content in actual.items():
        if hashlib.sha256(content).hexdigest() != expected[archive_name]:
            raise ValueError(
                f"public snapshot approval drift: changed {archive_name} during packaging"
            )


def _staging_htaccess(content: bytes) -> bytes:
    if b"X-Robots-Tag" in content:
        raise ValueError("production server directives unexpectedly contain X-Robots-Tag")
    separator = b"" if content.endswith(b"\n") else b"\n"
    return content + separator + STAGING_X_ROBOTS_TAG


def _write_entry(package: ZipFile, archive_name: str, content: bytes) -> None:
    information = ZipInfo(archive_name, date_time=ARCHIVE_TIMESTAMP)
    information.create_system = 3
    information.compress_type = ZIP_DEFLATED
    information.external_attr = 0o100644 << 16
    package.writestr(information, content, compress_type=ZIP_DEFLATED, compresslevel=9)


def package_site(project_root: Path, destination: Path, environment: str) -> Path:
    """Package public website files and production dependencies for deployment."""

    if environment not in {"staging", "production"}:
        raise ValueError("environment must be staging or production")
    project_root = Path(project_root).resolve()
    destination = Path(destination).resolve()
    _validate_production_dependencies(project_root)

    entries = _collect_files(project_root, project_root / "site", "public")
    vendor_entries = _collect_files(project_root, project_root / "vendor", "vendor")

    validation_errors = validate_site(project_root, environment)
    if validation_errors:
        raise ValueError("Site validation failed: " + "; ".join(validation_errors))

    _validate_public_snapshot(entries)
    _validate_vendor_fingerprint(vendor_entries)
    entries.extend(vendor_entries)
    entries.sort(key=lambda item: item[0])

    snapshot = dict(entries)
    robots_content = snapshot.get("public/robots-staging.txt") if environment == "staging" else None
    if environment == "staging" and robots_content is None:
        raise ValueError("staging robots snapshot is unavailable")

    destination.mkdir(parents=True, exist_ok=True)
    archive = destination / f"stronger-at-home-{environment}.zip"
    with TemporaryDirectory(prefix="site-package-", dir=destination) as temporary:
        temporary_archive = Path(temporary) / archive.name
        with ZipFile(temporary_archive, "w", compression=ZIP_DEFLATED, compresslevel=9) as package:
            for archive_name, content in entries:
                content = (
                    robots_content
                    if environment == "staging" and archive_name == "public/robots.txt"
                    else _staging_htaccess(content)
                    if environment == "staging" and archive_name == "public/.htaccess"
                    else content
                )
                _write_entry(package, archive_name, content)
        temporary_archive.replace(archive)
    return archive


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", required=True, choices=("staging", "production"))
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root (defaults to the parent of scripts/).",
    )
    arguments = parser.parse_args(argv)
    try:
        archive = package_site(arguments.root, arguments.destination, arguments.environment)
    except (OSError, ValueError) as error:
        print(f"Package failed: {error}", file=sys.stderr)
        return 1
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    print(f"Created {archive}")
    print(f"SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
