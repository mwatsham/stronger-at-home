"""Native Apache acceptance tests with disposable credentials and verified local TLS."""
import base64
import http.client
import os
from pathlib import Path
import socket
import ssl
import subprocess
import tempfile
import time
import unittest

from scripts.build_git_release import _configure_htaccess

ROOT = Path(__file__).resolve().parents[1]
HTTPD = Path("/usr/sbin/httpd")
MODULES = Path("/usr/libexec/apache2")


@unittest.skipUnless(HTTPD.exists() and MODULES.exists(), "native macOS Apache unavailable")
class StagingApacheTests(unittest.TestCase):
    def test_authentication_covers_routes_and_never_challenges_plain_http(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            public = root / "public"
            public.mkdir()
            paths = ("/index.html", "/contact/index.php", "/assets/site.css", "/assets/logo.png", "/api/enquiry.php")
            for path in paths:
                target = public / path.lstrip("/")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("protected-marker")
            # This is a synthetic local password, never the hosting credential.
            password_file = root / "passwd"
            subprocess.run(["/usr/sbin/htpasswd", "-ci", str(password_file), "melanie"],
                           input="test-only-password\n", text=True, capture_output=True, check=True)
            subprocess.run(["/usr/sbin/htpasswd", "-i", str(password_file), "other"],
                           input="test-only-password\n", text=True, capture_output=True, check=True)
            config = public / ".htaccess"
            config.write_bytes((ROOT / "site/.htaccess").read_bytes())
            _configure_htaccess(config, "staging", "")
            config.write_text(config.read_text().replace(
                "/home/v0398ees6dry/.htpasswds/public_html/staging.stronger-at-home.co.uk/passwd",
                str(password_file)))
            subprocess.run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes",
                            "-keyout", str(root / "key.pem"), "-out", str(root / "cert.pem"),
                            "-days", "1", "-subj", "/CN=localhost",
                            "-addext", "subjectAltName=DNS:localhost"],
                           capture_output=True, check=True)
            def free_port():
                with socket.socket() as sock:
                    sock.bind(("127.0.0.1", 0))
                    return sock.getsockname()[1]
            http_port, https_port = free_port(), free_port()
            modules = ("mpm_prefork", "authn_core", "authn_file", "authz_core", "authz_user",
                       "auth_basic", "unixd", "dir", "mime", "rewrite", "headers", "env", "ssl", "socache_shmcb")
            server_config = root / "httpd.conf"
            server_config.write_text(
                f'ServerRoot "{root}"\nDefaultRuntimeDir "{root}"\nMutex file:{root} default\nServerName localhost\nPidFile "{root}/httpd.pid"\n'
                f'ErrorLog "{root}/error.log"\nListen 127.0.0.1:{http_port}\nListen 127.0.0.1:{https_port}\n'
                + "".join(f'LoadModule {module}_module "{MODULES}/mod_{module}.so"\n' for module in modules)
                + f'TypesConfig /etc/apache2/mime.types\nDocumentRoot "{public}"\n'
                + f'<Directory "{public}">\nAllowOverride All\nRequire all granted\n</Directory>\n'
                + '<FilesMatch "^\\.ht">\nRequire all denied\n</FilesMatch>\n'
                + f'<VirtualHost 127.0.0.1:{https_port}>\nSSLEngine on\n'
                + f'SSLCertificateFile "{root}/cert.pem"\nSSLCertificateKeyFile "{root}/key.pem"\n</VirtualHost>\n')
            syntax = subprocess.run([str(HTTPD), "-t", "-f", str(server_config)], capture_output=True, text=True)
            self.assertEqual(syntax.returncode, 0, syntax.stderr)
            process = subprocess.Popen([str(HTTPD), "-f", str(server_config), "-DFOREGROUND"],
                                       stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, text=True, start_new_session=True)
            try:
                for _ in range(100):
                    if process.poll() is not None:
                        self.fail(process.communicate()[1] + ((root / "error.log").read_text() if (root / "error.log").exists() else ""))
                    try:
                        with socket.create_connection(("127.0.0.1", https_port), timeout=.1):
                            break
                    except OSError:
                        time.sleep(.05)
                context = ssl.create_default_context(cafile=str(root / "cert.pem"))
                def request(path, secure=True, user=None, password="test-only-password", method="GET"):
                    connection = (http.client.HTTPSConnection("localhost", https_port, context=context)
                                  if secure else http.client.HTTPConnection("localhost", http_port))
                    headers = {"Host": "staging.stronger-at-home.co.uk"}
                    if user:
                        headers["Authorization"] = "Basic " + base64.b64encode(f"{user}:{password}".encode()).decode()
                    try:
                        connection.request(method, path, headers=headers)
                    except OSError as error:
                        raise AssertionError((root / "error.log").read_text() if (root / "error.log").exists() else str(error)) from error
                    response = connection.getresponse()
                    result = response.status, dict(response.getheaders()), response.read()
                    connection.close()
                    return result
                for path in (*paths, "/missing"):
                    for method in ("GET", "HEAD", "POST", "OPTIONS"):
                        with self.subTest(path=path, method=method):
                            status, headers, body = request(path, method=method)
                            self.assertEqual(status, 401)
                            self.assertIn("WWW-Authenticate", headers)
                            self.assertNotIn(b"protected-marker", body)
                            self.assertNotIn(b"/home/", body)
                    status, headers, body = request(path, secure=False)
                    self.assertEqual(status, 403)
                    self.assertNotIn("WWW-Authenticate", headers)
                    self.assertNotIn(b"protected-marker", body)
                for path in paths:
                    status, _, body = request(path, user="melanie")
                    self.assertEqual(status, 200)
                    self.assertEqual(body, b"protected-marker")
                for user, password in (("melanie", "wrong"), ("other", "test-only-password")):
                    self.assertEqual(request("/index.html", user=user, password=password)[0], 401)
                status, _, body = request("/.htaccess", user="melanie")
                self.assertEqual(status, 403)
                self.assertNotIn(b"AuthUserFile", body)
            finally:
                process.terminate()
                process.wait(timeout=5)
                process.stderr.close()
