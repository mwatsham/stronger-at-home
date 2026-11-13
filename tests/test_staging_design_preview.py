from pathlib import Path
from html.parser import HTMLParser
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from PIL import Image

from scripts.build_git_release import build_git_release
from scripts.package_site import package_site
from scripts.staging_design_preview import include_staging_preview

ROOT = Path(__file__).resolve().parents[1]
SHA = '0123456789abcdef0123456789abcdef01234567'
STAMP = '2026-11-08T12:00:00Z'


class StagingDesignPreviewTests(unittest.TestCase):
    def test_new_treatment_images_resolve_on_staging_and_preview_routes(self):
        class Images(HTMLParser):
            def __init__(self):
                super().__init__()
                self.items = []

            def handle_starttag(self, tag, attrs):
                if tag == 'img':
                    self.items.append(dict(attrs))

        with TemporaryDirectory() as directory:
            release = build_git_release(ROOT, Path(directory) / 'release', 'staging', SHA, STAMP)
            public = release / 'public'
            include_staging_preview(ROOT, public, 'staging')
            for prefix in ('', 'design-preview/'):
                for page, name in (('index.html', 'seated-treatment'), ('how-i-can-help/index.html', 'standing-balance')):
                    html = (public / prefix / page).read_text()
                    images = Images()
                    images.feed(html)
                    selected = [item for item in images.items if name in item.get('src', '')]
                    self.assertEqual(len(selected), 1)
                    photo = selected[0]
                    self.assertTrue(photo.get('alt'))
                    self.assertEqual(photo['loading'], 'lazy')
                    with Image.open(public / photo['src'].lstrip('/')) as image:
                        self.assertEqual(image.size, (int(photo['width']), int(photo['height'])))
                    for source in photo['srcset'].split(','):
                        url, width = source.split()
                        with Image.open(public / url.lstrip('/')) as image:
                            self.assertEqual(image.width, int(width[:-1]))
                home = (public / prefix / 'index.html').read_text()
                self.assertIn('data-feedback-carousel', home)
                self.assertIn('melanie-navy-portrait-preview.webp', home)
                self.assertIn('breathing-support-preview.webp', (public / prefix / 'how-i-can-help/index.html').read_text())

    def test_public_releases_exclude_removed_personal_and_editorial_references(self):
        for environment in ('staging', 'production'):
            with self.subTest(environment=environment), TemporaryDirectory() as directory:
                release = build_git_release(ROOT, Path(directory) / 'release', environment, SHA, STAMP)
                include_staging_preview(ROOT, release / 'public', environment, approved_production=True)
                for page in (release / 'public').rglob('*'):
                    if page.suffix in {'.html', '.php', '.css', '.js', '.json', '.xml', '.txt'}:
                        content = page.read_text().lower()
                        for removed in ('mospey', 'kt17 4lz', 'ai-edited', 'ai-generated', 'complaint'):
                            self.assertNotIn(removed, content, str(page.relative_to(release)))

    def test_informational_fallback_is_not_overwritten_by_approved_photos(self):
        with TemporaryDirectory() as directory:
            release = build_git_release(ROOT, Path(directory) / 'release', 'production', SHA, STAMP, publication_mode='informational')
            before = {p.relative_to(release): p.read_bytes() for p in release.rglob('*') if p.is_file()}
            include_staging_preview(ROOT, release / 'public', 'production', approved_production=True)
            self.assertEqual(before, {p.relative_to(release): p.read_bytes() for p in release.rglob('*') if p.is_file()})

    def test_explicit_production_promotion_matches_accepted_staging_pages(self):
        with TemporaryDirectory() as directory:
            staging = build_git_release(ROOT, Path(directory) / 'staging', 'staging', SHA, STAMP)
            production = build_git_release(ROOT, Path(directory) / 'production', 'production', SHA, STAMP)
            security = (production / 'public/.htaccess').read_bytes()
            contact = (production / 'public/contact/index.php').read_bytes()
            include_staging_preview(ROOT, staging / 'public', 'staging')
            include_staging_preview(ROOT, production / 'public', 'production', approved_production=True)
            for page in ('index.html', 'about/index.html', 'how-i-can-help/index.html'):
                self.assertEqual((staging / 'public' / page).read_bytes(), (production / 'public' / page).read_bytes())
            for asset in (staging / 'public/assets/approved-photos').rglob('*'):
                if asset.is_file():
                    self.assertEqual(asset.read_bytes(), (production / asset.relative_to(staging)).read_bytes())
            self.assertEqual(security, (production / 'public/.htaccess').read_bytes())
            self.assertNotIn(b'AuthType Basic', security)
            self.assertEqual(contact, (production / 'public/contact/index.php').read_bytes())
            self.assertFalse((production / 'public/design-preview').exists())

    def test_main_staging_uses_approved_photos_and_keeps_protection(self):
        with TemporaryDirectory() as directory:
            release = build_git_release(ROOT, Path(directory) / 'release', 'staging', SHA, STAMP)
            public = release / 'public'
            protection = (public / '.htaccess').read_bytes()
            contact = (public / 'contact/index.php').read_bytes()
            include_staging_preview(ROOT, public, 'staging')
            for page in ('index.html', 'how-i-can-help/index.html', 'about/index.html'):
                html = (public / page).read_text()
                self.assertNotIn('href="/design-preview/', html)
                self.assertNotIn('aria-label="Design preview"', html)
                self.assertNotIn('AI-edited', html)
            home = (public / 'index.html').read_text()
            self.assertIn('/assets/approved-photos/images/melanie-navy-portrait-preview.webp', home)
            self.assertIn('treatment-section', home)
            self.assertIn('/assets/approved-photos/css/photo-fades.css', home)
            about = (public / 'about/index.html').read_text()
            self.assertIn('/assets/approved-photos/images/melanie-navy-portrait-preview.webp', about)
            services = (public / 'how-i-can-help/index.html').read_text()
            for name in ('home-exercise', 'mat-exercise', 'breathing-support', 'melanie-navy-portrait'):
                relative = f'images/{name}-preview.webp'
                self.assertEqual((public / 'assets/approved-photos' / relative).read_bytes(),
                                 (ROOT / 'design-previews/seamless-photo/assets' / relative).read_bytes())
            self.assertIn('breathing-support-preview.webp', services)
            self.assertIn('standing-balance-960.webp', services)
            self.assertEqual(protection, (public / '.htaccess').read_bytes())
            self.assertEqual(contact, (public / 'contact/index.php').read_bytes())

    def test_staging_rejects_preview_parent_symlink_without_output(self):
        with TemporaryDirectory() as directory:
            temporary = Path(directory)
            archive = package_site(ROOT, temporary / 'package', 'staging')
            project = temporary / 'project'
            project.mkdir()
            outside = temporary / 'outside'
            (outside / 'seamless-photo').mkdir(parents=True)
            (outside / 'seamless-photo/index.html').write_text('external file')
            (project / 'design-previews').symlink_to(outside, target_is_directory=True)
            output = temporary / 'release'
            with patch('scripts.build_git_release.package_site', return_value=archive):
                build_git_release(project, output, 'staging', SHA, STAMP)
            with self.assertRaisesRegex(ValueError, 'symlink'):
                include_staging_preview(project, output / 'public', 'staging')
            self.assertFalse((output / 'public/design-preview').exists())

    def test_staging_release_serves_preview_and_all_three_photos(self):
        with TemporaryDirectory() as directory:
            release = build_git_release(ROOT, Path(directory) / 'release', 'staging', SHA, STAMP)
            include_staging_preview(ROOT, release / 'public', 'staging')
            preview = release / 'public/design-preview'
            self.assertTrue((preview / 'index.html').is_file(), 'Staging must serve the review page')
            self.assertTrue((preview / 'how-i-can-help/index.html').is_file())
            self.assertIn('/design-preview/assets/images/melanie-navy-portrait-preview.webp', (preview / 'index.html').read_text())
            for name in ('home-exercise', 'mat-exercise', 'breathing-support', 'melanie-navy-portrait'):
                asset = f'assets/images/{name}-preview.webp'
                self.assertEqual((preview / asset).read_bytes(), (ROOT / 'design-previews/seamless-photo' / asset).read_bytes())

    def test_production_release_excludes_preview_and_placeholder_photos(self):
        with TemporaryDirectory() as directory:
            release = build_git_release(ROOT, Path(directory) / 'release', 'production', SHA, STAMP)
            before = {p.relative_to(release): p.read_bytes() for p in release.rglob('*') if p.is_file()}
            include_staging_preview(ROOT, release / 'public', 'production')
            self.assertEqual(before, {p.relative_to(release): p.read_bytes() for p in release.rglob('*') if p.is_file()})
            self.assertFalse((release / 'public/design-preview').exists())
            self.assertFalse(list((release / 'public').rglob('*-preview.webp')))


if __name__ == '__main__':
    unittest.main()
