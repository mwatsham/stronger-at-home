from pathlib import Path
import shutil


def sync_site_brand_assets(project_root: Path, site_root: Path | None = None) -> None:
    destination = site_root or project_root / "site"
    pairs = {
        project_root / "brand/generated/tokens.css": destination / "assets/css/brand-tokens.css",
        project_root / "brand/assets/source/logo-primary-raster-v2-512.png": destination / "assets/images/stronger-at-home-logo.png",
        project_root / "brand/fonts/source-serif-4.ttf": destination / "assets/fonts/source-serif-4.ttf",
        project_root / "brand/fonts/atkinson-hyperlegible-next.ttf": destination / "assets/fonts/atkinson-hyperlegible-next.ttf",
    }
    for source, target in pairs.items():
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


if __name__ == "__main__":
    sync_site_brand_assets(Path(__file__).resolve().parents[1])
