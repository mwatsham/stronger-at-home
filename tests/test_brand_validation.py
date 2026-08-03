import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.validate_brand import contrast_ratio, validate_project


VALID_HYBRID_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1160 340">
  <title>Stronger at Home Physiotherapy by Melanie Watsham</title>
  <desc>A supporting hand and progressing person within an open-doorway home, beside the Stronger at Home Physiotherapy wordmark.</desc>
  <path fill="none" stroke="#203E55" d="M10 100 L50 50 L90 100"/>
  <circle fill="#203E55" cx="40" cy="75" r="5"/>
  <rect fill="#C3A26E" x="50" y="80" width="20" height="5"/>
  <text fill="#203E55" x="120" y="80">Stronger at Home</text>
  <text fill="#203E55" x="120" y="110">Physiotherapy</text>
  <text fill="#203E55" x="120" y="130">by Melanie Watsham</text>
</svg>
"""


def write_asset_project(
    root: Path,
    *,
    svg_text: str = VALID_HYBRID_SVG,
    status: str = "proposed",
    reviewed_by: str | None = None,
    reviewed_on: str | None = None,
    sha256: str | None = None,
) -> None:
    asset_path = root / "brand/assets/source/logo-primary-hybrid.svg"
    asset_path.parent.mkdir(parents=True)
    asset_path.write_text(svg_text, encoding="utf-8")
    manifest = {
        "schema_version": "1.0",
        "assets": [
            {
                "id": "logo_primary_hybrid",
                "role": "primary_hybrid_logo",
                "path": "brand/assets/source/logo-primary-hybrid.svg",
                "status": status,
                "sha256": sha256
                or hashlib.sha256(asset_path.read_bytes()).hexdigest(),
                "reviewed_by": reviewed_by,
                "reviewed_on": reviewed_on,
            }
        ],
    }
    manifest_path = root / "brand/assets/manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")


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

    def test_proposed_hybrid_svg_contract(self):
        root = Path(__file__).resolve().parents[1]
        svg_path = root / "brand/assets/source/logo-primary-hybrid.svg"
        svg_text = svg_path.read_text(encoding="utf-8")

        self.assertNotIn("<image", svg_text)
        self.assertIn("Stronger at Home", svg_text)
        self.assertIn("Physiotherapy", svg_text)
        self.assertIn("by Melanie Watsham", svg_text)
        self.assertIn("#203E55", svg_text)
        self.assertIn("#C3A26E", svg_text)

    def test_proposed_hybrid_manifest_contract_and_hash(self):
        root = Path(__file__).resolve().parents[1]
        manifest = json.loads(
            (root / "brand/assets/manifest.json").read_text(encoding="utf-8")
        )
        asset = manifest["assets"][0]

        self.assertEqual(asset["status"], "proposed")
        self.assertIsNone(asset["reviewed_by"])
        self.assertIsNone(asset["reviewed_on"])

        for manifest_asset in manifest["assets"]:
            asset_path = root / manifest_asset["path"]
            self.assertTrue(asset_path.is_file())
            self.assertEqual(
                manifest_asset["sha256"],
                hashlib.sha256(asset_path.read_bytes()).hexdigest(),
            )

    def test_valid_proposed_hybrid_asset_has_no_asset_validation_errors(self):
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
            "  <desc>A supporting hand and progressing person within an open-doorway home, beside the Stronger at Home Physiotherapy wordmark.</desc>\n",
            "",
        )
        with TemporaryDirectory() as directory:
            root = Path(directory)
            write_asset_project(root, svg_text=svg)

            errors = validate_project(root)

        self.assertIn("Hybrid logo is missing an accessible title", errors)
        self.assertIn("Hybrid logo is missing an accessible description", errors)

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
