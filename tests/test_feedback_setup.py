from pathlib import Path
import json
import shutil
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

@unittest.skipUnless(shutil.which('php'),'PHP required')
class FeedbackSetupTests(unittest.TestCase):
    def test_setup_private_files_and_rotation_preserves_quotes(self):
        with tempfile.TemporaryDirectory() as tmp:
            target=Path(tmp).resolve()/'feedback'
            cmd=['php',str(ROOT/'scripts/setup_feedback.php'),'--directory='+str(target),'--environment=local','--origin=http://127.0.0.1:58640','--password-stdin']
            first=subprocess.run(cmd,input=b'Local-test-only-password-123\n',capture_output=True)
            self.assertEqual(first.returncode,0,first.stderr.decode())
            quotes=target/'quotes.json'
            original=quotes.read_bytes()
            self.assertEqual(json.loads(original),{'revision':0,'records':[]})
            for name in ['feedback.php','quotes.json']:
                self.assertEqual((target/name).stat().st_mode&0o777,0o600)
            self.assertEqual(target.stat().st_mode&0o777,0o700)
            self.assertNotIn(b'Local-test-only-password-123',(target/'feedback.php').read_bytes())
            self.assertNotEqual(subprocess.run(cmd,input=b'Local-test-only-password-456\n',capture_output=True).returncode,0)
            self.assertEqual(subprocess.run(cmd+['--rotate'],input=b'Local-test-only-password-456\n',capture_output=True).returncode,0)
            self.assertEqual(quotes.read_bytes(),original)

    def test_rejects_weak_password_and_wrong_live_origin(self):
        with tempfile.TemporaryDirectory() as tmp:
            cmd=['php',str(ROOT/'scripts/setup_feedback.php'),'--directory='+str(Path(tmp).resolve()/'feedback'),'--environment=production','--origin=http://example.com','--password-stdin']
            self.assertNotEqual(subprocess.run(cmd,input=b'weak\n',capture_output=True).returncode,0)
