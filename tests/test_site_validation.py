from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
PUBLIC_PAGES = {
    "site/index.html": "/",
    "site/about/index.html": "/about/",
    "site/how-i-can-help/index.html": "/how-i-can-help/",
    "site/appointments-and-fees/index.html": "/appointments-and-fees/",
    "site/contact/index.php": "/contact/",
}


class LandmarkParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags, self.links, self.h1_count = [], [], 0

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.tags.append(tag)
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag == "h1":
            self.h1_count += 1


class SiteValidationTests(unittest.TestCase):
    def test_mobile_menu_is_a_javascript_enhancement_with_an_accurate_disclosure_control(self):
        stylesheet = (ROOT / "site/assets/css/site.css").read_text(encoding="utf-8")

        self.assertRegex(
            stylesheet,
            r"\.menu-button \{\n  display: none;",
        )
        self.assertRegex(
            stylesheet,
            r"\.js \.menu-button \{\n    display: block;",
        )
        self.assertRegex(
            stylesheet,
            r"\.js #primary-navigation \{ display: none;",
        )
        self.assertRegex(
            stylesheet,
            r'\.js #primary-navigation\[data-open="true"\] \{ display: flex; \}',
        )

    def test_focus_indicator_uses_the_high_contrast_two_colour_treatment(self):
        stylesheet = (ROOT / "site/assets/css/site.css").read_text(encoding="utf-8")

        self.assertIn(
            "outline: 3px solid var(--brand-colour-text-inverse);",
            stylesheet,
        )
        self.assertIn(
            "box-shadow: 0 0 0 6px var(--brand-colour-background-strong);",
            stylesheet,
        )
        self.assertNotIn(
            "outline: 3px solid var(--brand-colour-accent-progress);",
            stylesheet,
        )

    def test_every_primary_page_has_common_landmarks_and_one_h1(self):
        for relative_path in PUBLIC_PAGES:
            parser = LandmarkParser()
            parser.feed((ROOT / relative_path).read_text(encoding="utf-8"))
            self.assertTrue({"header", "nav", "main", "footer"}.issubset(parser.tags))
            self.assertEqual(parser.h1_count, 1, relative_path)

    def test_every_page_links_all_primary_routes_and_appointment_action(self):
        expected = set(PUBLIC_PAGES.values()) | {"/contact/#appointment-request"}
        for relative_path in PUBLIC_PAGES:
            parser = LandmarkParser()
            parser.feed((ROOT / relative_path).read_text(encoding="utf-8"))
            self.assertTrue(expected.issubset(set(parser.links)), relative_path)
