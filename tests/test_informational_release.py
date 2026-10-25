"""Exercise the generated release, including real local HTTP requests."""
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import sys
import tempfile
import time
import unittest
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from scripts.build_git_release import build_git_release

ROOT = Path(__file__).resolve().parents[1]
SHA = "0123456789abcdef0123456789abcdef01234567"


class InformationalReleaseTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.release = build_git_release(ROOT, cls.root / "release", "staging", SHA,
                                        "2026-10-24T12:00:00Z", publication_mode="informational")

    def test_contact_is_static_and_old_anchor_remains_useful(self):
        contact = (self.release / "public/contact/index.php").read_text()
        for forbidden in ("<?", "<form", "<input", "<select", "<textarea", "csrf_token"):
            self.assertNotIn(forbidden, contact)
        self.assertIn('id="appointment-request"', contact)
        self.assertIn("Online appointment requests are temporarily unavailable.", contact)
        self.assertRegex(contact, r'<div class="section-heading narrow-heading">\s*<p class="notice">')
        self.assertIn("mailto:melanie@stronger-at-home.co.uk", contact)
        self.assertIn("tel:+447843497871", contact)

    def test_public_copy_and_metadata_match_disabled_functionality(self):
        for path in (self.release / "public").rglob("*"):
            if path.suffix in {".html", ".shtml", ".php"} and "api" not in path.parts:
                content = path.read_text()
                self.assertNotIn("Request an appointment", content, str(path))
                self.assertNotIn("or this website enquiry form", content, str(path))
        privacy = (self.release / "public/privacy/index.html").read_text()
        self.assertNotIn("The form asks", privacy)
        self.assertNotIn("A secure session identifier supports", privacy)
        self.assertNotIn("The rate limit stores", privacy)
        self.assertIn("technical server logs", privacy)
        self.assertIn("Trustpilot review widget", privacy)
        metadata = json.loads((self.release / "release.json").read_text())
        self.assertEqual(metadata["publicationMode"], "informational")
        self.assertEqual(metadata["icoStatus"], "pending")
        htaccess = (self.release / "public/.htaccess").read_text()
        self.assertNotIn("SetEnv STRONGER_HOME_CONFIG", htaccess)
        self.assertNotIn("SetEnv STRONGER_HOME_AUTOLOAD", htaccess)
        self.assertIn('X-Robots-Tag "noindex, nofollow"', htaccess)

    def test_real_http_rejects_submissions_without_sessions_or_bootstrap(self):
        sessions = self.root / "sessions"
        sessions.mkdir(exist_ok=True)
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            port = sock.getsockname()[1]
        environment = os.environ.copy()
        environment.pop("STRONGER_HOME_CONFIG", None)
        environment.pop("STRONGER_HOME_AUTOLOAD", None)
        process = subprocess.Popen(["php", "-d", f"session.save_path={sessions}",
                                    "-S", f"127.0.0.1:{port}", "-t", str(self.release / "public")],
                                   env=environment, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            url = f"http://127.0.0.1:{port}"
            for attempt in range(100):
                try:
                    with urlopen(url + "/contact/", timeout=1) as response:
                        self.assertEqual(response.status, 200)
                        self.assertIsNone(response.headers.get("Set-Cookie"))
                        self.assertNotIn(b"<form", response.read())
                    break
                except URLError:
                    time.sleep(.02)
            else:
                self.fail("PHP test server did not start")
            for method in ("GET", "POST", "PUT", "OPTIONS"):
                with self.subTest(method=method):
                    request = Request(url + "/api/enquiry.php", method=method,
                                      data=b"name=DO_NOT_ECHO_THIS" if method != "GET" else None)
                    with self.assertRaises(HTTPError) as caught:
                        urlopen(request, timeout=3)
                    with caught.exception as response:
                        self.assertEqual(response.code, 503)
                        self.assertEqual(response.headers.get("Cache-Control"), "no-store")
                        self.assertIsNone(response.headers.get("Set-Cookie"))
                        self.assertNotIn(b"DO_NOT_ECHO_THIS", response.read())
            self.assertEqual(list(sessions.iterdir()), [])
        finally:
            process.terminate()
            process.wait(timeout=5)

    def test_informational_deploy_needs_no_enquiry_config_and_restores_on_failure(self):
        for fail_swap in (False, True):
            with self.subTest(fail_swap=fail_swap), tempfile.TemporaryDirectory() as directory:
                account = Path(directory).resolve()
                repo = account / "repositories/stronger-at-home-staging"
                shutil.copytree(self.release, repo)
                deploy = repo / "deploy.sh"
                deploy.write_text(deploy.read_text().replace("/home/v0398ees6dry", str(account)))
                public = account / "public_html/staging.stronger-at-home.co.uk"
                public.mkdir(parents=True)
                (public / "old.txt").write_text("previous")
                env = {**os.environ, "HOME": str(account)}
                if fail_swap:
                    fakebin = account / "bin"
                    fakebin.mkdir()
                    fake = fakebin / "mv"
                    fake.write_text('#!/bin/bash\nif [[ "$1" == "--" && "$2" == *".next-"* ]]; then exit 70; fi\nexec /bin/mv "$@"\n')
                    fake.chmod(0o755)
                    env["PATH"] = str(fakebin) + os.pathsep + env["PATH"]
                result = subprocess.run(["bash", str(deploy)], cwd=repo, env=env, capture_output=True)
                self.assertEqual(result.returncode == 0, not fail_swap, result.stderr)
                self.assertEqual((public / "old.txt").exists(), fail_swap)
                if not fail_swap:
                    self.assertNotIn("<form", (public / "contact/index.php").read_text())

    def test_unknown_mode_fails_before_creating_output(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "release"
            with self.assertRaises(ValueError):
                build_git_release(ROOT, output, "staging", SHA, "2026-10-24T12:00:00Z",
                                  publication_mode="typo")
            self.assertFalse(output.exists())


class PublicationModeTests(unittest.TestCase):
    def run_cli(self, mode_path, output):
        return subprocess.run([sys.executable, str(ROOT / "scripts/build_git_release.py"),
            "--environment", "production", "--source-sha", SHA,
            "--build-timestamp", "2026-10-24T12:00:00Z", "--output-directory", str(output),
            "--publication-mode-file", str(mode_path)], capture_output=True, text=True)

    def test_informational_mode_still_builds_disabled_production(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "release"
            mode = Path(directory) / "mode.json"
            mode.write_text('{"publicationMode":"informational","icoStatus":"pending"}')
            result = self.run_cli(mode, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads((output / "release.json").read_text())["publicationMode"], "informational")
            self.assertNotIn("X-Robots-Tag", (output / "public/.htaccess").read_text())

    def test_tracked_mode_builds_enquiries_with_pending_exception(self):
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "release"
            result = self.run_cli(ROOT / "config/publication-mode.json", output)
            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "release.json").read_text())
            self.assertEqual(metadata["publicationMode"], "enquiries")
            self.assertEqual(metadata["icoStatus"], "pending")
            self.assertEqual(metadata["approvalException"], "owner-pending-registration-2026-10-24")
            self.assertIn("<form", (output / "public/contact/index.php").read_text())

    def test_invalid_and_missing_mode_fail_without_artifact(self):
        for value in (None, "{", '{}', '[]', '{"publicationMode":"enquiries","icoStatus":"pending"}',
                      '{"publicationMode":"informational","icoStatus":"pending","publicationMode":"enquiries","icoStatus":"completed"}',
                      '{"publicationMode":"informational","icoStatus":"pending","extra":true}'):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                mode = Path(directory) / "mode.json"
                if value is not None:
                    mode.write_text(value)
                output = Path(directory) / "release"
                result = self.run_cli(mode, output)
                self.assertEqual(result.returncode, 1, result.stderr)
                self.assertFalse(output.exists())

    def test_pending_exception_restores_enquiries_with_truthful_metadata_and_config_guard(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory).resolve()
            mode = root / "mode.json"
            mode.write_text(json.dumps({
                "publicationMode": "enquiries", "icoStatus": "pending",
                "approvalException": "owner-pending-registration-2026-10-24",
            }))
            output = root / "release"
            result = self.run_cli(mode, output)
            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads((output / "release.json").read_text())
            self.assertEqual(metadata["publicationMode"], "enquiries")
            self.assertEqual(metadata["icoStatus"], "pending")
            self.assertEqual(metadata["approvalException"], "owner-pending-registration-2026-10-24")
            contact = (output / "public/contact/index.php").read_text()
            self.assertIn('<form class="appointment-form"', contact)
            self.assertIn('action="/api/enquiry.php"', contact)
            self.assertIn("csrf_token", contact)
            self.assertIn("Please do not include detailed or urgent medical information.", contact)
            self.assertIn("The form asks", (output / "public/privacy/index.html").read_text())
            self.assertNotIn("Online appointment requests are temporarily unavailable.",
                             (output / "public/api/enquiry.php").read_text())
            self.assertIn("SetEnv STRONGER_HOME_CONFIG", (output / "public/.htaccess").read_text())
            self.assertNotIn("X-Robots-Tag", (output / "public/.htaccess").read_text())
            # Execute the actual deploy script in a temporary account with no private config.
            repo = root / "repositories/stronger-at-home-production"
            repo.parent.mkdir()
            shutil.move(output, repo)
            deploy = repo / "deploy.sh"
            deploy.write_text(deploy.read_text().replace("/home/v0398ees6dry", str(root)))
            public = root / "public_html/stronger-at-home.co.uk"
            public.mkdir(parents=True)
            (public / "old.txt").write_text("previous")
            deployed = subprocess.run(["bash", str(deploy)], cwd=repo,
                                     env={**os.environ, "HOME": str(root)}, capture_output=True, text=True)
            self.assertNotEqual(deployed.returncode, 0)
            self.assertIn("Missing external environment configuration.", deployed.stderr)
            self.assertEqual((public / "old.txt").read_text(), "previous")

    def test_pending_exception_rejects_unknown_contradictory_and_duplicate_approval(self):
        for value in (
            '{"publicationMode":"enquiries","icoStatus":"pending","approvalException":"other"}',
            '{"publicationMode":"enquiries","icoStatus":"completed","approvalException":"owner-pending-registration-2026-10-24"}',
            '{"publicationMode":"informational","icoStatus":"pending","approvalException":"owner-pending-registration-2026-10-24"}',
            '{"publicationMode":"enquiries","icoStatus":"pending","approvalException":"other","approvalException":"owner-pending-registration-2026-10-24"}',
            '{"publicationMode":"enquiries","icoStatus":"pending","approvalException":"owner-pending-registration-2026-10-24","extra":true}',
        ):
            with self.subTest(value=value), tempfile.TemporaryDirectory() as directory:
                mode = Path(directory) / "mode.json"
                mode.write_text(value)
                output = Path(directory) / "release"
                result = self.run_cli(mode, output)
                self.assertEqual(result.returncode, 1)
                self.assertFalse(output.exists())

    def test_workflows_select_tracked_mode(self):
        import shlex
        for environment in ("production", "staging"):
            workflow = (ROOT / f".github/workflows/release-{environment}.yml").read_text()
            command = next(line.strip().removeprefix("run: ") for line in workflow.splitlines()
                           if "run: python scripts/build_git_release.py" in line)
            tokens = shlex.split(command)
            self.assertIn("--publication-mode-file", tokens)
            self.assertEqual(tokens[tokens.index("--publication-mode-file") + 1], "config/publication-mode.json")


if __name__ == "__main__":
    unittest.main()
