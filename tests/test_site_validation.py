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
    def test_homepage_uses_approved_patient_first_content_order(self):
        html = (ROOT / "site/index.html").read_text(encoding="utf-8")
        ids = [
            "introduction",
            "how-i-can-help",
            "benefits-at-home",
            "meet-melanie",
            "appointments",
            "area-and-fees",
            "request-an-appointment",
        ]

        section_ids = []
        for tag in html.split("<section ")[1:]:
            attributes = tag.split(">", 1)[0]
            if 'id="' in attributes:
                section_ids.append(attributes.split('id="', 1)[1].split('"', 1)[0])

        self.assertEqual(section_ids, ids)
        self.assertIn("Physiotherapy to help you feel stronger at home", html)
        self.assertIn("20+ years of NHS experience", html)

    def test_homepage_intro_uses_appointment_request_as_primary_action(self):
        html = (ROOT / "site/index.html").read_text(encoding="utf-8")
        introduction = html.split('<section id="introduction"', 1)[1].split(
            '<section id="how-i-can-help"', 1
        )[0]
        primary_action = '<a class="button" href="/contact/#appointment-request">Request an appointment</a>'
        secondary_action = '<a class="text-link" href="tel:+447843497871">Call Melanie</a>'

        self.assertIn(primary_action, introduction)
        self.assertIn(secondary_action, introduction)
        self.assertLess(introduction.index(primary_action), introduction.index(secondary_action))

    def test_homepage_claim_boundary_preserves_approved_facts_without_invented_claims(self):
        html = (ROOT / "site/index.html").read_text(encoding="utf-8")
        approved_facts = [
            "After surgery, a hospital admission or a fall",
            "falls prevention",
            "Appointments are arranged flexibly, subject to availability.",
            "Fees are quoted individually because travel requirements vary by location.",
            "A fixed price will be confirmed and agreed before the appointment is booked.",
        ]
        prohibited_claims = [
            "HCPC",
            "CSP",
            "AGILE",
            "ATOCP",
            "guaranteed",
            "testimonial",
            "review",
            "referral suitability",
            "referral exclusion",
            "emergency",
            "personal plan",
        ]

        for fact in approved_facts:
            self.assertIn(fact, html)
        for claim in prohibited_claims:
            self.assertNotIn(claim.lower(), html.lower(), claim)

    def test_development_portrait_is_a_production_blocker(self):
        html = (ROOT / "site/index.html").read_text(encoding="utf-8")

        self.assertIn('data-production-blocker="portrait"', html)
        self.assertIn("Professional portrait to be supplied", html)

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

    def test_information_pages_present_approved_service_and_appointment_facts(self):
        about = (ROOT / "site/about/index.html").read_text(encoding="utf-8")
        help_page = (ROOT / "site/how-i-can-help/index.html").read_text(encoding="utf-8")
        appointments = (ROOT / "site/appointments-and-fees/index.html").read_text(
            encoding="utf-8"
        )

        self.assertIn("20+ years of NHS experience", about)
        for phrase in (
            "Recovery after surgery",
            "Following a hospital admission",
            "A decline in mobility or physical function",
            "Rehabilitation following a fall",
            "Falls prevention",
            "Mobility and balance",
        ):
            self.assertIn(phrase, help_page)
        for phrase in (
            "60 minutes",
            "45 minutes",
            "approximately 10 miles of Epsom",
            "subject to availability",
            "postcode or address",
            "A fixed price will be confirmed and agreed before the appointment is booked.",
        ):
            self.assertIn(phrase, appointments)

    def test_information_pages_use_clear_page_titles_as_their_top_level_headings(self):
        expected_headings = {
            "site/about/index.html": "About Melanie",
            "site/how-i-can-help/index.html": "How I can help",
            "site/appointments-and-fees/index.html": "Appointments and fees",
        }

        for relative_path, heading in expected_headings.items():
            html = (ROOT / relative_path).read_text(encoding="utf-8")
            self.assertIn(f"<h1>{heading}</h1>", html)

    def test_public_pages_omit_unapproved_claims_and_payment_method_details(self):
        combined = "\n".join(
            (ROOT / path).read_text(encoding="utf-8") for path in PUBLIC_PAGES
        ).lower()

        for text in (
            "hcpc",
            "csp",
            "agile",
            "atocp",
            "guaranteed",
            "walk-in clinic",
            "cash",
            "bank transfer",
            "payment timing",
            "bank details",
        ):
            self.assertNotIn(text, combined)
