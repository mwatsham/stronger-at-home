"""Package approved imagery; production promotion requires an explicit opt-in."""

import argparse
import json
from pathlib import Path
import re
import shutil


def include_staging_preview(project_root: Path, public_root: Path, environment: str, *, approved_production: bool = False) -> None:
    if environment not in {"staging", "production"}:
        raise ValueError("environment must be staging or production")
    if environment == "production" and not approved_production:
        return
    project_root = Path(project_root).resolve()
    public_root = Path(public_root)
    if public_root.is_symlink() or not public_root.is_dir():
        raise ValueError("preview requires a regular public release directory")
    # Never restore enquiry CTAs over the disabled-enquiries fallback.
    metadata = json.loads((public_root.parent / "release.json").read_text())
    if metadata.get("publicationMode") == "informational":
        return
    htaccess = public_root / ".htaccess"
    if htaccess.is_symlink() or not htaccess.is_file():
        raise ValueError("preview requires existing staging protection")
    if environment == "staging" and "AuthType Basic" not in htaccess.read_text():
        raise ValueError("preview requires existing staging protection")
    if environment == "production" and "AuthType Basic" in htaccess.read_text():
        raise ValueError("production must not inherit staging authentication")
    preview = project_root / "design-previews/seamless-photo"
    if preview.parent.is_symlink() or preview.is_symlink():
        raise ValueError("staging design preview must not be a symlink")
    if not preview.is_dir():
        raise ValueError("staging design preview source is missing")
    for item in preview.rglob("*"):
        if item.is_symlink() or (not item.is_dir() and (
            not item.is_file() or item.suffix not in {".html", ".css", ".webp"}
        )):
            raise ValueError("staging design preview contains an unsupported file")
    if environment == "staging":
        shutil.copytree(preview, public_root / "design-preview")
    # Main pages share the exact owner-approved staging composition.
    shutil.copytree(preview / "assets", public_root / "assets/approved-photos")
    disclosure = '<p>Photographs include AI-edited uniform colours.</p>'
    for page in ("index.html", "how-i-can-help/index.html"):
        html = (preview / page).read_text()
        html, count = re.subn(
            r'<aside class="design-preview" aria-label="Design preview">.*?</aside>\s*',
            '', html, count=1, flags=re.DOTALL,
        )
        if count != 1:
            raise ValueError("approved layout must contain one preview banner")
        html = html.replace('/design-preview/assets/', '/assets/approved-photos/')
        html = html.replace('href="/design-preview/', 'href="/')
        html = html.replace('</footer>', f'  {disclosure}\n  </footer>')
        (public_root / page).write_text(html)
    about = public_root / "about/index.html"
    html = about.read_text()
    original = '<img src="/assets/images/melanie-watsham-portrait.jpg" alt="Melanie Watsham, physiotherapist" width="1020" height="1190">'
    replacement = '<img src="/assets/approved-photos/images/melanie-navy-portrait-preview.webp" alt="Melanie Watsham, physiotherapist" width="1161" height="1355">'
    if html.count(original) != 1:
        raise ValueError("About page must contain the expected portrait")
    html = html.replace(original, replacement)
    html = html.replace('</footer>', f'  {disclosure}\n  </footer>')
    about.write_text(html)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--public-directory", type=Path, required=True)
    parser.add_argument("--environment", choices=("staging", "production"), required=True)
    parser.add_argument("--approved-production", action="store_true", help="Apply the owner-approved imagery to production without preview routes")
    args = parser.parse_args()
    include_staging_preview(args.root, args.public_directory, args.environment, approved_production=args.approved_production)


if __name__ == "__main__":
    main()
