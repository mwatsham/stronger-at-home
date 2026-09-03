from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts.sync_site_brand_assets import sync_site_brand_assets


ROOT = Path(__file__).resolve().parents[1]


class SiteAssetSyncTests(unittest.TestCase):
    def test_sync_copies_approved_logo_bytes_and_generated_tokens(self):
        with TemporaryDirectory() as directory:
            target = Path(directory)
            sync_site_brand_assets(ROOT, target)

            self.assertEqual(
                (target / "assets/images/stronger-at-home-logo.png").read_bytes(),
                (ROOT / "brand/assets/source/logo-primary-raster-v2-512.png").read_bytes(),
            )
            self.assertEqual(
                (target / "assets/css/brand-tokens.css").read_bytes(),
                (ROOT / "brand/generated/tokens.css").read_bytes(),
            )
            for filename in ("source-serif-4.ttf", "atkinson-hyperlegible-next.ttf"):
                self.assertEqual(
                    (target / "assets/fonts" / filename).read_bytes(),
                    (ROOT / "brand/fonts" / filename).read_bytes(),
                )
