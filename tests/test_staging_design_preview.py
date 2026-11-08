from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.build_git_release import build_git_release
from scripts.package_site import package_site
from scripts.staging_design_preview import include_staging_preview

ROOT = Path(__file__).resolve().parents[1]
SHA = '0123456789abcdef0123456789abcdef01234567'
STAMP = '2026-11-08T12:00:00Z'


class StagingDesignPreviewTests(unittest.TestCase):
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
            include_staging_preview(ROOT, release / 'public', 'production')
            self.assertFalse((release / 'public/design-preview').exists())
            self.assertFalse(list((release / 'public').rglob('*-preview.webp')))


if __name__ == '__main__':
    unittest.main()
