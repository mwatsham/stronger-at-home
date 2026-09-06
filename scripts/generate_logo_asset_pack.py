from __future__ import annotations

import hashlib
from io import BytesIO
from pathlib import Path

import PIL
from PIL import Image, ImageDraw, ImageFont


REQUIRED_PILLOW_VERSION = "12.3.0"
BACKGROUND = (249, 244, 242)
WARM_CREAM = (247, 242, 232)
PALE_SKY = (232, 241, 246)
DEEP_NAVY = (32, 62, 85)
WARM_SAND = (195, 162, 110)

PRIMARY_SOURCE = Path("brand/assets/source/logo-primary-raster-v2-2048.png")
PRIMARY_SOURCE_SHA256 = (
    "4e8988e571269353aed86697468e0a60b838bc1e121c8e590f974d5124df3683"
)
PRIMARY_SOURCE_SIZE = (2048, 640)
SYMBOL_SOURCE = Path(
    "docs/superpowers/specs/assets/"
    "home-physiotherapy-logo-approved-concept-v2.png"
)
SYMBOL_SOURCE_SHA256 = (
    "41267865711ca55f9225df8370c50bca823f68ca966b8fc216852e65a36d0ef1"
)
SYMBOL_SOURCE_SIZE = (1254, 1254)
SYMBOL_CROP = (300, 285, 954, 1023)

SOURCE_SERIF = Path("brand/fonts/source-serif-4.ttf")
ATKINSON = Path("brand/fonts/atkinson-hyperlegible-next.ttf")
EXPORT_DIRECTORY = Path("brand/assets/exports")
REVIEW_OUTPUT = Path("brand/assets/review/logo-asset-pack-comparison.png")
CANONICAL_ASSET_ROOT = Path(__file__).resolve().parents[1]

PRIMARY_SIZES = {
    2048: (2048, 640),
    1024: (1024, 320),
    512: (512, 160),
    256: (256, 80),
}
SECONDARY_TRANSPARENT_SIZES = (1024, 512, 256, 128)
SECONDARY_CONTAINED_SIZES = (1024, 512, 192, 180, 64, 32, 16)
EMAIL_SIZE = (600, 188)
REVIEW_SIZE = (1800, 2100)
APPROVED_EXPORT_SHA256 = {
    "brand/assets/exports/logo-email-transparent-600.png": "1d1282ff9f5df7eeda3b49976a4d104c77467f145957a93d6a583cff553cf7c6",
    "brand/assets/exports/logo-primary-transparent-1024.png": "857c31f151052fe4ce4f589f7de80c11119c87b7fbe09bb37a20848b6108bc0d",
    "brand/assets/exports/logo-primary-transparent-2048.png": "0328080f1f7ecc01a93108cc686fad88490f404c0d989671271bd7b16a96717c",
    "brand/assets/exports/logo-primary-transparent-256.png": "cdeb1048b9b3f2240568a098bb178e5bced80d1ac12e0a3f749d25af20bf25c7",
    "brand/assets/exports/logo-primary-transparent-512.png": "8159f4a14c38f6b334329c01bf86cb84cbd059d5503e83e3ec15bdf1bc0ab0ff",
    "brand/assets/exports/logo-secondary-contained-1024.png": "35ee071a01c91998fb3c88c5ec15f6047e2dae2e1634a714895ea9ef7264bbe0",
    "brand/assets/exports/logo-secondary-contained-16.png": "58024d77114572f8b7f93efb24d1cf982a19584d62ed68839ceeb438390e0574",
    "brand/assets/exports/logo-secondary-contained-180.png": "ae8b91455206a2169ebba94c5b2e92796093784bfa71c6e76d867f98c388f91e",
    "brand/assets/exports/logo-secondary-contained-192.png": "a9a72f62748b13b2e093583171aa948f22de6bb45c09510be58b3dfd7e7146d9",
    "brand/assets/exports/logo-secondary-contained-32.png": "876a1a8339942d228a9b971779e9581661827ade976c2a4dfdc2eafa97cb35d0",
    "brand/assets/exports/logo-secondary-contained-512.png": "13d4c724c28b02792177a22cac32c7553ec668b8b95300ee71d8aa358320997d",
    "brand/assets/exports/logo-secondary-contained-64.png": "87d944d4741b0e309ec5fec5b6efd233ef43219740e2449fa06ee7d2a51b4eae",
    "brand/assets/exports/logo-secondary-transparent-1024.png": "e1b6e546b866c0b2eb17a997a3e873104d1e863c0074437c12c7ff826e6ce67f",
    "brand/assets/exports/logo-secondary-transparent-128.png": "a2d1109ed2e50f63f9f4a1d52d8acbda855226cff2715c3f2d2c0098ec462928",
    "brand/assets/exports/logo-secondary-transparent-256.png": "62c00ac3fcc4256c2253fa1d9e65ff9799de4806caff7244b8d502b18eee2067",
    "brand/assets/exports/logo-secondary-transparent-512.png": "6b886f09ada6314a55b4a7a6cf034e3267841d41fb97f9b36448a315bbc9c50c",
}


