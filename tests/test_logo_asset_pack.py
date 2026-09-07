import hashlib
import importlib.util
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from PIL import Image
from scripts.validate_brand import APPROVED_EXPORT_RECORDS


PROJECT_ROOT = Path(__file__).resolve().parents[1]

EXPECTED_OUTPUTS = {
    "brand/assets/exports/logo-primary-transparent-2048.png": ((2048, 640), "RGBA"),
    "brand/assets/exports/logo-primary-transparent-1024.png": ((1024, 320), "RGBA"),
    "brand/assets/exports/logo-primary-transparent-512.png": ((512, 160), "RGBA"),
    "brand/assets/exports/logo-primary-transparent-256.png": ((256, 80), "RGBA"),
    "brand/assets/exports/logo-secondary-transparent-1024.png": ((1024, 1024), "RGBA"),
    "brand/assets/exports/logo-secondary-transparent-512.png": ((512, 512), "RGBA"),
    "brand/assets/exports/logo-secondary-transparent-256.png": ((256, 256), "RGBA"),
    "brand/assets/exports/logo-secondary-transparent-128.png": ((128, 128), "RGBA"),
    "brand/assets/exports/logo-secondary-contained-1024.png": ((1024, 1024), "RGB"),
    "brand/assets/exports/logo-secondary-contained-512.png": ((512, 512), "RGB"),
    "brand/assets/exports/logo-secondary-contained-192.png": ((192, 192), "RGB"),
    "brand/assets/exports/logo-secondary-contained-180.png": ((180, 180), "RGB"),
    "brand/assets/exports/logo-secondary-contained-64.png": ((64, 64), "RGB"),
    "brand/assets/exports/logo-secondary-contained-32.png": ((32, 32), "RGB"),
    "brand/assets/exports/logo-secondary-contained-16.png": ((16, 16), "RGB"),
    "brand/assets/exports/logo-email-transparent-600.png": ((600, 188), "RGBA"),
    "brand/assets/review/logo-asset-pack-comparison.png": ((1800, 2100), "RGB"),
}

INPUTS = (
    "brand/assets/source/logo-primary-transparent-v3-2048.png",
    "docs/superpowers/specs/assets/home-physiotherapy-logo-approved-concept-v2.png",
    "brand/fonts/source-serif-4.ttf",
    "brand/fonts/atkinson-hyperlegible-next.ttf",
)


