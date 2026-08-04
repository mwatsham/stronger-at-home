import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image

from scripts.validate_brand import contrast_ratio, validate_project


VALID_HYBRID_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1160 340">
  <title>Stronger at Home Physiotherapy by Melanie Watsham</title>
  <desc>An open-bottom home above a supporting outlined hand, with a moving person and three ascending steps, beside the Stronger at Home Physiotherapy wordmark.</desc>
  <path fill="none" stroke="#203E55" d="M10 100 L50 50 L90 100"/>
  <circle fill="#203E55" cx="40" cy="75" r="5"/>
  <rect fill="#C3A26E" x="50" y="80" width="20" height="5"/>
  <text fill="#203E55" x="120" y="80">Stronger at Home</text>
  <text fill="#203E55" x="120" y="110">Physiotherapy</text>
  <text fill="#203E55" x="120" y="130">by Melanie Watsham</text>
</svg>
"""

RASTER_ASSETS = {
    "primary_raster_logo_2048": {
        "id": "logo_primary_raster_2048",
        "filename": "logo-primary-raster-2048.png",
        "size": (2048, 640),
    },
    "primary_raster_logo_512": {
        "id": "logo_primary_raster_512",
        "filename": "logo-primary-raster-512.png",
        "size": (512, 160),
    },
}


def _write_manifest(root: Path, assets: list[dict[str, object]]) -> None:
    manifest_path = root / "brand/assets/manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(
        json.dumps({"schema_version": "1.0", "assets": assets}),
        encoding="utf-8",
    )


def _write_default_rasters(root: Path) -> list[dict[str, object]]:
    assets = []
    for role, configuration in RASTER_ASSETS.items():
        asset_path = root / "brand/assets/source" / configuration["filename"]
        asset_path.parent.mkdir(parents=True, exist_ok=True)
        Image.new("RGB", configuration["size"], (249, 244, 242)).save(asset_path)
        assets.append(
            {
                "id": configuration["id"],
                "role": role,
                "path": f"brand/assets/source/{configuration['filename']}",
                "status": "proposed",
                "sha256": hashlib.sha256(asset_path.read_bytes()).hexdigest(),
                "reviewed_by": None,
                "reviewed_on": None,
            }
        )
    return assets


def write_asset_project(
    root: Path,
    *,
    svg_text: str = VALID_HYBRID_SVG,
    role: str = "primary_hybrid_logo",
    status: str = "deprecated",
    reviewed_by: str | None = None,
    reviewed_on: str | None = None,
    sha256: str | None = None,
) -> None:
    asset_path = root / "brand/assets/source/logo-primary-hybrid.svg"
    asset_path.parent.mkdir(parents=True)
    asset_path.write_text(svg_text, encoding="utf-8")
    assets = [
        {
            "id": "logo_primary_hybrid",
            "role": role,
            "path": "brand/assets/source/logo-primary-hybrid.svg",
            "status": status,
            "sha256": sha256
            or hashlib.sha256(asset_path.read_bytes()).hexdigest(),
            "reviewed_by": reviewed_by,
            "reviewed_on": reviewed_on,
        },
        *_write_default_rasters(root),
    ]
    _write_manifest(root, assets)


def write_raster_asset(
    root: Path,
    *,
    role: str = "primary_raster_logo_2048",
    size: tuple[int, int] | None = None,
    mode: str = "RGB",
    transparency: tuple[int, int, int] | None = None,
    status: str = "proposed",
    reviewed_by: str | None = None,
    reviewed_on: str | None = None,
) -> None:
    configuration = RASTER_ASSETS[role]
    source_directory = root / "brand/assets/source"
    source_directory.mkdir(parents=True, exist_ok=True)
    hybrid_path = source_directory / "logo-primary-hybrid.svg"
    hybrid_path.write_text(VALID_HYBRID_SVG, encoding="utf-8")
    assets: list[dict[str, object]] = [
        {
            "id": "logo_primary_hybrid_historical",
            "role": "primary_hybrid_logo",
            "path": "brand/assets/source/logo-primary-hybrid.svg",
            "status": "deprecated",
            "sha256": hashlib.sha256(hybrid_path.read_bytes()).hexdigest(),
            "reviewed_by": None,
            "reviewed_on": None,
        }
    ]
    for current_role, current_configuration in RASTER_ASSETS.items():
        filename = current_configuration["filename"]
        asset_path = source_directory / filename
        is_target = current_role == role
        image_mode = mode if is_target else "RGB"
        image_size = (
            size if is_target and size is not None else current_configuration["size"]
        )
        colour = (
            (249, 244, 242, 255)
            if image_mode == "RGBA"
            else (249, 244, 242)
        )
        image = Image.new(image_mode, image_size, colour)
        if is_target and transparency is not None:
            image.save(asset_path, transparency=transparency)
        else:
            image.save(asset_path)
        assets.append(
            {
                "id": current_configuration["id"],
                "role": current_role,
                "path": f"brand/assets/source/{filename}",
                "status": status if is_target else "proposed",
                "sha256": hashlib.sha256(asset_path.read_bytes()).hexdigest(),
                "reviewed_by": reviewed_by if is_target else None,
                "reviewed_on": reviewed_on if is_target else None,
            }
        )
    _write_manifest(root, assets)


class BrandValidationTests(unittest.TestCase):
    def test_approved_primary_pairs_exceed_wcag_aa(self):
        self.assertGreaterEqual(contrast_ratio("#203E55", "#E8F1F6"), 4.5)
        self.assertGreaterEqual(contrast_ratio("#F7F2E8", "#203E55"), 4.5)

    def test_missing_sources_are_reported(self):
        with TemporaryDirectory() as directory:
            errors = validate_project(Path(directory))
        self.assertIn("Missing required file: BRAND.md", errors)
        self.assertIn("Missing required file: brand/tokens.json", errors)

    def test_invalid_decision_status_is_reported(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "DECISIONS.md").write_text(
                "| D-1 | Test | final | Owner | 2026-08-03 |", encoding="utf-8"
            )
            errors = validate_project(root)
        self.assertIn("Invalid decision status in DECISIONS.md: final", errors)

    def test_source_serif_requires_its_licence_file(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            font = root / "brand/fonts/source-serif-4.ttf"
            font.parent.mkdir(parents=True)
            font.write_bytes(b"font")

            errors = validate_project(root)

        self.assertIn(
            "Missing font licence: brand/fonts/OFL-source-serif.txt", errors
        )

    def test_atkinson_hyperlegible_requires_its_licence_file(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            font = root / "brand/fonts/atkinson-hyperlegible-next.ttf"
            font.parent.mkdir(parents=True)
            font.write_bytes(b"font")

            errors = validate_project(root)

        self.assertIn("Missing font licence: brand/fonts/OFL-atkinson.txt", errors)

    def test_valid_deprecated_hybrid_asset_has_no_asset_validation_errors(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root)

            errors = validate_project(root)

        self.assertFalse(
            [error for error in errors if error.startswith(("Asset ", "Hybrid logo "))]
        )

    def test_embedded_raster_image_is_rejected(self):
        svg = VALID_HYBRID_SVG.replace(
            "</svg>", '<image href="data:image/png;base64,AAAA"/></svg>'
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root, svg_text=svg)

            errors = validate_project(root)

        self.assertIn("Hybrid logo must not contain embedded image elements", errors)

    def test_missing_accessible_title_and_description_are_rejected(self):
        svg = VALID_HYBRID_SVG.replace(
            "  <title>Stronger at Home Physiotherapy by Melanie Watsham</title>\n",
            "",
        ).replace(
            "  <desc>An open-bottom home above a supporting outlined hand, with a moving person and three ascending steps, beside the Stronger at Home Physiotherapy wordmark.</desc>\n",
            "",
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root, svg_text=svg)

            errors = validate_project(root)

        self.assertIn("Hybrid logo is missing an accessible title", errors)
        self.assertIn("Hybrid logo is missing an accessible description", errors)

    def test_accessible_title_must_match_exactly(self):
        svg = VALID_HYBRID_SVG.replace(
            "Stronger at Home Physiotherapy by Melanie Watsham</title>",
            "Stronger at Home Physiotherapy by Melanie Watsham draft</title>",
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root, svg_text=svg)

            errors = validate_project(root)

        self.assertIn(
            "Hybrid logo title must equal: Stronger at Home Physiotherapy by Melanie Watsham",
            errors,
        )

    def test_accessible_description_must_match_exactly(self):
        svg = VALID_HYBRID_SVG.replace(
            "Physiotherapy wordmark.</desc>",
            "Physiotherapy wordmark. Draft artwork.</desc>",
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root, svg_text=svg)

            errors = validate_project(root)

        self.assertIn(
            "Hybrid logo description must equal: An open-bottom home above a supporting outlined hand, with a moving person and three ascending steps, beside the Stronger at Home Physiotherapy wordmark.",
            errors,
        )

    def test_missing_required_editable_text_is_rejected(self):
        svg = VALID_HYBRID_SVG.replace(
            '<text fill="#203E55" x="120" y="130">by Melanie Watsham</text>',
            '<path fill="#203E55" d="M120 130h80"/>',
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root, svg_text=svg)

            errors = validate_project(root)

        self.assertIn(
            "Hybrid logo is missing editable text: by Melanie Watsham", errors
        )

    def test_disallowed_primary_artwork_colour_is_rejected(self):
        svg = VALID_HYBRID_SVG.replace("#C3A26E", "#FFFFFF")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root, svg_text=svg)

            errors = validate_project(root)

        self.assertIn("Hybrid logo uses disallowed colour: #FFFFFF", errors)

    def test_disallowed_inline_style_colour_is_rejected(self):
        svg = VALID_HYBRID_SVG.replace(
            'fill="#203E55"', 'style="fill:#FFFFFF"', 1
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root, svg_text=svg)

            errors = validate_project(root)

        self.assertIn("Hybrid logo uses disallowed colour: #FFFFFF", errors)

    def test_disallowed_named_css_colour_is_rejected(self):
        svg = VALID_HYBRID_SVG.replace(
            "  <title>", "  <style>path { fill: white; }</style>\n  <title>"
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root, svg_text=svg)

            errors = validate_project(root)

        self.assertIn("Hybrid logo uses disallowed colour: white", errors)

    def test_manifest_hash_mismatch_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root, sha256="0" * 64)

            errors = validate_project(root)

        self.assertIn(
            "Asset hash mismatch: brand/assets/source/logo-primary-hybrid.svg",
            errors,
        )

    def test_approved_logo_requires_melanie_and_iso_review_date(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root, status="approved")

            errors = validate_project(root)

        self.assertIn(
            "Approved asset logo_primary_hybrid must be reviewed by Melanie Watsham",
            errors,
        )
        self.assertIn(
            "Approved asset logo_primary_hybrid must have an ISO review date", errors
        )

    def test_proposed_logo_rejects_review_metadata(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(
                root,
                status="proposed",
                reviewed_by="Melanie Watsham",
                reviewed_on="2026-08-03",
            )

            errors = validate_project(root)

        self.assertIn(
            "Proposed asset logo_primary_hybrid must not have review metadata",
            errors,
        )

    def test_non_logo_asset_does_not_require_logo_approval_metadata(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root, role="supporting_document", status="approved")

            errors = validate_project(root)

        self.assertNotIn(
            "Approved asset logo_primary_hybrid must be reviewed by Melanie Watsham",
            errors,
        )
        self.assertNotIn(
            "Approved asset logo_primary_hybrid must have an ISO review date", errors
        )

    def test_each_primary_raster_role_requires_its_exact_dimensions(self):
        cases = {
            "primary_raster_logo_2048": ((2047, 640), "2048 × 640"),
            "primary_raster_logo_512": ((511, 160), "512 × 160"),
        }
        for role, (invalid_size, expected_size) in cases.items():
            with self.subTest(role=role), TemporaryDirectory() as directory:
                root = Path(directory)
                write_raster_asset(root, role=role, size=invalid_size)
                errors = validate_project(root)
            self.assertIn(
                f"Raster logo {role} must be {expected_size} pixels",
                errors,
            )

    def test_each_primary_raster_role_accepts_its_exact_opaque_png(self):
        for role in RASTER_ASSETS:
            with self.subTest(role=role), TemporaryDirectory() as directory:
                root = Path(directory)
                write_raster_asset(root, role=role)
                errors = validate_project(root)
            self.assertFalse(
                [error for error in errors if f"Raster logo {role}" in error]
            )

    def test_each_primary_raster_role_must_be_opaque_rgb_png(self):
        for role in RASTER_ASSETS:
            with self.subTest(role=role), TemporaryDirectory() as directory:
                root = Path(directory)
                write_raster_asset(root, role=role, mode="RGBA")
                errors = validate_project(root)
            self.assertIn(
                f"Raster logo {role} must use opaque RGB mode",
                errors,
            )

    def test_primary_raster_rejects_png_transparency(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_raster_asset(root, transparency=(1, 2, 3))
            errors = validate_project(root)
        self.assertIn(
            "Raster logo primary_raster_logo_2048 must use opaque RGB mode",
            errors,
        )

    def test_primary_raster_does_not_use_svg_validation(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_raster_asset(root)
            errors = validate_project(root)
        self.assertFalse(
            [error for error in errors if error.startswith("Invalid hybrid logo SVG:")]
        )

    def test_active_primary_svg_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root, status="proposed")
            errors = validate_project(root)
        self.assertIn(
            "Active primary logo must not be SVG: "
            "brand/assets/source/logo-primary-hybrid.svg",
            errors,
        )

    def test_immutable_raster_source_is_required(self):
        with TemporaryDirectory() as directory:
            errors = validate_project(Path(directory))
        self.assertIn(
            "Missing immutable raster source: "
            "docs/superpowers/specs/assets/"
            "home-physiotherapy-logo-approved-concept-v2.png",
            errors,
        )

    def test_deprecated_primary_svg_is_retained_as_history(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root, status="deprecated")
            errors = validate_project(root)
        self.assertNotIn(
            "Active primary logo must not be SVG: "
            "brand/assets/source/logo-primary-hybrid.svg",
            errors,
        )

    def test_each_approved_raster_requires_melanie_and_iso_date(self):
        for role, configuration in RASTER_ASSETS.items():
            with self.subTest(role=role), TemporaryDirectory() as directory:
                root = Path(directory)
                write_raster_asset(root, role=role, status="approved")
                errors = validate_project(root)
            asset_id = configuration["id"]
            self.assertIn(
                f"Approved asset {asset_id} must be reviewed by Melanie Watsham",
                errors,
            )
            self.assertIn(
                f"Approved asset {asset_id} must have an ISO review date",
                errors,
            )

    def test_each_approved_raster_accepts_valid_approval_metadata(self):
        for role, configuration in RASTER_ASSETS.items():
            with self.subTest(role=role), TemporaryDirectory() as directory:
                root = Path(directory)
                write_raster_asset(
                    root,
                    role=role,
                    status="approved",
                    reviewed_by="Melanie Watsham",
                    reviewed_on="2026-08-04",
                )
                errors = validate_project(root)
            asset_id = configuration["id"]
            self.assertFalse(
                [error for error in errors if f"asset {asset_id}" in error]
            )

    def test_manifest_requires_exactly_one_canonical_entry_for_each_logo_role(self):
        for missing_role in (
            "primary_hybrid_logo",
            "primary_raster_logo_2048",
            "primary_raster_logo_512",
        ):
            with self.subTest(missing_role=missing_role), TemporaryDirectory() as directory:
                root = Path(directory)
                write_raster_asset(root)
                manifest_path = root / "brand/assets/manifest.json"
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                manifest["assets"] = [
                    asset
                    for asset in manifest["assets"]
                    if asset["role"] != missing_role
                ]
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                errors = validate_project(root)
            self.assertIn(
                f"Asset manifest must contain exactly one {missing_role} entry",
                errors,
            )

    def test_empty_asset_manifest_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            _write_manifest(root, [])
            errors = validate_project(root)
        for role in (
            "primary_hybrid_logo",
            "primary_raster_logo_2048",
            "primary_raster_logo_512",
        ):
            self.assertIn(
                f"Asset manifest must contain exactly one {role} entry", errors
            )

    def test_duplicate_required_role_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_raster_asset(root)
            manifest_path = root / "brand/assets/manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            duplicate = dict(manifest["assets"][1])
            duplicate["id"] = "duplicate_raster"
            manifest["assets"].append(duplicate)
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            errors = validate_project(root)
        self.assertIn(
            "Asset manifest must contain exactly one primary_raster_logo_2048 entry",
            errors,
        )

    def test_required_historical_svg_role_must_be_deprecated(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_raster_asset(root)
            manifest_path = root / "brand/assets/manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            historical = next(
                asset
                for asset in manifest["assets"]
                if asset["role"] == "primary_hybrid_logo"
            )
            historical["status"] = "proposed"
            manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
            errors = validate_project(root)
        self.assertIn(
            "Historical primary_hybrid_logo asset must have deprecated status",
            errors,
        )

    def test_required_roles_reject_noncanonical_paths(self):
        expected_paths = {
            "primary_hybrid_logo": "brand/assets/source/logo-primary-hybrid.svg",
            "primary_raster_logo_2048": "brand/assets/source/logo-primary-raster-2048.png",
            "primary_raster_logo_512": "brand/assets/source/logo-primary-raster-512.png",
        }
        for role, expected_path in expected_paths.items():
            with self.subTest(role=role), TemporaryDirectory() as directory:
                root = Path(directory)
                write_raster_asset(root)
                manifest_path = root / "brand/assets/manifest.json"
                manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
                entry = next(
                    asset for asset in manifest["assets"] if asset["role"] == role
                )
                original_path = root / entry["path"]
                wrong_path = original_path.with_name(f"wrong-{original_path.name}")
                wrong_path.write_bytes(original_path.read_bytes())
                entry["path"] = wrong_path.relative_to(root).as_posix()
                entry["sha256"] = hashlib.sha256(wrong_path.read_bytes()).hexdigest()
                manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
                errors = validate_project(root)
            self.assertIn(
                f"Asset role {role} must use canonical path: {expected_path}", errors
            )

    def test_missing_required_raster_file_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_raster_asset(root, role="primary_raster_logo_512")
            missing_path = root / "brand/assets/source/logo-primary-raster-512.png"
            missing_path.unlink()
            errors = validate_project(root)
        self.assertIn(
            "Asset path does not exist: brand/assets/source/logo-primary-raster-512.png",
            errors,
        )

    def test_unmanaged_source_svg_is_rejected(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_raster_asset(root)
            unmanaged = root / "brand/assets/source/logo-unmanaged.svg"
            unmanaged.write_text(VALID_HYBRID_SVG, encoding="utf-8")
            errors = validate_project(root)
        self.assertIn(
            "Unmanaged SVG asset in brand/assets/source: "
            "brand/assets/source/logo-unmanaged.svg",
            errors,
        )

    def test_unmanaged_source_svg_check_is_case_insensitive(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_raster_asset(root)
            unmanaged = root / "brand/assets/source/logo-unmanaged.SVG"
            unmanaged.write_text(VALID_HYBRID_SVG, encoding="utf-8")
            errors = validate_project(root)
        self.assertIn(
            "Unmanaged SVG asset in brand/assets/source: "
            "brand/assets/source/logo-unmanaged.SVG",
            errors,
        )
