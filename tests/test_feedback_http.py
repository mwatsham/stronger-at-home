import http.cookiejar
import json
import os
from pathlib import Path
import re
import shutil
import socket
import subprocess
import tempfile
import time
import unittest
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which('php'), 'PHP required for HTTP integration')
class FeedbackHTTPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.private = Path(self.tmp.name).resolve()
        self.private.chmod(0o700)
        (self.private/'sessions').mkdir(mode=0o700)
        (self.private/'quotes.json').write_text('{"revision":0,"records":[]}')
        (self.private/'quotes.json').chmod(0o600)
        with socket.socket() as sock:
            sock.bind(('127.0.0.1',0))
            port=sock.getsockname()[1]
        self.origin=f'http://127.0.0.1:{port}'
        self.password='Local-test-only-password-123'
        hashed=subprocess.check_output(['php','-r','echo password_hash(trim(stream_get_contents(STDIN)),PASSWORD_DEFAULT);'],input=self.password.encode()).decode()
        config={'environment':'local','origin':self.origin,'username':'melanie','password_hash':hashed,'directory':str(self.private)}
        self.config=self.private/'feedback.php'
        self.config.write_text('<?php return json_decode('+repr(json.dumps(config))+',true);')
        self.config.chmod(0o600)
        env=dict(os.environ,STRONGER_HOME_FEEDBACK_CONFIG=str(self.config))
        self.log=open(self.private/'server.log','wb')
        self.server=subprocess.Popen(['php','-S',f'127.0.0.1:{port}','-t',str(ROOT/'site')],env=env,stdout=self.log,stderr=self.log)
        self.addCleanup(self.close)
        self.cookies=http.cookiejar.CookieJar()
        self.client=urllib.request.build_opener(urllib.request.HTTPCookieProcessor(self.cookies))
        for _ in range(100):
            try:
                self.get('/feedback/feed.php')
                break
            except urllib.error.URLError:
                time.sleep(.05)

    def close(self):
        self.server.terminate()
        self.server.wait(timeout=5)
        self.log.close()
        self.tmp.cleanup()

    def request(self,path,data=None,client=None,headers=None):
        request=urllib.request.Request(self.origin+path,data=urllib.parse.urlencode(data).encode() if data is not None else None,headers=headers or {})
        try: response=(client or self.client).open(request,timeout=5)
        except urllib.error.HTTPError as error: response=error
        return response.status,response.read().decode(),response.headers

    def get(self,path): return self.request(path)

    def token(self,html):
        match=re.search(r'name="csrf" value="([a-f0-9]+)"',html)
        self.assertIsNotNone(match,html[:300])
        return match[1]

    def login(self):
        status,body,_=self.get('/feedback/admin/')
        self.assertEqual(status,200)
        return self.request('/feedback/admin/',{'action':'login','csrf':self.token(body),'username':'melanie','password':self.password})

    def post(self,**data):
        _,body,_=self.get('/feedback/admin/')
        return self.request('/feedback/admin/',{'csrf':self.token(body),**data})

    def state(self): return json.loads((self.private/'quotes.json').read_text())

    def test_login_csrf_and_private_access(self):
        status,_,_=self.request('/feedback/admin/',{'action':'save','csrf':'bad'})
        self.assertEqual(status,403)
        status,body,headers=self.login()
        self.assertEqual(status,200)
        self.assertIn('Manage feedback',body)
        self.assertIn('no-store',headers['Cache-Control'])
        self.assertTrue(all(c.has_nonstandard_attr('HttpOnly') for c in self.cookies))
        _,body,_=self.post(action='logout')
        self.assertIn('Sign in',body)
        self.assertNotIn('Manage feedback',body)

    def test_browser_form_policy_preserves_same_origin_login(self):
        _, body, headers = self.get('/feedback/admin/')
        # no-referrer makes browser navigation POSTs send Origin: null.
        # Same-origin keeps the local form origin without leaking referrers off-site.
        self.assertEqual(headers['Referrer-Policy'], 'same-origin')
        status, body, _ = self.request('/feedback/admin/', {
            'action':'login', 'csrf':self.token(body), 'username':'melanie',
            'password':self.password}, headers={'Origin':self.origin})
        self.assertEqual(status, 200)
        self.assertIn('Manage feedback', body)

    def test_null_origin_still_rejected_with_valid_token(self):
        _, body, _ = self.get('/feedback/admin/')
        status, _, _ = self.request('/feedback/admin/', {
            'action':'login', 'csrf':self.token(body), 'username':'melanie',
            'password':self.password}, headers={'Origin':'null'})
        self.assertEqual(status, 403)

    def test_rejected_saves_preserve_unsaved_wording(self):
        self.login()
        for revision, order, expected in [(0, -1, 422), (99, 0, 409)]:
            status, body, _ = self.post(action='save', revision=revision, id='',
                text='Unsaved <wording>', attribution='Agreed attribution', order=order)
            self.assertEqual(status, expected)
            self.assertIn('Unsaved &lt;wording&gt;</textarea>', body)
            self.assertIn('value="Agreed attribution"', body)
            self.assertIn(f'name="revision" value="{revision}"', body)
            self.assertEqual(self.state()['records'], [])

    def test_draft_publish_edit_unpublish_delete_and_conflict(self):
        self.login()
        status,_,_=self.post(action='save',revision=0,text='<script>unsafe</script> Helpful',attribution='Patient',order=2)
        self.assertEqual(status,200)
        record=self.state()['records'][0]; rid=record['id']
        self.assertEqual(json.loads(self.get('/feedback/feed.php')[1]),{'quotes':[]})
        status,body,_=self.get('/feedback/admin/?edit='+rid)
        self.assertIn('&lt;script&gt;',body)
        self.assertNotIn('<script>unsafe</script>',body)
        status,_,_=self.post(action='publish',id=rid,revision=1)
        self.assertEqual(status,422)
        self.post(action='publish',id=rid,revision=1,permission='yes')
        feed=json.loads(self.get('/feedback/feed.php')[1])['quotes'][0]
        self.assertEqual(set(feed),{'text','attribution','order'})
        status,_,_=self.post(action='save',id=rid,revision=1,text='Stale',attribution='Patient',order=1)
        self.assertEqual(status,409)
        self.post(action='save',id=rid,revision=2,text='Updated quote',attribution='Family',order=1)
        self.assertEqual(self.state()['records'][0]['status'],'draft')
        self.assertEqual(json.loads(self.get('/feedback/feed.php')[1])['quotes'],[])
        self.post(action='publish',id=rid,revision=3,permission='yes')
        self.post(action='unpublish',id=rid,revision=4)
        self.assertEqual(self.state()['records'][0]['status'],'draft')
        self.assertEqual(self.post(action='delete',id=rid,revision=5)[0],422)
        self.post(action='delete',id=rid,revision=5,confirm='yes')
        self.assertEqual(self.state()['records'],[])

    def test_invalid_input_and_foreign_origin(self):
        self.login()
        for text in ['', 'x'*601]:
            self.assertEqual(self.post(action='save',revision=0,text=text,attribution='Patient',order=1)[0],422)
        _,body,_=self.get('/feedback/admin/')
        self.assertEqual(self.request('/feedback/admin/',{'action':'save','csrf':self.token(body)},headers={'Origin':'https://evil.example'})[0],403)
        self.assertEqual(self.state()['revision'],0)

    def test_login_throttling(self):
        for _ in range(5):
            self.assertEqual(self.post(action='login',username='melanie',password='bad')[0],401)
        self.assertEqual(self.post(action='login',username='melanie',password=self.password)[0],401)

    def test_feed_fail_closed_and_get_only(self):
        self.assertEqual(self.request('/feedback/feed.php',{})[0],405)
        (self.private/'quotes.json').write_text('corrupt')
        status,body,_=self.get('/feedback/feed.php')
        self.assertEqual(status,503)
        self.assertEqual(json.loads(body),{'quotes':[]})

if __name__ == '__main__':
    unittest.main()