def _require_pinned_pillow() -> None:
    if PIL.__version__ != REQUIRED_PILLOW_VERSION:
        raise RuntimeError(
            "Logo asset generation requires Pillow "
            f"{REQUIRED_PILLOW_VERSION}; found {PIL.__version__}"
        )


def _verified_image(
    root: Path,
    relative_path: Path,
    expected_hash: str,
    expected_size: tuple[int, int],
) -> Image.Image:
    path = root / relative_path
    actual_hash = hashlib.sha256(path.read_bytes()).hexdigest()
    if actual_hash != expected_hash:
        raise ValueError(
            f"Approved source hash mismatch for {relative_path}: "
            f"expected {expected_hash}, received {actual_hash}"
        )
    image = Image.open(path)
    image.load()
    if image.size != expected_size or image.mode != "RGB":
        raise ValueError(
            f"Approved source {relative_path} must be RGB "
            f"{expected_size[0]} × {expected_size[1]}"
        )
    return image


def _remove_background(image: Image.Image) -> Image.Image:
    """Remove the approved matte without redrawing or recolouring the artwork."""
    clear_at = 3
    opaque_at = 36
    pixels = []
    mattes = (BACKGROUND, (255, 255, 255))
    for colour in image.get_flattened_data():
        matte = min(
            mattes,
            key=lambda candidate: sum(
                (channel - matte_channel) ** 2
                for channel, matte_channel in zip(colour, candidate, strict=True)
            ),
        )
        distance = max(
            abs(channel - matte_channel)
            for channel, matte_channel in zip(colour, matte, strict=True)
        )
        if distance <= clear_at:
            opacity = 0
        elif distance >= opaque_at:
            opacity = 255
        else:
            opacity = round((distance - clear_at) * 255 / (opaque_at - clear_at))

        if opacity == 0:
            pixels.append((0, 0, 0, 0))
            continue
        if opacity == 255:
            pixels.append((*colour, 255))
            continue

        fraction = opacity / 255
        foreground = tuple(
            max(0, min(255, round((channel - matte_channel * (1 - fraction)) / fraction)))
            for channel, matte_channel in zip(colour, matte, strict=True)
        )
        pixels.append((*foreground, opacity))

    transparent = Image.new("RGBA", image.size)
    transparent.putdata(pixels)
    return transparent


