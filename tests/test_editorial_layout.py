from html.parser import HTMLParser
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


class AppointmentTargetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.target_depth = None
        self.target_tag = None
        self.heading_found = False
        self.form_found = False

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get("id") == "appointment-request":
            self.target_depth = self.depth
            self.target_tag = tag
        if self.target_depth is not None:
            if tag == "h2" and attributes.get("id") == "appointment-request-heading":
                self.heading_found = True
            if tag == "form" and attributes.get("action") == "/api/enquiry.php":
                self.form_found = attributes.get("method") == "post"
        if tag not in {"input", "meta", "link", "img", "br"}:
            self.depth += 1

    def handle_endtag(self, tag):
        self.depth -= 1
        if self.depth == self.target_depth:
            self.target_depth = None


class EditorialLayoutTests(unittest.TestCase):
    def test_appointment_fragment_includes_heading_and_form_context(self):
        parser = AppointmentTargetParser()
        parser.feed((ROOT / "site/contact/index.php").read_text())
        self.assertEqual(parser.target_tag, "section")
        self.assertTrue(parser.heading_found, "Appointment link must include its heading")
        self.assertTrue(parser.form_found, "Appointment link must include the actual POST form")


if __name__ == "__main__":
    unittest.main()
