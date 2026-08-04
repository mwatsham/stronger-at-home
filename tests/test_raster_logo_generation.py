import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from PIL import Image
import PIL

from scripts.generate_raster_logo import (
    MASTER_SIZE,
    SMALL_SIZE,
    SOURCE_SHA256,
    generate,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RasterLogoGenerationTests(unittest.TestCase):
    def test_immutable_source_matches_approved_hash(self):
        source = PROJECT_ROOT / (
            "docs/superpowers/specs/assets/"
            "home-physiotherapy-logo-approved-concept-v2.png"
        )
        self.assertEqual(
            hashlib.sha256(source.read_bytes()).hexdigest(), SOURCE_SHA256
        )

    def test_generate_writes_exact_opaque_dimensions(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            master_path, small_path = generate(root)
            with Image.open(master_path) as master:
                self.assertEqual(master.size, MASTER_SIZE)
                self.assertEqual(master.mode, "RGB")
                self.assertEqual(master.format, "PNG")
            with Image.open(small_path) as small:
                self.assertEqual(small.size, SMALL_SIZE)
                self.assertEqual(small.mode, "RGB")
                self.assertEqual(small.format, "PNG")

    def test_generate_is_byte_deterministic(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            first_paths = generate(root)
            first_hashes = [
                hashlib.sha256(path.read_bytes()).hexdigest()
                for path in first_paths
            ]
            second_paths = generate(root)
            second_hashes = [
                hashlib.sha256(path.read_bytes()).hexdigest()
                for path in second_paths
            ]
        self.assertEqual(first_hashes, second_hashes)

    def test_generate_rejects_a_non_pinned_pillow_version(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            with patch.object(PIL, "__version__", "12.2.0"):
                with self.assertRaisesRegex(
                    RuntimeError,
                    "Raster generation requires Pillow 12.3.0; found 12.2.0",
                ):
                    generate(root)

    def _copy_inputs(self, root: Path) -> None:
        relative_inputs = (
            "docs/superpowers/specs/assets/"
            "home-physiotherapy-logo-approved-concept-v2.png",
            "brand/fonts/source-serif-4.ttf",
            "brand/fonts/atkinson-hyperlegible-next.ttf",
        )
        for relative in relative_inputs:
            source = PROJECT_ROOT / relative
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())