def load_generator():
    module_path = PROJECT_ROOT / "scripts/generate_logo_asset_pack.py"
    if not module_path.is_file():
        raise AssertionError(
            "scripts/generate_logo_asset_pack.py must implement the approved asset pack"
        )
    spec = importlib.util.spec_from_file_location("generate_logo_asset_pack", module_path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class LogoAssetPackTests(unittest.TestCase):
    def test_generator_is_pinned_to_the_independently_approved_export_hashes(self):
        generator = load_generator()

        self.assertEqual(generator.APPROVED_EXPORT_SHA256, APPROVED_EXPORT_RECORDS)

    def test_generator_refuses_to_write_drifted_approved_bytes(self):
        generator = load_generator()
        relative = "brand/assets/exports/logo-primary-transparent-2048.png"
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            original_hash = generator.APPROVED_EXPORT_SHA256[relative]
            generator.APPROVED_EXPORT_SHA256[relative] = "0" * 64
            try:
                with self.assertRaisesRegex(
                    RuntimeError,
                    "Canonical approved logo hash mismatch",
                ):
                    generator.generate_asset_pack(root)
            finally:
                generator.APPROVED_EXPORT_SHA256[relative] = original_hash

            self.assertFalse((root / relative).exists())

    def test_approved_exports_do_not_depend_on_platform_png_encoding(self):
        generator = load_generator()
        relative = Path("brand/assets/exports/logo-primary-transparent-512.png")
        with TemporaryDirectory() as directory:
            root = Path(directory)
            with Image.open(PROJECT_ROOT / relative) as approved:
                image = approved.copy()

            original_png_bytes = generator._png_bytes
            generator._png_bytes = lambda *args, **kwargs: b"platform-dependent"
            try:
                generator._save_approved_export(image, root, relative)
            finally:
                generator._png_bytes = original_png_bytes

            self.assertEqual(
                (root / relative).read_bytes(),
                (PROJECT_ROOT / relative).read_bytes(),
            )

    def test_approved_export_refuses_pixel_mode_or_size_drift_before_writing(self):
        generator = load_generator()
        relative = Path("brand/assets/exports/logo-primary-transparent-512.png")
        with Image.open(PROJECT_ROOT / relative) as approved:
            base = approved.copy()

        pixel_drift = base.copy()
        pixel_drift.putpixel((0, 0), (1, 2, 3, 4))
        variants = {
            "pixel": pixel_drift,
            "mode": base.convert("RGB"),
            "size": base.resize((511, 160)),
        }
        for label, image in variants.items():
            with self.subTest(label=label), TemporaryDirectory() as directory:
                root = Path(directory)
                with self.assertRaisesRegex(
                    RuntimeError,
                    "Generated logo pixels do not match approved asset",
                ):
                    generator._save_approved_export(image, root, relative)
                self.assertFalse((root / relative).exists())

    def test_pack_generates_the_approved_png_matrix(self):
        generator = load_generator()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            paths = generator.generate_asset_pack(root)

            self.assertEqual(
                {path.relative_to(root).as_posix() for path in paths},
                set(EXPECTED_OUTPUTS),
            )
            self.assertFalse((root / "brand/assets/candidates").exists())
            self.assertFalse(list((root / "brand/assets").rglob("*.svg")))
            for relative, expected in EXPECTED_OUTPUTS.items():
                with self.subTest(relative=relative):
                    with Image.open(root / relative) as image:
                        self.assertEqual((image.size, image.mode), expected)
                        self.assertEqual(image.format, "PNG")

    def test_transparent_outputs_remove_the_background_and_retain_ink(self):
        generator = load_generator()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            generator.generate_asset_pack(root)

            transparent_paths = [
                root / relative
                for relative, (_, mode) in EXPECTED_OUTPUTS.items()
                if mode == "RGBA"
            ]
            for path in transparent_paths:
                with self.subTest(path=path.name):
                    with Image.open(path) as image:
                        alpha = image.getchannel("A")
                        minimum, maximum = alpha.getextrema()
                        self.assertEqual(minimum, 0)
                        self.assertEqual(maximum, 255)
                        self.assertIsNotNone(alpha.getbbox())

    def test_primary_export_preserves_the_approved_v3_master_pixels(self):
        generator = load_generator()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            generator.generate_asset_pack(root)
            with Image.open(root / generator.PRIMARY_SOURCE) as source:
                with Image.open(root / "brand/assets/exports/logo-primary-transparent-2048.png") as output:
                    self.assertEqual(source.mode, output.mode)
                    self.assertEqual(source.size, output.size)
                    self.assertEqual(source.tobytes(), output.tobytes())

    def test_v3_wordmark_is_three_quarters_symbol_height_and_centred(self):
        with Image.open(PROJECT_ROOT / "brand/assets/source/logo-primary-transparent-v3-2048.png") as source:
            alpha = source.getchannel("A")
            # The composition separates the two blocks at x=650.
            symbol = alpha.crop((0, 0, 650, 640)).getbbox()
            wordmark = alpha.crop((650, 0, 2048, 640)).getbbox()
            self.assertIsNotNone(symbol)
            self.assertIsNotNone(wordmark)
            self.assertAlmostEqual(
                (wordmark[3] - wordmark[1]) / (symbol[3] - symbol[1]), 0.75, delta=0.01
            )
            self.assertLessEqual(abs(sum(symbol[1::2]) - sum(wordmark[1::2])), 3)
            gap = 650 + wordmark[0] - symbol[2]
            self.assertAlmostEqual(gap / (symbol[3] - symbol[1]), 39 / 469, delta=0.01)

    def test_secondary_marks_are_centred_with_protective_clearspace(self):
        generator = load_generator()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            generator.generate_asset_pack(root)

            for size in (1024, 512, 256, 128):
                path = root / (
                    "brand/assets/exports/"
                    f"logo-secondary-transparent-{size}.png"
                )
                with Image.open(path) as image:
                    bbox = image.getchannel("A").getbbox()
                    self.assertIsNotNone(bbox)
                    left, top, right, bottom = bbox
                    self.assertLessEqual(abs((left + right) - size), 2)
                    self.assertLessEqual(abs((top + bottom) - size), 2)
                    self.assertGreaterEqual(left, round(size * 0.08))
                    self.assertGreaterEqual(top, round(size * 0.08))

    def test_print_master_records_300_dpi_metadata(self):
        generator = load_generator()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            generator.generate_asset_pack(root)

            path = root / "brand/assets/exports/logo-primary-transparent-2048.png"
            with Image.open(path) as image:
                self.assertIn("dpi", image.info)
                horizontal, vertical = image.info["dpi"]
                self.assertAlmostEqual(horizontal, 300, delta=0.1)
                self.assertAlmostEqual(vertical, 300, delta=0.1)

    def test_generation_is_deterministic_and_preserves_approved_inputs(self):
        generator = load_generator()
        with TemporaryDirectory() as directory:
            root = Path(directory)
            self._copy_inputs(root)
            before = {
                relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
                for relative in INPUTS
            }

            first_paths = generator.generate_asset_pack(root)
            first = {
                path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in first_paths
            }
            second_paths = generator.generate_asset_pack(root)
            second = {
                path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in second_paths
            }
            after = {
                relative: hashlib.sha256((root / relative).read_bytes()).hexdigest()
                for relative in INPUTS
            }

            self.assertEqual(second, first)
            self.assertEqual(after, before)

    def test_manifest_traces_every_approved_export_to_its_exact_bytes(self):
        manifest = json.loads(
            (PROJECT_ROOT / "brand/assets/manifest.json").read_text(encoding="utf-8")
        )
        entries = {
            asset["path"]: asset
            for asset in manifest["assets"]
            if asset["path"].startswith("brand/assets/exports/")
        }
        export_paths = {
            relative for relative in EXPECTED_OUTPUTS if "/exports/" in relative
        }

        self.assertEqual(set(entries), export_paths)
        for relative in sorted(export_paths):
            with self.subTest(relative=relative):
                asset = entries[relative]
                self.assertEqual(asset["status"], "approved")
                revised = "/logo-primary-" in relative or "/logo-email-" in relative
                self.assertEqual(asset["reviewed_by"], "Project sponsor" if revised else "Melanie Watsham")
                self.assertEqual(asset["reviewed_on"], "2026-09-07" if revised else "2026-09-06")
                self.assertEqual(
                    asset["sha256"],
                    hashlib.sha256((PROJECT_ROOT / relative).read_bytes()).hexdigest(),
                )

    def _copy_inputs(self, root: Path) -> None:
        for relative in INPUTS:
            source = PROJECT_ROOT / relative
            destination = root / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            destination.write_bytes(source.read_bytes())


if __name__ == "__main__":
    unittest.main()
