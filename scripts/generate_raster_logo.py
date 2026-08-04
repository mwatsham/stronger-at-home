from __future__ import annotations

import hashlib
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


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
MASTER_OUTPUT = Path("brand/assets/source/logo-primary-raster-2048.png")
SMALL_OUTPUT = Path("brand/assets/source/logo-primary-raster-512.png")


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


def render_master(root: Path) -> Image.Image:
    source = _verified_source(root)
    symbol = source.crop(CROP_BOX)
    symbol.thumbnail(SYMBOL_FIT, Image.Resampling.LANCZOS)

    canvas = Image.new("RGB", MASTER_SIZE, BACKGROUND)
    canvas.paste(symbol, SYMBOL_POSITION)
    draw = ImageDraw.Draw(canvas)
    source_serif_primary = ImageFont.truetype(root / SOURCE_SERIF, 112)
    source_serif_descriptor = ImageFont.truetype(root / SOURCE_SERIF, 82)
    atkinson_endorsement = ImageFont.truetype(root / ATKINSON, 44)
    draw.text(
        (640, 130),
        "Stronger at Home",
        font=source_serif_primary,
        fill=DEEP_NAVY,
        anchor="lt",
    )
    draw.text(
        (640, 270),
        "Physiotherapy",
        font=source_serif_descriptor,
        fill=DEEP_NAVY,
        anchor="lt",
    )
    draw.text(
        (640, 390),
        "by Melanie Watsham",
        font=atkinson_endorsement,
        fill=DEEP_NAVY,
        anchor="lt",
    )
    return canvas


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


def main() -> None:
    master_path, small_path = generate(Path.cwd())
    print(master_path)
    print(small_path)


if __name__ == "__main__":
    main()
