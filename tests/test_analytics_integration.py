"""Offline integration checks: no analytics endpoint or mail transport contacted."""
from html.parser import HTMLParser
from pathlib import Path
import subprocess
import tempfile
import unittest
from scripts.build_git_release import build_git_release
from scripts.staging_design_preview import include_staging_preview

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
            if tag != 'a' and ('goatcounter.com' in value or 'gc.zgo.at' in value):
                self.remote_analytics.append(value)
        if 'data-form-status' in attrs:
            self.flash = attrs.get('data-flash-kind')


class AnalyticsIntegrationTests(unittest.TestCase):
    def test_final_photo_pages_keep_versioned_analytics_but_preview_does_not(self):
        for env in ('staging', 'production'):
            with self.subTest(environment=env), tempfile.TemporaryDirectory() as temp:
                release = build_git_release(ROOT, Path(temp)/'release', env, 'a'*40, '2026-11-26T21:00:00Z')
                include_staging_preview(ROOT, release/'public', env, approved_production=True)
                for page in PAGES:
                    parser = AnalyticsParser((release/'public'/page).read_text())
                    adapters = [s for s in parser.scripts if s.get('src','').startswith('/assets/js/analytics.js?')]
                    self.assertEqual(len(adapters),1 if env == 'production' else 0,page)
                    if adapters:
                        self.assertNotIn('prepared-',adapters[0]['src'])
                if env == 'staging':
                    parser = AnalyticsParser((release/'public/design-preview/index.html').read_text())
                    self.assertFalse(any('analytics.js' in s.get('src','') for s in parser.scripts))

    def test_csp_permits_only_required_analytics_endpoints(self):
        policy = (ROOT/'site/.htaccess').read_text()
        self.assertIn("script-src 'self' https://widget.trustpilot.com https://gc.zgo.at/count.js;", policy)
        self.assertIn("connect-src 'self' https://stronger-at-home.goatcounter.com/count;", policy)
        self.assertIn("img-src 'self' https://stronger-at-home.goatcounter.com/count;", policy)
        self.assertNotIn("'unsafe-inline'",policy)

    def test_staging_has_no_analytics_asset_permissions_or_controls_in_either_mode(self):
        for mode in ('enquiries', 'informational'):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as temp:
                release = build_git_release(ROOT, Path(temp)/'release', 'staging', 'a'*40,
                                            '2026-11-26T21:00:00Z', publication_mode=mode)
                public = release/'public'
                include_staging_preview(ROOT, public, 'staging')
                self.assertFalse((public/'assets/js/analytics.js').exists())
                policy = (public/'.htaccess').read_text()
                self.assertNotIn('goatcounter.com', policy)
                self.assertNotIn('gc.zgo.at', policy)
                self.assertIn('AuthType Basic', policy)
                for page in PAGES:
                    self.assertNotIn('/assets/js/analytics.js', (public/page).read_text())
                privacy = (public/'privacy/index.html').read_text()
                self.assertNotIn('data-analytics-off', privacy)
                self.assertIn('Analytics are off on staging', privacy)

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
