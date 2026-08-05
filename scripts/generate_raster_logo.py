from __future__ import annotations

import hashlib
from pathlib import Path

try:
    import PIL
    from PIL import Image, ImageDraw, ImageFont
except ModuleNotFoundError as error:
    if error.name != "PIL":
        raise
    raise RuntimeError(
        "Raster generation requires Pillow 12.3.0; install the pinned project "
        "dependencies from requirements.txt."
    ) from error


SOURCE_RELATIVE = Path(
    "docs/superpowers/specs/assets/"
    "home-physiotherapy-logo-approved-concept-v2.png"
)
SOURCE_SHA256 = (
    "41267865711ca55f9225df8370c50bca823f68ca966b8fc216852e65a36d0ef1"
)
SOURCE_SIZE = (1254, 1254)
CROP_BOX = (300, 285, 954, 1023)
MASTER_SIZE = (2048, 640)
SMALL_SIZE = (512, 160)
SYMBOL_FIT = (520, 560)
SYMBOL_POSITION = (48, 40)
BACKGROUND = (249, 244, 242)
DEEP_NAVY = (32, 62, 85)
SOURCE_SERIF = Path("brand/fonts/source-serif-4.ttf")
ATKINSON = Path("brand/fonts/atkinson-hyperlegible-next.ttf")
APPROVED_MASTER_OUTPUT = Path("brand/assets/source/logo-primary-raster-2048.png")
APPROVED_SMALL_OUTPUT = Path("brand/assets/source/logo-primary-raster-512.png")
CANDIDATE_MASTER_OUTPUT = Path("brand/assets/source/logo-primary-raster-v2-2048.png")
CANDIDATE_SMALL_OUTPUT = Path("brand/assets/source/logo-primary-raster-v2-512.png")
MASTER_OUTPUT = APPROVED_MASTER_OUTPUT
SMALL_OUTPUT = APPROVED_SMALL_OUTPUT
APPROVED_WORDMARK_LINES = (
    "Stronger at Home",
    "Physiotherapy",
    "by Melanie Watsham",
)
CANDIDATE_WORDMARK_LINES = (
    "Stronger@Home",
    "Physiotherapy",
    "by Melanie Watsham",
)
REQUIRED_PILLOW_VERSION = "12.3.0"


def _require_pinned_pillow() -> None:
    installed_version = PIL.__version__
    if installed_version != REQUIRED_PILLOW_VERSION:
        raise RuntimeError(
            "Raster generation requires Pillow "
            f"{REQUIRED_PILLOW_VERSION}; found {installed_version}. "
            "Install the pinned project dependencies from requirements.txt."
        )


def _verified_source(root: Path) -> Image.Image:
    path = root / SOURCE_RELATIVE
    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual_hash != SOURCE_SHA256:
        raise ValueError(
            f"Immutable source hash mismatch: expected {SOURCE_SHA256}, "
            f"received {actual_hash}"
        )
    image = Image.open(path)
    image.load()
    if image.size != SOURCE_SIZE or image.mode != "RGB":
        raise ValueError(
            f"Immutable source must be RGB {SOURCE_SIZE[0]} × {SOURCE_SIZE[1]}"
        )
    return image


def _render_master(root: Path, wordmark_lines: tuple[str, str, str]) -> Image.Image:
    _require_pinned_pillow()
    source = _verified_source(root)
    symbol = source.crop(CROP_BOX)
    symbol.thumbnail(SYMBOL_FIT, Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", MASTER_SIZE, BACKGROUND)
    canvas.paste(symbol, SYMBOL_POSITION)
    draw = ImageDraw.Draw(canvas)
    fonts = (
        ImageFont.truetype(root / SOURCE_SERIF, 112),
        ImageFont.truetype(root / SOURCE_SERIF, 82),
        ImageFont.truetype(root / ATKINSON, 44),
    )
    positions = ((640, 130), (640, 270), (640, 390))
    for text, font, position in zip(wordmark_lines, fonts, positions, strict=True):
        draw.text(position, text, font=font, fill=DEEP_NAVY, anchor="lt")
    return canvas


def render_master(root: Path) -> Image.Image:
    return _render_master(root, APPROVED_WORDMARK_LINES)


def render_candidate_master(root: Path) -> Image.Image:
    return _render_master(root, CANDIDATE_WORDMARK_LINES)


def _save_png(image: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    image.save(path, format="PNG", optimize=False, compress_level=9)


def generate(root: Path) -> tuple[Path, Path]:
    master = render_master(root)
    small = master.resize(SMALL_SIZE, Image.Resampling.LANCZOS)
    master_path = root / MASTER_OUTPUT
    small_path = root / SMALL_OUTPUT
    _save_png(master, master_path)
    _save_png(small, small_path)
    return master_path, small_path


def generate_candidate(root: Path) -> tuple[Path, Path]:
    master = render_candidate_master(root)
    small = master.resize(SMALL_SIZE, Image.Resampling.LANCZOS)
    master_path = root / CANDIDATE_MASTER_OUTPUT
    small_path = root / CANDIDATE_SMALL_OUTPUT
    _save_png(master, master_path)
    _save_png(small, small_path)
    return master_path, small_path


def main() -> None:
    master_path, small_path = generate_candidate(Path.cwd())
    print(master_path)
    print(small_path)


if __name__ == "__main__":
    main()
