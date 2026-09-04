import hashlib
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from PIL import Image
import PIL

from scripts.generate_raster_logo import (
    APPROVED_MASTER_OUTPUT,
    APPROVED_SMALL_OUTPUT,
    CANDIDATE_MASTER_OUTPUT,
    CANDIDATE_MASTER_SHA256,
    CANDIDATE_SMALL_OUTPUT,
    CANDIDATE_SMALL_SHA256,
    CANDIDATE_WORDMARK_LINES,
    MASTER_SIZE,
    SMALL_SIZE,
    SOURCE_SHA256,
    generate,
    generate_candidate,
)


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class RasterLogoGenerationTests(unittest.TestCase):
    def test_candidate_uses_approved_display_wording(self):
        self.assertEqual(
            CANDIDATE_WORDMARK_LINES,
            ("Stronger@Home", "Physiotherapy", "by Melanie Watsham"),
        )

    def test_generate_candidate_writes_versioned_opaque_pngs(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            master_path, small_path = generate_candidate(root)
            self.assertEqual(master_path, root / CANDIDATE_MASTER_OUTPUT)
            self.assertEqual(small_path, root / CANDIDATE_SMALL_OUTPUT)
            with Image.open(master_path) as master:
                self.assertEqual(
                    (master.size, master.mode, master.format),
                    (MASTER_SIZE, "RGB", "PNG"),
                )
            with Image.open(small_path) as small:
                self.assertEqual(
                    (small.size, small.mode, small.format),
                    (SMALL_SIZE, "RGB", "PNG"),
                )

    def test_generate_candidate_does_not_modify_approved_outputs(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            approved_paths = (
                root / APPROVED_MASTER_OUTPUT,
                root / APPROVED_SMALL_OUTPUT,
            )
            approved_paths[0].parent.mkdir(parents=True, exist_ok=True)
            approved_paths[0].write_bytes(b"approved master evidence")
            approved_paths[1].write_bytes(b"approved small evidence")
            before = tuple(
                hashlib.sha256(path.read_bytes()).hexdigest()
                for path in approved_paths
            )
            generate_candidate(root)
            after = tuple(
                hashlib.sha256(path.read_bytes()).hexdigest()
                for path in approved_paths
            )
            self.assertEqual(after, before)

    def test_generate_candidate_is_byte_deterministic(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            first = tuple(
                hashlib.sha256(path.read_bytes()).hexdigest()
                for path in generate_candidate(root)
            )
            second = tuple(
                hashlib.sha256(path.read_bytes()).hexdigest()
                for path in generate_candidate(root)
            )
            self.assertEqual(second, first)

    def test_checked_in_candidate_files_match_exact_approved_hashes(self):
        expected_hashes = (
            "4e8988e571269353aed86697468e0a60b838bc1e121c8e590f974d5124df3683",
            "d557a0e8fd05efc86fcca2b3f63d807ad33f29527062697705a8e05616c6db39",
        )
        paths = (
            PROJECT_ROOT / CANDIDATE_MASTER_OUTPUT,
            PROJECT_ROOT / CANDIDATE_SMALL_OUTPUT,
        )
        actual_hashes = tuple(
            hashlib.sha256(path.read_bytes()).hexdigest() for path in paths
        )
        self.assertEqual(
            (CANDIDATE_MASTER_SHA256, CANDIDATE_SMALL_SHA256), expected_hashes
        )
        self.assertEqual(actual_hashes, expected_hashes)

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
