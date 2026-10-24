from html.parser import HTMLParser
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory
import unittest

from scripts.validate_site import validate_site

ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = "https://widget.trustpilot.com/bootstrap/v5/tp.widget.bootstrap.min.js"
PROFILE = "https://uk.trustpilot.com/review/stronger-at-home.co.uk"
GOOGLE_REVIEW = "https://g.page/r/CYqDnIzAeBQuEBM/review"


class EmbedParser(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.head = False
        self.loaders = []
        self.widgets = []
        self.links = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "head":
            self.head = True
        if tag == "script" and attrs.get("src") == BOOTSTRAP:
            self.loaders.append((self.head, attrs))
        if tag == "div" and "trustpilot-widget" in attrs.get("class", "").split():
            self.widgets.append(attrs)
        if tag == "a":
            self.links.append(attrs)

    def handle_endtag(self, tag):
        if tag == "head":
            self.head = False


class TrustpilotWidgetTests(unittest.TestCase):
    def test_homepage_offers_the_supplied_google_review_destination_as_a_safe_link(self):
        parser = EmbedParser((ROOT / "site/index.html").read_text())
        links = [link for link in parser.links if link.get("href") == GOOGLE_REVIEW]
        self.assertEqual(len(links), 1)
        self.assertEqual(links[0].get("target"), "_blank")
        self.assertIn("noopener", links[0].get("rel", "").split())
        self.assertIn("noreferrer", links[0].get("rel", "").split())

    def test_homepage_can_load_the_supplied_collector_and_has_a_no_script_link(self):
        parser = EmbedParser((ROOT / "site/index.html").read_text())
        self.assertEqual(len(parser.loaders), 1)
        in_head, loader = parser.loaders[0]
        self.assertTrue(in_head)
        self.assertIn("async", loader)
        self.assertEqual(len(parser.widgets), 1)
        widget = parser.widgets[0]
        self.assertEqual(widget["data-template-id"], "56278e9abfbbba0bdcd568bc")
        self.assertEqual(widget["data-businessunit-id"], "6a9e920821171d34e2c1aa32")
        self.assertEqual(widget["data-token"], "661be9f1-bbf0-460a-90da-2c5052dbae00")
        self.assertEqual(widget["data-style-height"], "52px")
        self.assertEqual(widget["data-style-width"], "100%")
        profile_links = [link for link in parser.links if link.get("href") == PROFILE]
        self.assertEqual(len(profile_links), 1)
        link = profile_links[0]
        self.assertIn("noopener", link["rel"].split())

    def test_release_validator_accepts_only_the_approved_resource_context(self):
        cases = [
            ("script", BOOTSTRAP, True),
            ("script", "https://widget.trustpilot.com/unapproved.js", False),
            ("script", PROFILE, False),
            ("script", "https://invitejs.trustpilot.com/tp.min.js", False),
            ("a", PROFILE, True),
            ("a", GOOGLE_REVIEW, True),
            ("script", GOOGLE_REVIEW, False),
            ("a", "https://g.page/r/unapproved/review", False),
        ]
        for tag, url, approved in cases:
            with self.subTest(tag=tag, url=url), TemporaryDirectory() as directory:
                copy = Path(directory)
                shutil.copytree(ROOT / "site", copy / "site")
                home = copy / "site/index.html"
                markup = f'<script src="{url}"></script>' if tag == "script" else f'<a href="{url}">Review</a>'
                home.write_text(home.read_text().replace("</body>", markup + "</body>"))
                errors = validate_site(copy, "development")
                rejected = any(url in error and "External URL" in error for error in errors)
                self.assertEqual(rejected, not approved, errors)

    def test_csp_allows_widget_script_and_frame_without_relaxing_other_sources(self):
        htaccess = (ROOT / "site/.htaccess").read_text()
        line = next(line for line in htaccess.splitlines() if "Content-Security-Policy" in line)
        policy = line.split('"')[1]
        directives = {parts[0]: parts[1:] for item in policy.split(";") if (parts := item.split())}
        self.assertIn("https://widget.trustpilot.com", directives["script-src"])
        self.assertEqual(directives["frame-src"], ["https://widget.trustpilot.com"])
        self.assertEqual(directives["default-src"], ["'self'"])
        self.assertEqual(directives["form-action"], ["'self'"])
        self.assertNotIn("'unsafe-inline'", policy)
        self.assertNotIn("'unsafe-eval'", policy)
        self.assertNotIn("*", policy)


if __name__ == "__main__":
    unittest.main()
