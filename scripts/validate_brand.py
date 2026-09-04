from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

try:
    from PIL import Image, UnidentifiedImageError
except ModuleNotFoundError as error:
    if error.name != "PIL":
        raise
    raise RuntimeError(
        "Brand validation requires Pillow; install the pinned project "
        "dependencies from requirements.txt."
    ) from error

try:
    from scripts.generate_brand_tokens import render_css
except ImportError:
    from generate_brand_tokens import render_css

ALLOWED_ASSET_STATUSES = {"approved", "proposed", "rejected", "deprecated"}
ALLOWED_DECISION_STATUSES = ALLOWED_ASSET_STATUSES | {"superseded"}
REQUIRED_FILES = (
    "BRAND.md",
    "DECISIONS.md",
    "MEMORY.md",
    "brand/strategy.md",
    "brand/messaging.md",
    "brand/identity.md",
    "brand/clearance.md",
    "brand/tokens.json",
    ".ai/context/brand.json",
    "brand/assets/manifest.json",
    "requirements.txt",
)
FONT_LICENCE_PAIRS = {
    "brand/fonts/source-serif-4.ttf": "brand/fonts/OFL-source-serif.txt",
    "brand/fonts/atkinson-hyperlegible-next.ttf": "brand/fonts/OFL-atkinson.txt",
}
ALLOWED_LOGO_COLOURS = {"#203E55", "#C3A26E"}
REQUIRED_LOGO_TEXT = (
    "Stronger at Home",
    "Physiotherapy",
    "by Melanie Watsham",
)
REQUIRED_LOGO_TITLE = "Stronger at Home Physiotherapy by Melanie Watsham"
REQUIRED_LOGO_DESCRIPTION = (
    "An open-bottom home above a supporting outlined hand, with a moving person "
    "and three ascending steps, beside the Stronger at Home Physiotherapy "
    "wordmark."
)
SVG_PAINT_ATTRIBUTES = {"color", "fill", "flood-color", "stop-color", "stroke"}
CSS_PAINT_DECLARATION = re.compile(
    r"(?<![\w-])(?:color|fill|flood-color|stop-color|stroke)\s*:\s*([^;}]+)",
    re.IGNORECASE,
)
IMMUTABLE_RASTER_SOURCE = Path(
    "docs/superpowers/specs/assets/"
    "home-physiotherapy-logo-approved-concept-v2.png"
)
IMMUTABLE_RASTER_SOURCE_SHA256 = (
    "41267865711ca55f9225df8370c50bca823f68ca966b8fc216852e65a36d0ef1"
)
PRIMARY_RASTER_SIZES = {
    "primary_raster_logo_2048": (2048, 640),
    "primary_raster_logo_512": (512, 160),
}
HISTORICAL_RASTER_SIZES = {
    "historical_raster_logo_2048": (2048, 640),
    "historical_raster_logo_512": (512, 160),
}
RASTER_SIZES = PRIMARY_RASTER_SIZES | HISTORICAL_RASTER_SIZES
HISTORICAL_RASTER_ROLES = set(HISTORICAL_RASTER_SIZES)
PRIMARY_LOGO_ROLES = set(PRIMARY_RASTER_SIZES) | {"primary_hybrid_logo"}
REQUIRED_ASSET_PATHS = {
    "primary_hybrid_logo": "brand/assets/source/logo-primary-hybrid.svg",
    "primary_raster_logo_2048": "brand/assets/source/logo-primary-raster-v2-2048.png",
    "primary_raster_logo_512": "brand/assets/source/logo-primary-raster-v2-512.png",
    "historical_raster_logo_2048": "brand/assets/source/logo-primary-raster-2048.png",
    "historical_raster_logo_512": "brand/assets/source/logo-primary-raster-512.png",
}
CURRENT_PRIMARY_RASTER_RECORDS = {
    "primary_raster_logo_2048": {
        "sha256": "4e8988e571269353aed86697468e0a60b838bc1e121c8e590f974d5124df3683",
        "reviewed_on": "2026-08-05",
    },
    "primary_raster_logo_512": {
        "sha256": "d557a0e8fd05efc86fcca2b3f63d807ad33f29527062697705a8e05616c6db39",
        "reviewed_on": "2026-08-05",
    },
}
HISTORICAL_RASTER_RECORDS = {
    "historical_raster_logo_2048": {
        "sha256": "108c7bf9175868c4dffe15be6b2e4433346093d1f9d692752851a4b9d9bd5864",
        "reviewed_on": "2026-08-04",
    },
    "historical_raster_logo_512": {
        "sha256": "153f964143d1fadae66595871c6bbef5d3a336260bf28f6229043eaf91a23afd",
        "reviewed_on": "2026-08-04",
    },
}


