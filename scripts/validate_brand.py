from __future__ import annotations

from datetime import date
import hashlib
import json
from pathlib import Path
import re
import sys
import xml.etree.ElementTree as ET

try:
    from scripts.generate_brand_tokens import render_css
except ImportError:
    from generate_brand_tokens import render_css

ALLOWED_STATUSES = {"approved", "proposed", "rejected", "deprecated"}
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
SVG_PAINT_ATTRIBUTES = {"color", "fill", "flood-color", "stop-color", "stroke"}


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
    elif REQUIRED_LOGO_TITLE not in title_text:
        errors.append(f"Hybrid logo title must include: {REQUIRED_LOGO_TITLE}")
    if not _element_text(description):
        errors.append("Hybrid logo is missing an accessible description")

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
        if _local_name(element.tag) == "style" and element.text:
            colours.update(re.findall(r"#[0-9A-Fa-f]{6}", element.text))
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


def _validate_asset_manifest(root: Path, manifest: object) -> list[str]:
    if not isinstance(manifest, dict):
        return ["Asset manifest must be a JSON object"]
    assets = manifest.get("assets")
    if not isinstance(assets, list):
        return ["Asset manifest must contain an assets array"]

    errors: list[str] = []
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
        if status not in ALLOWED_STATUSES:
            errors.append(f"Asset {asset_id or '<unknown>'} has invalid status: {status}")
        if status == "approved":
            if asset.get("reviewed_by") != "Melanie Watsham":
                errors.append(
                    f"Approved asset {asset_id or '<unknown>'} must be reviewed by Melanie Watsham"
                )
            if not _is_iso_date(asset.get("reviewed_on")):
                errors.append(
                    f"Approved asset {asset_id or '<unknown>'} must have an ISO review date"
                )

        if asset.get("role") == "primary_hybrid_logo":
            errors.extend(_validate_hybrid_logo(asset_path))
    return errors


def validate_project(root: Path) -> list[str]:
    errors = [f"Missing required file: {path}" for path in REQUIRED_FILES if not (root / path).is_file()]
    for font, licence in FONT_LICENCE_PAIRS.items():
        if (root / font).is_file() and not (root / licence).is_file():
            errors.append(f"Missing font licence: {licence}")
    decisions = root / "DECISIONS.md"
    if decisions.is_file():
        for line in decisions.read_text(encoding="utf-8").splitlines():
            if line.startswith("| D-"):
                columns = [value.strip() for value in line.strip("|").split("|")]
                if len(columns) >= 3 and columns[2] not in ALLOWED_STATUSES:
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