def _fit_secondary(symbol: Image.Image, size: int) -> Image.Image:
    bbox = symbol.getchannel("A").getbbox()
    if bbox is None:
        raise ValueError("Approved symbol source contains no visible artwork")
    trimmed = symbol.crop(bbox)
    maximum = max(1, round(size * 0.82))
    trimmed.thumbnail((maximum, maximum), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    position = ((size - trimmed.width) // 2, (size - trimmed.height) // 2)
    canvas.alpha_composite(trimmed, position)
    return canvas


def _png_bytes(image: Image.Image, *, print_master: bool = False) -> bytes:
    save_options = {
        "format": "PNG",
        "optimize": False,
        "compress_level": 9,
    }
    if print_master:
        save_options["dpi"] = (300, 300)
    output = BytesIO()
    image.save(output, **save_options)
    return output.getvalue()


def _save_png(
    image: Image.Image,
    path: Path,
    *,
    print_master: bool = False,
    approved_hash: str | None = None,
) -> None:
    payload = _png_bytes(image, print_master=print_master)
    actual_hash = hashlib.sha256(payload).hexdigest()
    if approved_hash is not None and actual_hash != approved_hash:
        raise RuntimeError(
            f"Generated logo bytes do not match approved SHA-256 for {path.name}: "
            f"expected {approved_hash}, received {actual_hash}"
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def _save_approved_export(
    image: Image.Image,
    root: Path,
    relative_path: Path,
    *,
    print_master: bool = False,
) -> Path:
    path = root / relative_path
    canonical_path = CANONICAL_ASSET_ROOT / relative_path
    payload = canonical_path.read_bytes()
    expected_hash = APPROVED_EXPORT_SHA256[relative_path.as_posix()]
    actual_hash = hashlib.sha256(payload).hexdigest()
    if actual_hash != expected_hash:
        raise RuntimeError(
            f"Canonical approved logo hash mismatch for {canonical_path}: "
            f"expected {expected_hash}, received {actual_hash}"
        )

    with Image.open(BytesIO(payload)) as approved:
        approved.load()
        if (
            approved.size != image.size
            or approved.mode != image.mode
            or approved.tobytes() != image.tobytes()
        ):
            raise RuntimeError(
                f"Generated logo pixels do not match approved asset for {path.name}"
            )
        if print_master:
            horizontal, vertical = approved.info.get("dpi", (0, 0))
            if abs(horizontal - 300) > 0.1 or abs(vertical - 300) > 0.1:
                raise RuntimeError(
                    f"Approved print master must record 300 dpi for {path.name}"
                )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)
    return path


def _font(root: Path, relative: Path, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(root / relative, size)


def _draw_card(
    sheet: Image.Image,
    box: tuple[int, int, int, int],
    fill: tuple[int, int, int],
    label: str,
    image: Image.Image,
    root: Path,
) -> None:
    draw = ImageDraw.Draw(sheet)
    draw.rounded_rectangle(box, radius=28, fill=fill, outline=WARM_SAND, width=3)
    draw.text(
        (box[0] + 28, box[1] + 24),
        label,
        fill=DEEP_NAVY if fill != DEEP_NAVY else WARM_CREAM,
        font=_font(root, ATKINSON, 24),
    )
    available_width = box[2] - box[0] - 72
    available_height = box[3] - box[1] - 100
    preview = image.copy()
    preview.thumbnail((available_width, available_height), Image.Resampling.LANCZOS)
    position = (
        box[0] + (box[2] - box[0] - preview.width) // 2,
        box[1] + 72 + (available_height - preview.height) // 2,
    )
    if preview.mode == "RGBA":
        sheet.paste(preview, position, preview)
    else:
        sheet.paste(preview, position)


def _render_review_sheet(root: Path, generated: dict[str, Path]) -> Image.Image:
    sheet = Image.new("RGB", REVIEW_SIZE, WARM_CREAM)
    draw = ImageDraw.Draw(sheet)
    title = _font(root, SOURCE_SERIF, 62)
    heading = _font(root, SOURCE_SERIF, 42)
    body = _font(root, ATKINSON, 27)
    small = _font(root, ATKINSON, 22)

    draw.text((80, 62), "Core logo asset pack", fill=DEEP_NAVY, font=title)
    draw.text(
        (82, 145),
        "APPROVED BY MELANIE WATSHAM — 6 SEPTEMBER 2026",
        fill=DEEP_NAVY,
        font=body,
    )

    draw.text((80, 230), "Primary transparent logo", fill=DEEP_NAVY, font=heading)
    primary = Image.open(generated["primary-1024"])
    _draw_card(sheet, (70, 300, 600, 600), (255, 255, 255), "White", primary, root)
    _draw_card(sheet, (635, 300, 1165, 600), PALE_SKY, "Pale Sky", primary, root)
    opaque = Image.open(root / PRIMARY_SOURCE)
    _draw_card(sheet, (1200, 300, 1730, 600), DEEP_NAVY, "Opaque fallback", opaque, root)

    draw.text((80, 675), "Secondary mark", fill=DEEP_NAVY, font=heading)
    secondary = Image.open(generated["secondary-transparent-512"])
    contained = Image.open(generated["secondary-contained-512"])
    _draw_card(sheet, (70, 745, 600, 1225), (255, 255, 255), "Transparent / white", secondary, root)
    _draw_card(sheet, (635, 745, 1165, 1225), PALE_SKY, "Transparent / Pale Sky", secondary, root)
    _draw_card(sheet, (1200, 745, 1730, 1225), DEEP_NAVY, "Contained / dark", contained, root)

    draw.text((80, 1300), "Small-size behaviour", fill=DEEP_NAVY, font=heading)
    sizes = (192, 180, 64, 32, 16)
    x = 95
    baseline = 1570
    for size in sizes:
        icon = Image.open(generated[f"secondary-contained-{size}"])
        display_size = size if size >= 64 else size * 3
        display = icon.resize((display_size, display_size), Image.Resampling.NEAREST)
        sheet.paste(display, (x, baseline - display_size))
        draw.text((x, baseline + 20), f"{size} px", fill=DEEP_NAVY, font=small)
        x += max(display_size, 150) + 90

    draw.rounded_rectangle((70, 1710, 1730, 2010), radius=28, fill=(255, 255, 255))
    draw.text((105, 1750), "Usage boundary", fill=DEEP_NAVY, font=heading)
    lines = (
        "• Transparent files: light, plain backgrounds only.",
        "• Opaque or contained files: dark, photographic or uncontrolled backgrounds.",
        "• Exact approved primary files remain unchanged.",
        "• PNG only — no SVG, AI redraw or recolouring.",
    )
    y = 1825
    for line in lines:
        draw.text((110, y), line, fill=DEEP_NAVY, font=body)
        y += 45
    return sheet


def generate_asset_pack(root: Path) -> tuple[Path, ...]:
    _require_pinned_pillow()
    primary_source = _verified_image(
        root,
        PRIMARY_SOURCE,
        PRIMARY_SOURCE_SHA256,
        PRIMARY_SOURCE_SIZE,
    )
    symbol_source = _verified_image(
        root,
        SYMBOL_SOURCE,
        SYMBOL_SOURCE_SHA256,
        SYMBOL_SOURCE_SIZE,
    )
    transparent_primary = _remove_background(primary_source)
    transparent_symbol = _remove_background(symbol_source.crop(SYMBOL_CROP))

    paths: list[Path] = []
    generated: dict[str, Path] = {}

    for width, size in PRIMARY_SIZES.items():
        image = transparent_primary.resize(size, Image.Resampling.LANCZOS)
        relative_path = EXPORT_DIRECTORY / f"logo-primary-transparent-{width}.png"
        path = _save_approved_export(
            image, root, relative_path, print_master=width == 2048
        )
        paths.append(path)
        generated[f"primary-{width}"] = path

    for size in SECONDARY_TRANSPARENT_SIZES:
        image = _fit_secondary(transparent_symbol, size)
        relative_path = EXPORT_DIRECTORY / f"logo-secondary-transparent-{size}.png"
        path = _save_approved_export(image, root, relative_path)
        paths.append(path)
        generated[f"secondary-transparent-{size}"] = path

    for size in SECONDARY_CONTAINED_SIZES:
        transparent = _fit_secondary(transparent_symbol, size)
        image = Image.new("RGB", (size, size), BACKGROUND)
        image.paste(transparent, (0, 0), transparent)
        relative_path = EXPORT_DIRECTORY / f"logo-secondary-contained-{size}.png"
        path = _save_approved_export(image, root, relative_path)
        paths.append(path)
        generated[f"secondary-contained-{size}"] = path

    email = transparent_primary.resize(EMAIL_SIZE, Image.Resampling.LANCZOS)
    email_path = _save_approved_export(
        email,
        root,
        EXPORT_DIRECTORY / "logo-email-transparent-600.png",
    )
    paths.append(email_path)
    generated["email-600"] = email_path

    review_path = root / REVIEW_OUTPUT
    _save_png(_render_review_sheet(root, generated), review_path)
    paths.append(review_path)
    return tuple(paths)


def main() -> None:
    for path in generate_asset_pack(Path.cwd()):
        print(path)


if __name__ == "__main__":
    main()