def _relative_luminance(hex_colour: str) -> float:
    if not re.fullmatch(r"#[0-9A-Fa-f]{6}", hex_colour):
        raise ValueError(f"Invalid hex colour: {hex_colour}")
    channels = [int(hex_colour[index:index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4 for value in channels]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def _local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def _element_text(element: ET.Element | None) -> str:
    if element is None:
        return ""
    return " ".join("".join(element.itertext()).split())


def _css_paint_values(declarations: str) -> set[str]:
    values = set()
    for match in CSS_PAINT_DECLARATION.finditer(declarations):
        value = re.sub(
            r"\s*!important\s*$", "", match.group(1).strip(), flags=re.IGNORECASE
        )
        values.add(value)
    return values


def _validate_hybrid_logo(path: Path) -> list[str]:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as error:
        return [f"Invalid hybrid logo SVG: {error}"]

    errors: list[str] = []
    elements = list(root.iter())
    if any(_local_name(element.tag) == "image" for element in elements):
        errors.append("Hybrid logo must not contain embedded image elements")

    title = next(
        (element for element in elements if _local_name(element.tag) == "title"),
        None,
    )
    description = next(
        (element for element in elements if _local_name(element.tag) == "desc"),
        None,
    )
    title_text = _element_text(title)
    if not title_text:
        errors.append("Hybrid logo is missing an accessible title")
    elif title_text != REQUIRED_LOGO_TITLE:
        errors.append(f"Hybrid logo title must equal: {REQUIRED_LOGO_TITLE}")
    description_text = _element_text(description)
    if not description_text:
        errors.append("Hybrid logo is missing an accessible description")
    elif description_text != REQUIRED_LOGO_DESCRIPTION:
        errors.append(
            f"Hybrid logo description must equal: {REQUIRED_LOGO_DESCRIPTION}"
        )

    editable_text = {
        _element_text(element)
        for element in elements
        if _local_name(element.tag) == "text"
    }
    for required_text in REQUIRED_LOGO_TEXT:
        if required_text not in editable_text:
            errors.append(f"Hybrid logo is missing editable text: {required_text}")

    colours: set[str] = set()
    for element in elements:
        for attribute, value in element.attrib.items():
            if _local_name(attribute) in SVG_PAINT_ATTRIBUTES:
                paint = value.strip()
                if paint.lower() != "none":
                    colours.add(paint)
            elif _local_name(attribute) == "style":
                colours.update(_css_paint_values(value))
        if _local_name(element.tag) == "style" and element.text:
            colours.update(_css_paint_values(element.text))
    for colour in sorted(colours):
        if colour.upper() not in ALLOWED_LOGO_COLOURS:
            errors.append(f"Hybrid logo uses disallowed colour: {colour}")

    return errors


def _is_iso_date(value: object) -> bool:
    if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return False
    try:
        date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _validate_raster_logo(path: Path, role: str) -> list[str]:
    expected_size = RASTER_SIZES[role]
    try:
        with Image.open(path) as image:
            image.load()
            image_format = image.format
            size = image.size
            mode = image.mode
            transparency = image.info.get("transparency")
    except (OSError, UnidentifiedImageError) as error:
        return [f"Invalid raster logo {role}: {error}"]
    errors = []
    if image_format != "PNG":
        errors.append(f"Raster logo {role} must be PNG")
    if size != expected_size:
        errors.append(
            f"Raster logo {role} must be "
            f"{expected_size[0]} × {expected_size[1]} pixels"
        )
    if mode != "RGB" or transparency is not None:
        errors.append(f"Raster logo {role} must use opaque RGB mode")
    return errors


def _validate_raster_approval_record(asset: dict[str, object]) -> list[str]:
    role = asset.get("role")
    asset_id = asset.get("id") or "<unknown>"
    if role in CURRENT_PRIMARY_RASTER_RECORDS:
        record = CURRENT_PRIMARY_RASTER_RECORDS[role]
        label = f"Current primary raster asset {asset_id}"
        expected_status = "approved"
        hash_label = "approved"
    elif role in HISTORICAL_RASTER_RECORDS:
        record = HISTORICAL_RASTER_RECORDS[role]
        label = f"Historical raster asset {asset_id}"
        expected_status = "deprecated"
        hash_label = "original"
    else:
        return []

    errors = []
    if asset.get("status") != expected_status:
        if role in HISTORICAL_RASTER_RECORDS:
            errors.append(f"{label} must be deprecated")
        else:
            errors.append(f"{label} must have status approved")
    if asset.get("reviewed_by") != "Melanie Watsham":
        errors.append(f"{label} must be reviewed by Melanie Watsham")
    if asset.get("reviewed_on") != record["reviewed_on"]:
        errors.append(
            f"{label} must have approval date {record['reviewed_on']}"
        )
    if asset.get("sha256") != record["sha256"]:
        errors.append(
            f"{label} must have {hash_label} SHA-256 {record['sha256']}"
        )
    return errors


def _validate_asset_manifest(root: Path, manifest: object) -> list[str]:
    if not isinstance(manifest, dict):
        return ["Asset manifest must be a JSON object"]
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        return ["Asset manifest must contain an assets array"]

    errors: list[str] = []
    entries_by_role = {
        role: [
            asset
            for asset in assets
            if isinstance(asset, dict) and asset.get("role") == role
        ]
        for role in REQUIRED_ASSET_PATHS
    }
    for role, expected_path in REQUIRED_ASSET_PATHS.items():
        entries = entries_by_role[role]
        if len(entries) != 1:
            errors.append(f"Asset manifest must contain exactly one {role} entry")
            continue
        if entries[0].get("path") != expected_path:
            errors.append(
                f"Asset role {role} must use canonical path: {expected_path}"
            )

    historical_entries = entries_by_role["primary_hybrid_logo"]
    if (
        len(historical_entries) == 1
        and historical_entries[0].get("status") != "deprecated"
    ):
        errors.append(
            "Historical primary_hybrid_logo asset must have deprecated status"
        )
    historical_svg_is_managed = (
        len(historical_entries) == 1
        and historical_entries[0].get("path")
        == REQUIRED_ASSET_PATHS["primary_hybrid_logo"]
        and historical_entries[0].get("status") == "deprecated"
    )
    source_directory = root / "brand/assets/source"
    if source_directory.is_dir():
        svg_paths = sorted(
            path
            for path in source_directory.rglob("*")
            if path.is_file() and path.suffix.lower() == ".svg"
        )
        for svg_path in svg_paths:
            relative_path = svg_path.relative_to(root).as_posix()
            if (
                relative_path != REQUIRED_ASSET_PATHS["primary_hybrid_logo"]
                or not historical_svg_is_managed
            ):
                errors.append(
                    "Unmanaged SVG asset in brand/assets/source: "
                    f"{relative_path}"
                )

    for asset in assets:
        if not isinstance(asset, dict):
            errors.append("Asset manifest entries must be JSON objects")
            continue
        asset_id = asset.get("id")
        relative_path = asset.get("path")
        if not isinstance(relative_path, str) or not relative_path:
            errors.append(f"Asset {asset_id or '<unknown>'} has an invalid path")
            continue
        asset_path = root / relative_path
        if not asset_path.is_file():
            errors.append(f"Asset path does not exist: {relative_path}")
            continue

        actual_hash = hashlib.sha256(asset_path.read_bytes()).hexdigest()
        expected_hash = asset.get("sha256")
        if not isinstance(expected_hash, str) or not re.fullmatch(
            r"[0-9a-f]{64}", expected_hash
        ):
            errors.append(f"Asset has invalid lowercase SHA-256: {relative_path}")
        elif expected_hash != actual_hash:
            errors.append(f"Asset hash mismatch: {relative_path}")

        status = asset.get("status")
        if status not in ALLOWED_ASSET_STATUSES:
            errors.append(f"Asset {asset_id or '<unknown>'} has invalid status: {status}")
        role = asset.get("role")
        if (
            role in PRIMARY_LOGO_ROLES
            and asset_path.suffix.lower() == ".svg"
            and status != "deprecated"
        ):
            errors.append(f"Active primary logo must not be SVG: {relative_path}")
        if role in RASTER_SIZES:
            errors.extend(_validate_raster_logo(asset_path, role))
        if role == "primary_hybrid_logo":
            errors.extend(_validate_hybrid_logo(asset_path))
        if role in RASTER_SIZES:
            errors.extend(_validate_raster_approval_record(asset))
        elif role in PRIMARY_LOGO_ROLES:
            if status == "approved":
                if asset.get("reviewed_by") != "Melanie Watsham":
                    errors.append(
                        f"Approved asset {asset_id or '<unknown>'} must be reviewed by Melanie Watsham"
                    )
                if not _is_iso_date(asset.get("reviewed_on")):
                    errors.append(
                        f"Approved asset {asset_id or '<unknown>'} must have an ISO review date"
                    )
            elif status == "proposed" and (
                asset.get("reviewed_by") is not None
                or asset.get("reviewed_on") is not None
            ):
                errors.append(
                    f"Proposed asset {asset_id or '<unknown>'} must not have review metadata"
                )
    return errors


def validate_project(root: Path) -> list[str]:
    errors = [f"Missing required file: {path}" for path in REQUIRED_FILES if not (root / path).is_file()]
    source_path = root / IMMUTABLE_RASTER_SOURCE
    if not source_path.is_file():
        errors.append(f"Missing immutable raster source: {IMMUTABLE_RASTER_SOURCE}")
    else:
        actual_source_hash = hashlib.sha256(source_path.read_bytes()).hexdigest()
        if actual_source_hash != IMMUTABLE_RASTER_SOURCE_SHA256:
            errors.append(
                f"Immutable raster source hash mismatch: {IMMUTABLE_RASTER_SOURCE}"
            )
    for font, licence in FONT_LICENCE_PAIRS.items():
        if (root / font).is_file() and not (root / licence).is_file():
            errors.append(f"Missing font licence: {licence}")
    decisions = root / "DECISIONS.md"
    if decisions.is_file():
        for line in decisions.read_text(encoding="utf-8").splitlines():
            if line.startswith("| D-"):
                columns = [value.strip() for value in line.strip("|").split("|")]
                if len(columns) >= 3 and columns[2] not in ALLOWED_DECISION_STATUSES:
                    errors.append(f"Invalid decision status in DECISIONS.md: {columns[2]}")
    for relative in ("brand/tokens.json", ".ai/context/brand.json", "brand/assets/manifest.json"):
        path = root / relative
        if path.is_file():
            try:
                json.loads(path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as error:
                errors.append(f"Invalid JSON: {relative}: {error.msg}")
    manifest_path = root / "brand/assets/manifest.json"
    if manifest_path.is_file():
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
        else:
            errors.extend(_validate_asset_manifest(root, manifest))
    token_source = root / "brand/tokens.json"
    generated_tokens = root / "brand/generated/tokens.css"
    if token_source.is_file() and generated_tokens.is_file():
        try:
            tokens = json.loads(token_source.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
        else:
            if generated_tokens.read_text(encoding="utf-8") != render_css(tokens):
                errors.append("Generated token drift: brand/generated/tokens.css")
    return errors


def main() -> int:
    errors = validate_project(Path.cwd())
    if errors:
        print("\n".join(errors))
        return 1
    print("Brand validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
