from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.validate_brand import contrast_ratio, validate_project


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
