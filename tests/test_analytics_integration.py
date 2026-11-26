"""Offline integration checks: no analytics endpoint or mail transport contacted."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
PAGES = ['index.html', 'about/index.html', 'how-i-can-help/index.html',
         'appointments-and-fees/index.html', 'contact/index.php',
         'privacy/index.html', 'accessibility/index.html']


class AnalyticsParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.scripts = []
        self.remote_analytics = []
        self.flash = None
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'script':
            self.scripts.append(attrs)
        for key in ('src', 'href'):
            value = attrs.get(key, '')
            if 'goatcounter.com' in value or 'gc.zgo.at' in value:
                self.remote_analytics.append(value)
        if 'data-form-status' in attrs:
            self.flash = attrs.get('data-flash-kind')


class AnalyticsIntegrationTests(unittest.TestCase):
    def test_analytics_browser_contract_runs_in_the_ci_quality_gate(self):
        result = subprocess.run(['node', '--test', 'tests/js/analytics.test.js'], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_public_pages_load_only_local_deferred_adapter_once(self):
        for name in PAGES:
            with self.subTest(page=name):
                parser = AnalyticsParser((ROOT / 'site' / name).read_text())
                adapters = [s for s in parser.scripts if s.get('src', '').split('?')[0] == '/assets/js/analytics.js']
                self.assertEqual(len(adapters), 1)
                self.assertIn('defer', adapters[0])
                self.assertEqual(parser.remote_analytics, [])

    def test_private_and_preview_pages_have_no_adapter(self):
        for folder in ['site/feedback', 'site/api', 'design-previews']:
            for file in (ROOT / folder).rglob('*'):
                if file.suffix not in ['.html', '.php']:
                    continue
                parser = AnalyticsParser(file.read_text())
                self.assertFalse(any('/assets/js/analytics.js' in s.get('src', '') for s in parser.scripts), str(file))
                self.assertEqual(parser.remote_analytics, [])

    def test_success_flash_is_consumed_and_sent_query_cannot_forge_it(self):
        with tempfile.TemporaryDirectory() as sessions:
            def php(code):
                result = subprocess.run(['php', '-d', 'session.save_path='+sessions, '-r', code],
                                        cwd=ROOT, capture_output=True, text=True, check=True)
                self.assertEqual(result.stderr, '')
                return result.stdout
            php("session_id('analyticstest'); session_start(); $_SESSION['form_flash']=['kind'=>'success']; session_write_close();")
            render = "session_id('analyticstest'); $_GET['sent']='1'; include 'site/contact/index.php';"
            self.assertEqual(AnalyticsParser(php(render)).flash, 'success')
            self.assertEqual(AnalyticsParser(php(render)).flash, '')

    def test_enquiry_controller_acceptance_and_honeypot_regressions(self):
        result = subprocess.run(['php', 'tests/php/EnquiryControllerTest.php'], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
