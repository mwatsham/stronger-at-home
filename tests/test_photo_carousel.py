from pathlib import Path
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class PhotoCarouselTests(unittest.TestCase):
    def test_browser_behaviour(self):
        result = subprocess.run(['node', '--test', 'tests/js/photo-carousel.test.js'],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
