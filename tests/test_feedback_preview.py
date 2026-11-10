from pathlib import Path
import importlib.util
import json
import subprocess
import tempfile
import unittest
from zipfile import ZipFile
from scripts.package_site import package_site
from scripts.build_git_release import build_git_release

ROOT=Path(__file__).resolve().parents[1]

class FeedbackPreviewTests(unittest.TestCase):
    def test_release_points_to_environment_private_feedback_config(self):
        with tempfile.TemporaryDirectory() as tmp:
            for environment in ('staging','production'):
                release=build_git_release(ROOT,Path(tmp)/environment,environment,'1'*40,'2026-11-10T12:00:00Z')
                rules=(release/'public/.htaccess').read_text()
                self.assertIn('SetEnv STRONGER_HOME_FEEDBACK_CONFIG "/home/v0398ees6dry/private/stronger-at-home/'+environment+'/feedback/feedback.php"',rules)

    def test_packaged_code_excludes_runtime_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            archive=package_site(ROOT,Path(tmp)/'package','staging')
            with ZipFile(archive) as z:
                names=z.namelist()
                self.assertIn('public/feedback/admin/index.php',names)
                self.assertIn('public/feedback/feed.php',names)
                self.assertFalse(any(n.endswith(('feedback.php','quotes.json','login-attempts.json')) for n in names))

    def test_rebuilding_preview_preserves_private_quotes_and_separates_environments(self):
        source=ROOT/'scripts/preview_feedback.py'
        self.assertTrue(source.is_file(),'Local preview runner missing')
        from scripts import preview_feedback as module
        with tempfile.TemporaryDirectory() as tmp:
            workspace=Path(tmp).resolve()
            public, config=module.prepare_preview(ROOT,workspace,58640,'Local-test-only-password-123')
            store=workspace/'private/quotes.json'
            content=store.read_bytes()
            public2, config2=module.prepare_preview(ROOT,workspace,58640,'Local-test-only-password-123')
            self.assertEqual(content,store.read_bytes())
            self.assertEqual(public,public2)
            self.assertEqual(config,config2)
            self.assertNotIn(config,public.rglob('*'))
            self.assertIn('Local preview', (public/'index.html').read_text())
            self.assertIn('melanie-navy-portrait-preview.webp',(public/'index.html').read_text())
            self.assertIn('data-feedback-carousel',(public/'index.html').read_text())
            self.assertEqual(store.stat().st_mode&0o777,0o600)
            other=workspace/'other'; other.mkdir()
            module.prepare_preview(ROOT,other,58641,'Local-test-only-password-123')
            self.assertNotEqual(json.loads(store.read_text())['records'][0]['id'],json.loads((other/'private/quotes.json').read_text())['records'][0]['id'])
