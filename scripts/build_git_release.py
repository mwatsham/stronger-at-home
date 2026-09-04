#!/usr/bin/env python3
"""Build a traceable, deterministic Git deployment tree for cPanel."""

from __future__ import annotations

import argparse
from datetime import datetime
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import stat
import sys
from tempfile import TemporaryDirectory
from types import MappingProxyType
from typing import Mapping
from zipfile import BadZipFile, ZipFile, ZipInfo

if __package__:
    from .package_site import package_site
else:
    from package_site import package_site


ACCOUNT_HOME = "/home/v0398ees6dry"
ENVIRONMENTS: Mapping[str, Mapping[str, str]] = MappingProxyType(
    {
        "staging": MappingProxyType(
            {
                "sourceBranch": "develop",
                "deploymentBranch": "deploy-staging",
                "hostname": "staging.stronger-at-home.co.uk",
                "documentRoot": (
                    "/home/v0398ees6dry/public_html/staging.stronger-at-home.co.uk"
                ),
                "configPath": (
                    "/home/v0398ees6dry/private/stronger-at-home/staging/site.php"
                ),
                "repositoryRoot": (
                    "/home/v0398ees6dry/repositories/stronger-at-home-staging"
                ),
                "releaseRoot": (
                    "/home/v0398ees6dry/stronger-at-home-releases/staging"
                ),
            }
        ),
        "production": MappingProxyType(
            {
                "sourceBranch": "main",
                "deploymentBranch": "deploy-production",
                "hostname": "stronger-at-home.co.uk",
                "documentRoot": (
                    "/home/v0398ees6dry/public_html/stronger-at-home.co.uk"
                ),
                "configPath": (
                    "/home/v0398ees6dry/private/stronger-at-home/production/site.php"
                ),
                "repositoryRoot": (
                    "/home/v0398ees6dry/repositories/stronger-at-home-production"
                ),
                "releaseRoot": (
                    "/home/v0398ees6dry/stronger-at-home-releases/production"
                ),
            }
        ),
    }
)

CPANEL_CONFIGURATION = "---\ndeployment:\n  tasks:\n    - /bin/bash deploy.sh\n"
ENVIRONMENT_MARKERS = (
    "STRONGER_HOME_CONFIG",
    "STRONGER_HOME_AUTOLOAD",
)
SHARED_HOST_RULES = (
    "RewriteCond %{HTTP_HOST} "
    "!^(?:stronger-at-home\\.co\\.uk|www\\.stronger-at-home\\.co\\.uk|"
    "staging\\.stronger-at-home\\.co\\.uk)$ [NC]\n"
    "RewriteRule ^ - [R=400,L]\n"
    "RewriteCond %{HTTP_HOST} ^www\\.stronger-at-home\\.co\\.uk$ [NC]\n"
    "RewriteRule ^ https://stronger-at-home.co.uk%{REQUEST_URI} [R=301,L]\n"
    "RewriteCond %{HTTPS} !=on\n"
    "RewriteCond %{HTTP_HOST} "
    "^(?:stronger-at-home\\.co\\.uk|staging\\.stronger-at-home\\.co\\.uk)$ [NC]\n"
    "RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]\n"
)
ENVIRONMENT_HOST_RULES: Mapping[str, str] = MappingProxyType(
    {
        "staging": (
            "RewriteCond %{HTTP_HOST} "
            "!^staging\\.stronger-at-home\\.co\\.uk$ [NC]\n"
            "RewriteRule ^ - [R=400,L]\n"
            "RewriteCond %{HTTPS} !=on\n"
            "RewriteCond %{HTTP_HOST} "
            "^staging\\.stronger-at-home\\.co\\.uk$ [NC]\n"
            "RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]\n"
        ),
        "production": (
            "RewriteCond %{HTTP_HOST} "
            "!^(?:stronger-at-home\\.co\\.uk|www\\.stronger-at-home\\.co\\.uk)$ [NC]\n"
            "RewriteRule ^ - [R=400,L]\n"
            "RewriteCond %{HTTP_HOST} ^www\\.stronger-at-home\\.co\\.uk$ [NC]\n"
            "RewriteRule ^ https://stronger-at-home.co.uk%{REQUEST_URI} [R=301,L]\n"
            "RewriteCond %{HTTPS} !=on\n"
            "RewriteCond %{HTTP_HOST} ^stronger-at-home\\.co\\.uk$ [NC]\n"
            "RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]\n"
        ),
    }
)


def _environment(environment: str) -> Mapping[str, str]:
    try:
        return ENVIRONMENTS[environment]
    except (KeyError, TypeError) as error:
        raise ValueError("environment must be staging or production") from error


def _validate_source_sha(source_sha: str) -> None:
    if not isinstance(source_sha, str) or re.fullmatch(r"[0-9a-f]{40}", source_sha) is None:
        raise ValueError("source SHA must be forty lowercase hexadecimal characters")


def validate_provenance(source_sha: str, build_timestamp: str) -> None:
    """Validate immutable release provenance supplied by the build workflow."""

    _validate_source_sha(source_sha)
    if not isinstance(build_timestamp, str) or re.fullmatch(
        r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z",
        build_timestamp,
    ) is None:
        raise ValueError("build timestamp must use UTC format YYYY-MM-DDTHH:MM:SSZ")
    try:
        datetime.strptime(build_timestamp, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError as error:
        raise ValueError(
            "build timestamp must use UTC format YYYY-MM-DDTHH:MM:SSZ"
        ) from error


def _validate_archive_member(information: ZipInfo, seen: set[str]) -> PurePosixPath:
    name = information.filename
    if not name or "\\" in name:
        raise ValueError("archive contains an invalid member name")
    member = PurePosixPath(name)
    if member.is_absolute() or ".." in member.parts:
        raise ValueError(f"archive member escapes the approved roots: {name}")
    if len(member.parts) < 2 or member.parts[0] not in {"public", "vendor"}:
        raise ValueError(f"archive contains an unapproved root: {name}")
    if name in seen:
        raise ValueError(f"archive contains a duplicate member: {name}")
    seen.add(name)

    mode = information.external_attr >> 16
    if stat.S_ISLNK(mode):
        raise ValueError(f"archive contains a symlink: {name}")
    file_type = stat.S_IFMT(mode)
    if information.is_dir():
        if file_type not in {0, stat.S_IFDIR}:
            raise ValueError(f"archive contains a non-directory member: {name}")
    elif file_type not in {0, stat.S_IFREG}:
        raise ValueError(f"archive contains a non-regular member: {name}")
    return member


def extract_approved_archive(archive: Path, destination: Path) -> None:
    """Extract only regular public/ and vendor/ members from an approved ZIP."""

    archive = Path(archive)
    destination = Path(destination)
    if destination.exists() or destination.is_symlink():
        raise ValueError("archive destination must not already exist")

    with ZipFile(archive) as package:
        seen: set[str] = set()
        validated = [
            (information, _validate_archive_member(information, seen))
            for information in package.infolist()
        ]
        if not validated:
            raise ValueError("archive contains no approved files")

        destination.mkdir(parents=True, mode=0o755)
        try:
            for information, member in validated:
                target = destination.joinpath(*member.parts)
                if information.is_dir():
                    target.mkdir(parents=True, exist_ok=True, mode=0o755)
                    continue
                target.parent.mkdir(parents=True, exist_ok=True, mode=0o755)
                with package.open(information) as source, target.open("xb") as output:
                    shutil.copyfileobj(source, output)
                target.chmod(0o644)
        except Exception:
            shutil.rmtree(destination)
            raise


def environment_bindings(environment: str, source_sha: str) -> str:
    """Return the two reviewed Apache bindings for one immutable release."""

    settings = _environment(environment)
    _validate_source_sha(source_sha)
    autoload_path = f"{settings['releaseRoot']}/{source_sha}/vendor/autoload.php"
    return (
        f'SetEnv STRONGER_HOME_CONFIG "{settings["configPath"]}"\n'
        f'SetEnv STRONGER_HOME_AUTOLOAD "{autoload_path}"\n'
    )


def deployment_script(environment: str, source_sha: str) -> str:
    """Generate guarded, reversible cPanel deployment instructions."""

    settings = _environment(environment)
    _validate_source_sha(source_sha)
    return f"""#!/bin/bash
set -Eeuo pipefail
umask 027

readonly ACCOUNT_HOME='{ACCOUNT_HOME}'
readonly REPOSITORY_ROOT='{settings["repositoryRoot"]}'
readonly DOCUMENT_ROOT='{settings["documentRoot"]}'
readonly CONFIG_PATH='{settings["configPath"]}'
readonly RELEASE_ROOT='{settings["releaseRoot"]}'
readonly SOURCE_SHA='{source_sha}'
readonly RELEASE_DIRECTORY="$RELEASE_ROOT/$SOURCE_SHA"
readonly NEXT_DIRECTORY="$DOCUMENT_ROOT.next-$SOURCE_SHA"
readonly PREVIOUS_DIRECTORY="$RELEASE_DIRECTORY/previous-public"

fail() {{
  printf '%s\n' "$1" >&2
  exit 1
}}

[[ "${{HOME:-}}" == "$ACCOUNT_HOME" ]] || fail 'Unexpected cPanel account home.'
[[ "$(pwd -P)" == "$REPOSITORY_ROOT" ]] || fail 'Unexpected cPanel repository root.'
[[ -d public && ! -L public && -f public/.htaccess && ! -L public/.htaccess ]] || fail 'Missing public release tree.'
[[ -d public/api/src && ! -L public/api/src ]] || fail 'Missing application source tree.'
[[ -d vendor && ! -L vendor && -f vendor/autoload.php && ! -L vendor/autoload.php ]] || fail 'Missing vendor release tree.'
[[ -f "$CONFIG_PATH" && ! -L "$CONFIG_PATH" ]] || fail 'Missing external environment configuration.'
[[ ! -e "$RELEASE_DIRECTORY" && ! -L "$RELEASE_DIRECTORY" ]] || fail 'Release directory already exists.'
[[ ! -e "$NEXT_DIRECTORY" && ! -L "$NEXT_DIRECTORY" ]] || fail 'Next document-root directory already exists.'

mkdir -p -- "$RELEASE_ROOT"
mkdir -- "$RELEASE_DIRECTORY"
cp -a -- vendor "$RELEASE_DIRECTORY/vendor"
mkdir -p -- "$RELEASE_DIRECTORY/site/api"
cp -a -- public/api/src "$RELEASE_DIRECTORY/site/api/src"
cp -a -- public "$NEXT_DIRECTORY"

swap_pending=0
restore_previous() {{
  local status=$?
  if [[ "$swap_pending" -eq 1 && ! -e "$DOCUMENT_ROOT" && -d "$PREVIOUS_DIRECTORY" ]]; then
    mv -- "$PREVIOUS_DIRECTORY" "$DOCUMENT_ROOT" || true
  fi
  exit "$status"
}}
trap restore_previous EXIT

swap_pending=1
mv -- "$DOCUMENT_ROOT" "$PREVIOUS_DIRECTORY"
mv -- "$NEXT_DIRECTORY" "$DOCUMENT_ROOT"
swap_pending=0
printf '%s\n' "$SOURCE_SHA" > "$RELEASE_DIRECTORY/deployed-source-sha"
trap - EXIT
"""


def _configure_htaccess(htaccess: Path, environment: str, bindings: str) -> None:
    if not htaccess.is_file() or htaccess.is_symlink():
        raise ValueError("release archive is missing public/.htaccess")
    content = htaccess.read_text(encoding="utf-8")
    if any(marker in content for marker in ENVIRONMENT_MARKERS):
        raise ValueError("release archive already contains an environment binding")
    if content.count(SHARED_HOST_RULES) != 1:
        raise ValueError("release archive has unexpected shared host rules")
    content = content.replace(
        SHARED_HOST_RULES,
        ENVIRONMENT_HOST_RULES[environment],
        1,
    )
    separator = "" if content.endswith("\n") else "\n"
    htaccess.write_text(content + separator + bindings, encoding="utf-8")


def build_git_release(
    project_root: Path,
    output_directory: Path,
    environment: str,
    source_sha: str,
    build_timestamp: str,
) -> Path:
    """Build one validated deployment-branch directory without partial output."""

    settings = _environment(environment)
    validate_provenance(source_sha, build_timestamp)
    project_root = Path(project_root).resolve()
    output_directory = Path(output_directory).resolve()
    if output_directory.exists() or output_directory.is_symlink():
        raise ValueError("output directory already exists")
    output_directory.parent.mkdir(parents=True, exist_ok=True)

    with TemporaryDirectory(
        prefix=f".{output_directory.name}-", dir=output_directory.parent
    ) as temporary:
        temporary_root = Path(temporary)
        archive = package_site(
            project_root,
            temporary_root / "package",
            environment,
        )
        release = temporary_root / "release"
        extract_approved_archive(archive, release)

        autoload = release / "vendor/autoload.php"
        if not autoload.is_file() or autoload.is_symlink():
            raise ValueError("release archive is missing vendor/autoload.php")
        _configure_htaccess(
            release / "public/.htaccess",
            environment,
            environment_bindings(environment, source_sha),
        )

        metadata = {
            "buildTimestamp": build_timestamp,
            "deploymentBranch": settings["deploymentBranch"],
            "environment": environment,
            "hostname": settings["hostname"],
            "sourceBranch": settings["sourceBranch"],
            "sourceSha": source_sha,
        }
        (release / ".cpanel.yml").write_text(
            CPANEL_CONFIGURATION,
            encoding="utf-8",
        )
        deploy = release / "deploy.sh"
        deploy.write_text(deployment_script(environment, source_sha), encoding="utf-8")
        deploy.chmod(0o755)
        (release / "release.json").write_text(
            json.dumps(metadata, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        release.rename(output_directory)

    return output_directory


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--environment", required=True)
    parser.add_argument("--source-sha", required=True)
    parser.add_argument("--build-timestamp", required=True)
    parser.add_argument("--output-directory", required=True, type=Path)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="Project root (defaults to the parent of scripts/).",
    )
    arguments = parser.parse_args(argv)
    try:
        release = build_git_release(
            arguments.root,
            arguments.output_directory,
            arguments.environment,
            arguments.source_sha,
            arguments.build_timestamp,
        )
    except (BadZipFile, OSError, ValueError) as error:
        print(f"Release build failed: {error}", file=sys.stderr)
        return 1

    digest = hashlib.sha256((release / "release.json").read_bytes()).hexdigest()
    print(f"Created {release}")
    print(f"release.json SHA-256: {digest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
